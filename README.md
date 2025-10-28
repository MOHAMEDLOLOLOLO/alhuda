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


