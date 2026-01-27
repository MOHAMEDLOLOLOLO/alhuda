# YOLO + ByteTrack + MAP  
## Détection, suivi d’objets et analyse de zone de danger

Ce projet est une application Python avec interface graphique (**Tkinter**) destinée à l’analyse de vidéos en temps réel ou différé.

L’application utilise :
- un modèle de détection d’objets **YOLO (Ultralytics)**,
- un algorithme de suivi multi-objets **ByteTrack**,

afin de détecter, suivre et analyser le comportement d’objets (humains, obstacles) dans une scène vidéo.

Une **zone de danger** est définie dans l’image. Lorsqu’un objet entre dans cette zone, son mouvement est analysé (approche ou éloignement) afin de déterminer s’il représente un risque.

Deux fenêtres sont affichées :
- **VIDEO** : la vidéo originale avec boîtes englobantes, identifiants et alertes,
- **MAP** : une représentation 2D simplifiée (type radar) montrant les positions, trajectoires et directions de déplacement des objets suivis.

## Vue d’ensemble du fonctionnement

Le fonctionnement global de l’application repose sur un pipeline de traitement en plusieurs étapes :
Vidéo
↓
YOLO (détection d’objets)
↓
ByteTrack (suivi multi-objets)
↓
Logique d’analyse du mouvement
↓
Affichage VIDEO + MAP


Chaque étape du pipeline joue un rôle spécifique :

- **YOLO** est responsable de la détection des objets dans chaque image de la vidéo.
- **ByteTrack** assure le suivi des objets détectés en leur attribuant des identifiants persistants dans le temps.
- **La logique d’analyse du mouvement**, implémentée dans ce projet, exploite le suivi pour interpréter le comportement des objets (déplacement, direction, évolution dans le temps).
- **L’affichage** permet de visualiser à la fois la scène vidéo et une représentation simplifiée des déplacements.

Cette architecture modulaire facilite la compréhension du système et la séparation claire des responsabilités entre détection, suivi et analyse.

## Architecture du code

Le projet est implémenté sous la forme d’un script Python unique, organisé en plusieurs sections logiques clairement séparées.

L’architecture du code repose sur les blocs suivants :

1. **Configuration et paramètres globaux**
2. **Structures d’état et synchronisation**
3. **Fonctions utilitaires (helpers)**
4. **Interface graphique (Tkinter)**
5. **Boucle principale de traitement vidéo**

Chaque bloc a une responsabilité précise et communique avec les autres via des variables et structures partagées.

------comment s'agence le code------

### 1. Configuration et paramètres globaux

Cette section regroupe tous les paramètres configurables du projet:
- le chemin du modèle YOLO,
- la configuration du tracker ByteTrack,
- les dimensions de la MAP,
- les seuils de stabilisation et de détection du danger.

Centraliser ces paramètres permet d’ajuster facilement le comportement global du système sans modifier la logique principale.

---

### 2. Structures d’état et synchronisation

Le script utilise plusieurs variables globales pour gérer l’état de l’application :

- événements de contrôle (`pause`, `stop`),
- requêtes de saut temporel dans la vidéo,
- activation ou non du tracking,
- historiques associés aux objets suivis.

Ces états permettent la communication entre :
- l’interface graphique,
- et la boucle principale de traitement vidéo.

L’utilisation de mécanismes de synchronisation garantit un fonctionnement stable malgré l’exécution en parallèle (thread).

---

### 3. Fonctions utilitaires

Les fonctions utilitaires regroupent toute la logique générique réutilisable, notamment :
- la définition de la zone de danger,
- la projection des positions vers la MAP,
- le lissage des trajectoires,
- l’estimation de la vitesse,
- l’analyse de l’approche ou de l’éloignement.

Ces fonctions sont indépendantes de l’interface et du modèle de détection.

---

### 4. Interface graphique (Tkinter)

L’interface graphique permet à l’utilisateur de :
- sélectionner une vidéo,
- lancer, mettre en pause ou arrêter le traitement,
- naviguer dans la vidéo,
- activer ou désactiver le suivi par ByteTrack,
- modifier les paramètres d’inférence.

Les actions utilisateur modifient l’état global de l’application, lu ensuite par la boucle principale.

---

### 5. Boucle principale de traitement vidéo

La boucle principale est responsable de :
- la lecture des frames vidéo,
- l’appel au modèle YOLO (avec ou sans tracking),
- la mise à jour des historiques d’objets,
- le calcul de la logique de danger,
- l’affichage des résultats.

Cette boucle est exécutée dans un thread séparé afin de préserver la réactivité de l’interface graphique.

### Modèle de détection

- **`MODEL_PATH`**  
  Chemin vers le modèle YOLO entraîné (`best.pt`).  
  Ce modèle est utilisé pour détecter les objets présents dans chaque image de la vidéo.

