#état d'avancement :Obstacle Detection AI

## 🎯 Objectif
Développer un prototype de **lunettes intelligentes** capables de détecter les obstacles lors de la marche,
grâce à une caméra embarquée et un traitement IA déporté sur PC.

## 🧩 Architecture actuelle
- **Caméra** : module caméra du Raspberry Pi Zero 2 W.
- **Transmission** : flux vidéo H.264 envoyé via UDP (`udpsink`) au PC.
- **Traitement IA** : sur PC, en Python avec PyTorch / OpenCV.
- **Affichage** : annotation en direct (`Obstacle` / `Pas obstacle`).
- **Communication retour** (prévu) : envoi d’alerte UDP vers le Pi pour retour haptique ou sonore.

---

## ⚙️ Étapes déjà réalisées

### 🧠 1. Prototype de classification binaire 1
- Modèle utilisé : **MobileNetV3-Small (pré-entraîné ImageNet)**.
- Adapté à **2 classes** : `Obstacle` / `Pas obstacle`.
- Inférence directe sur les frames du flux UDP (FFmpeg ou GStreamer).
- Pipeline vidéo :
  ```bash
  Raspberry → UDP → PC → MobileNetV3 → Affichage + Détection

tester:
//editer la connection plus avec wpa.coonf mais avec sudo nmtui

Sur le Raspberry Pi — Émission du flux vidéo

Lance la commande suivante :
rpicam-vid -t 0 \
  --width 640 --height 480 --framerate 30 \
  --codec h264 --inline --listen \
  -o udp://<IP_PC>:5000
  
Sur le PC — Réception et traitement IA

Crée un fichier obstacle_simple.py
lancer obstacle_simple.py

résultat:
<img width="1451" height="1091" alt="Capture d'écran 2025-10-28 163614" src="https://github.com/user-attachments/assets/a9e77bf0-5f01-4b2a-97fd-ebc2c7a40e20" />
<img width="1368" height="1113" alt="Capture d'écran 2025-10-28 163652" src="https://github.com/user-attachments/assets/4393ffc7-d95a-4c0a-b961-0075d14f52a6" />

SUITE 

🚀 2. Détection d’obstacles par localisation (YOLOv8 + SafeWalkBD)
🔍 Objectif de cette étape

Améliorer la précision et la pertinence de la détection en remplaçant la simple classification binaire (Obstacle / Pas obstacle) par une détection d’objets.
L’objectif est d’identifier les obstacles visibles et de déterminer s’ils se trouvent réellement sur la trajectoire de marche (zone centrale de l’image).

🧠 Modèle utilisé

Modèle : YOLOv8 (Ultralytics)

Dataset : SafeWalkBD (hébergé sur Roboflow Universe
)

Poids : best.pt (version YOLOv8, téléchargée automatiquement depuis Roboflow)

Langage : Python 3.10+

Librairies principales :

ultralytics → pour le modèle YOLOv8

opencv-python → pour le flux vidéo et l’affichage

roboflow → pour le téléchargement automatique du modèle

⚙️ Fonctionnement actuel

Le PC reçoit en temps réel le flux vidéo du Raspberry Pi (H.264 / UDP) et applique le modèle YOLOv8.
Chaque objet détecté est analysé pour vérifier s’il se trouve dans une zone centrale basse de l’image — correspondant à la direction de marche de l’utilisateur.

Si un objet est détecté dans cette zone :
➡️ OBSTACLE
Sinon :
➡️ LIBRE


code dans obstacle_yolov8_centre.py

entrainement avec ce datasets https://universe.roboflow.com/tfg-7qtpm/accesibility-street/dataset/11/images

J’ai effectué de nombreuses recherches de datasets en ligne et entraîné plusieurs modèles.
Cependant, les résultats, bien que fonctionnels, manquaient souvent de précision.
J’ai constaté que le problème venait principalement des labels : les annotations des images n’étaient pas toujours adaptées à mon cas d’usage.

À partir de ce constat, j’ai eu l’idée de développer un outil de relabellisation d’images.
Cet outil permet d’afficher une image et son ancien label, puis de sélectionner un nouveau label parmi une liste de catégories adaptées à mon projet.
Une fois la sélection faite, le programme met automatiquement à jour le fichier de labels associé à l’image.

L’objectif est d’affiner les annotations pour constituer un dataset beaucoup plus pertinent, afin d’entraîner un modèle mieux adapté à la détection d’obstacles et d’éléments utiles à la navigation pour les personnes aveugles.

<img width="2118" height="1123" alt="image" src="https://github.com/user-attachments/assets/991b5cfc-d4d7-43e1-ad94-0b0000a7fb1a" />


changement de datasets 
├── person/

├── vehicle/

├── stairs/

├── crosswalk/

├── sidewalk/

├── pothole/

├── ramp/

├── obstacle/

├── garbage/

└── tree/
names:
  - person      # 0
  - vehicle     # 1
  - stairs      # 2
  - crosswalk   # 3
  - sidewalk    # 4
  - pothole     # 5
  - ramp        # 6
  - obstacle    # 7
  - garbage     # 8
  - tree        # 9

Type de classe	                                                                                        	   Quantité

Fréquente (ex : person, vehicle, sidewalk)	souvent visibles	2000–4000 images

Moyenne (ex : stairs, crosswalk, obstacle)	parfois visibles	1000–2000 images

Rare / Spécifique (ex : pothole, ramp, garbage)	peu présentes	700–1500 images
Retour sur les résultats

Le modèle est capable de détecter les obstacles, mais il peut encore confondre certaines classes.
De plus, la latence dépend fortement de l’état de la connexion : dans certaines zones, une connexion faible empêche l’envoi rapide des données, ce qui dégrade les performances en temps réel.

Solutions envisagées

La logique du système va être revue. Le modèle sera découpé en deux étapes :

Modèle 1 : détection simple des obstacles et des humains

Modèle 2 : classification fine du type d’obstacle (escaliers, passages piétons, etc.)

Cette approche permet de réduire fortement la puissance de calcul nécessaire, car seule une partie des images sera analysée en détail.

Le Modèle 1 sera volontairement léger et simplifié : tout objet situé sur la trajectoire sera considéré comme un obstacle.
La détection des humains est plus complexe car ils sont mobiles. Pour cela, un tracking (SORT ou ByteTrack) sera utilisé, combiné à un filtre de Kalman afin d’estimer leur trajectoire et déterminer s’ils peuvent entraver le déplacement de l’utilisateur.

La logique globale du système sera la suivante :

Camera frame
   ↓
Modèle 1 (détection obstacle + humain)
   ↓
Tracker (SORT / ByteTrack)
   ↓
Distance (LiDAR)
   ↓
Logique de décision (alerte / pas d’alerte)



dans C:\Users\bekhtaoui\tools
test avec: python video_tunerv2.py

suite : entraînez en YOLOv8m maintenant pour avoir le meilleur modèle de référence, puis au moment du déploiement vous faites :
YOLOv8m (PyTorch) 
    → distillation vers YOLOv8n 
        → export TFLite INT8 
            → compilation Edge TPU

1 ajout d'images dans E:\IA\final_dataset_save\final_dataset 
avec merge_one.py pour deplacer depuis les dataset jusqu'au final avec les bons labels 
verification avec count_all.py
