import time
import cv2
import torch
import torch.nn as nn
import torchvision.transforms as T
from torchvision import models
import numpy as np

# ---- Modèle MobileNetV3 2 classes ----
model = models.mobilenet_v3_small(weights="IMAGENET1K_V1")
model.classifier[3] = nn.Linear(model.classifier[3].in_features, 2)
model.eval()

transform = T.Compose([
    T.ToPILImage(),
    T.Resize((224, 224)),
    T.ToTensor(),
    T.Normalize([0.485, 0.456, 0.406],
                [0.229, 0.224, 0.225])
])

labels = ["Pas obstacle", "Obstacle"]

# ---- Flux UDP via FFmpeg ----
cap = cv2.VideoCapture("udp://@0.0.0.0:5000", cv2.CAP_FFMPEG)
if not cap.isOpened():
    raise RuntimeError("Impossible d’ouvrir le flux UDP.")

print("Flux en cours... Appuie sur ESC pour quitter.")

prev_t, frame_count, fps = time.time(), 0, 0.0
while True:
    ret, frame = cap.read()
    if not ret:
        continue

    img = transform(frame).unsqueeze(0)
    with torch.no_grad():
        out = model(img)
        pred = torch.argmax(out, 1).item()
        label = labels[pred]

    color = (0, 255, 0) if label == "Pas obstacle" else (0, 0, 255)
    cv2.putText(frame, label, (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

    frame_count += 1
    now = time.time()
    if now - prev_t >= 1.0:
        fps = frame_count / (now - prev_t)
        prev_t, frame_count = now, 0
    cv2.putText(frame, f"FPS: {fps:.1f}", (30, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

    cv2.imshow("Détection obstacle (UDP)", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