---

### Suivi des objets (tracking)

- **`TRACKER_CFG`**  
  Fichier de configuration du tracker ByteTrack (`bytetrack.yaml`).  
  Il définit les seuils et règles internes utilisés pour le suivi multi-objets.

- **`tracking_enabled`**  
  Active ou désactive dynamiquement l’utilisation du tracking.

---


### Paramètres de la MAP

- **`MAP_W`, `MAP_H`**  
  Dimensions de la carte 2D utilisée pour représenter les déplacements des objets.

- **`TRAIL_LEN`**  
  Nombre maximum de positions passées conservées pour afficher la trajectoire d’un objet.

- **`PREDICT_SEC`**  
  Durée (en secondes) utilisée pour prédire la position future d’un objet.

---

### Stabilisation et estimation du mouvement

- **`EMA_ALPHA`**  
  Facteur de lissage exponentiel appliqué aux centres des boîtes englobantes pour réduire le bruit.

- **`VEL_WINDOW`**  
  Nombre de points utilisés pour calculer une vitesse moyenne stable.

- **`MAX_VEL_PX_PER_SEC`**  
  Vitesse maximale autorisée afin d’éviter des prédictions aberrantes dues au bruit.

---

### Paramètres de la logique de danger

- **`APPROACH_WINDOW`**  
  Taille de la fenêtre temporelle utilisée pour analyser l’évolution du mouvement.

- **`AREA_GROWTH_RATIO`**  
  Seuil d’augmentation de l’aire d’une boîte englobante indiquant une approche.

- **`MIN_DY`**  
  Déplacement vertical minimum du centre d’un objet indiquant une approche vers la caméra.


## Interface graphique (Tkinter)

L’application dispose d’une interface graphique simple, développée avec **Tkinter**, permettant à l’utilisateur de contrôler l’analyse vidéo sans modifier le code.

---

### Sélection et contrôle de la vidéo

L’interface permet de :

- sélectionner un fichier vidéo à analyser,
- démarrer le traitement,
- mettre en pause ou reprendre l’analyse,
- arrêter complètement l’exécution.

Ces actions agissent directement sur l’état global de l’application, qui est ensuite pris en compte par la boucle principale de traitement.

---

### Navigation temporelle

Des boutons permettent de naviguer dans la vidéo :

- saut arrière (ex. −5 secondes),
- saut avant (ex. +5 secondes).

Ces actions modifient dynamiquement la position courante dans le flux vidéo sans redémarrer l’analyse.

---

### Activation du suivi (ByteTrack)

Un bouton dédié permet d’activer ou de désactiver le suivi multi-objets :

- **ByteTrack activé** : les objets sont suivis dans le temps avec des identifiants persistants.
- **ByteTrack désactivé** : les objets sont uniquement détectés image par image.

Cela permet de comparer facilement le comportement du système avec ou sans tracking.

---

### Paramètres d’inférence

L’interface offre la possibilité d’ajuster :
- la taille d’entrée du modèle (`imgsz`),
- le seuil de confiance (`conf`),
- l’épaisseur des boîtes englobantes,
- le périphérique de calcul (CPU ou GPU).

Ces paramètres sont lus au démarrage du traitement vidéo.


####### Boucle principale de traitement vidéo (`run_loop`) ##########

La fonction `run_loop()` constitue le cœur du système.  
Elle est responsable du traitement de la vidéo image par image et de la coordination entre détection, suivi, analyse et affichage.

Cette fonction est exécutée dans un **thread séparé**, ce qui permet de conserver une interface graphique réactive.

---

### Initialisation

Avant d’entrer dans la boucle principale :

- le modèle YOLO est chargé,
- la vidéo est ouverte via OpenCV,
- la fréquence d’images (FPS) est récupérée,
- les structures d’historique sont réinitialisées.

---

### Traitement par frame

Pour chaque image de la vidéo, les étapes suivantes sont exécutées :

1. **Gestion de l’état**
   - vérification des demandes de pause ou d’arrêt,
   - gestion des sauts temporels dans la vidéo.

2. **Préparation des données**
   - lecture de la frame courante,
   - calcul des dimensions,
   - définition de la zone de danger,
   - création de la MAP.

3. **Inference**
   - appel au modèle YOLO seul si le tracking est désactivé,
   - appel à YOLO avec ByteTrack si le tracking est activé.

4. **Traitement des détections**
   - récupération des boîtes englobantes,
   - identification de la classe détectée,
   - récupération de l’identifiant de suivi (`track_id`) si disponible.

5. **Mise à jour des historiques**
   - enregistrement des positions et des aires des objets suivis,
   - application du lissage des trajectoires.

