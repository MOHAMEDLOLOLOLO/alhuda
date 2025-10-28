from ultralytics import YOLO
import cv2

model = YOLO("safewalkbd-l8jbn-4/weights/best.pt")

gst_pipeline = (
    "udpsrc port=5000 ! application/x-rtp,media=video,encoding-name=H264,payload=96 "
    "! rtph264depay ! avdec_h264 ! videoconvert ! appsink"
)
cap = cv2.VideoCapture(gst_pipeline, cv2.CAP_GSTREAMER)

while True:
    ret, frame = cap.read()
    if not ret:
        continue
    H, W = frame.shape[:2]
    results = model.predict(source=frame, conf=0.4, verbose=False)
    obstacle_centre = False

    for box in results[0].boxes:
        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        if (W*0.35 < cx < W*0.65) and (H*0.55 < cy < H*0.95):
            obstacle_centre = True
        color = (0, 0, 255) if obstacle_centre else (0, 255, 0)
        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)

    status = "OBSTACLE" if obstacle_centre else "LIBRE"
    color = (0, 0, 255) if obstacle_centre else (0, 255, 0)
    cv2.putText(frame, status, (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)
    cv2.imshow("Détection obstacle (SafeWalkBD)", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break
cap.release()
cv2.destroyAllWindows()