6. **Analyse du mouvement**
   - estimation de la vitesse et de la direction,
   - prédiction de la position future,
   - analyse de l’approche ou de l’éloignement.

7. **Évaluation du danger**
   - vérification de la présence dans la zone de danger,
   - application de la logique spécifique à chaque type d’objet.

8. **Affichage**
   - dessin des boîtes englobantes sur la vidéo,
   - mise à jour de la MAP (points, trajectoires, flèches),
   - affichage des fenêtres VIDEO et MAP.

La boucle se termine lorsque la vidéo est terminée ou lorsqu’une demande d’arrêt est reçue.


## Logique de danger et analyse du mouvement

La détection d’une situation dangereuse repose sur l’analyse du mouvement des objets par rapport à une zone de danger définie dans l’image.

Cette analyse est rendue possible par le suivi des objets dans le temps.

---

### Zone de danger

Une zone rectangulaire, appelée *zone de danger*, est définie dans la partie centrale et inférieure de l’image.  
Elle représente le couloir de déplacement à surveiller.

Un objet présent en dehors de cette zone est considéré comme non dangereux, quel que soit son mouvement.

---

### Analyse du mouvement

Pour chaque objet suivi, le système conserve un historique de ses positions et de la taille de sa boîte englobante.

À partir de ces informations, plusieurs indicateurs sont calculés :
- évolution de la position du centre de l’objet,
- évolution de l’aire de la boîte englobante,
- direction et vitesse approximatives du déplacement.

Ces indicateurs permettent d’interpréter le comportement de l’objet dans le temps.

---

### Détection de l’approche et de l’éloignement

Un objet est considéré comme **en approche** si :
- l’aire de sa boîte englobante augmente de manière significative,
- ou si son centre se déplace vers le bas de l’image.

Un objet est considéré comme **en éloignement** si le comportement inverse est observé.

Cette distinction permet d’éviter des alertes lorsque l’objet quitte la scène ou s’éloigne de la caméra.

---

### Décision de danger

La décision finale dépend :
- de la présence de l’objet dans la zone de danger,
- de son type (humain, obstacle, autre),
- de son comportement (approche ou éloignement).

Cette logique permet de différencier :
- un humain qui s’approche dans le couloir (situation critique),
- un humain qui s’éloigne (situation non critique),
- un obstacle statique présent dans la zone.


## ByteTrack : rôle et intégration dans le projet

ByteTrack est un algorithme de suivi multi-objets (*multi-object tracking*) utilisé pour associer les détections produites par YOLO sur plusieurs frames consécutives.

Dans ce projet, ByteTrack joue un rôle central en permettant de suivre chaque objet détecté de manière cohérente dans le temps.

---

### Rôle de ByteTrack

ByteTrack permet de :

- attribuer un identifiant unique (`track_id`) à chaque objet détecté,
- maintenir cet identifiant sur plusieurs images consécutives,
- gérer les disparitions temporaires et les réapparitions d’objets,
- fournir une base temporelle stable pour l’analyse du mouvement.

Grâce à ces identifiants persistants, il devient possible de raisonner sur l’évolution d’un objet au fil du temps.

---

### Intégration dans le code

ByteTrack est intégré via l’API Ultralytics de YOLO à l’aide de l’appel suivant :

```python
model.track(
    frame,
    tracker="bytetrack.yaml",
    persist=True
)
Lorsque le tracking est activé :

chaque boîte englobante retournée par YOLO contient un champ id,

cet identifiant correspond au track_id attribué par ByteTrack.

Ces identifiants sont ensuite utilisés par la logique métier pour stocker des historiques et analyser le mouvement des objets.

### Fonctionnement de ByteTrack (lié à `bytetrack.yaml`)

À chaque frame, ByteTrack applique les étapes suivantes :

- **YOLO fournit les détections**  
  → Entrée du tracker (boîtes, scores, classes).

- **Séparation des détections**
  - haute confiance (score ≥ `track_high_thresh: 0.25`)
  - basse confiance (`track_low_thresh: 0.1` ≤ score < 0.25)

- **Prédiction de la position des objets existants**  
  → Modèle de mouvement interne (ex. filtre de Kalman).

- **Association principale (haute confiance)**  
  → Association des tracks avec les détections fiables  
  (`track_high_thresh`, `match_thresh: 0.8`).

- **Association secondaire (basse confiance)**  
  → Tentative de récupération des tracks non associés  
  (`track_low_thresh`).

- **Création de nouveaux objets**  
  → Si une détection ne correspond à aucun track et  
  score ≥ `new_track_thresh: 0.25`.

- **Suppression des objets perdus**  
  → Un track est supprimé s’il n’est pas associé pendant  
  plus de `track_buffer: 30` frames.

L’option `fuse_score: True` permet de combiner la géométrie (IoU) et la confiance
lors du calcul des associations.

