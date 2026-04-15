import cv2
import numpy as np
import os
from datetime import datetime
import uuid

class MaskDetector:

    def __init__(self):
        self.model = None
        try:
            from ultralytics import YOLO

            base_dir = os.path.dirname(os.path.abspath(__file__))
            model_path = os.path.join(base_dir, "models", "best.pt")

            self.model = YOLO(model_path)
            print("✅ YOLO model loaded successfully")

        except Exception as e:
            print(f"❌ YOLO load failed: {e}")
            self.model = None

    def detect_face_mask(self, image_bytes):

        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            print("❌ Image decode failed")
            return "without_mask", 0.0

        # ✅ YOLO Detection
        if self.model is not None:
            try:
                results = self.model(img)

                if len(results[0].boxes) == 0:
                    print("⚠ No face detected")
                    return "without_mask", 0.0

                box = results[0].boxes[0]
                class_id = int(box.cls[0])
                confidence = float(box.conf[0]) * 100

                label = "with_mask" if class_id == 0 else "without_mask"

                print(f"✅ Detection: {label} ({confidence:.2f}%)")

                return label, confidence

            except Exception as e:
                print(f"❌ Detection error: {e}")
                return "without_mask", 0.0

        # ❗ Fallback (basic OpenCV)
        print("⚠ Using OpenCV fallback")

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )

        faces = face_cascade.detectMultiScale(gray, 1.1, 5)

        if len(faces) == 0:
            return "without_mask", 0.0

        return "without_mask", 50.0

    def save_no_mask_screenshot(self, image_bytes, confidence=None):
        try:
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if img is None:
                return None

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            filename = f"no_mask_{timestamp}_{unique_id}.jpg"

            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            screenshot_dir = os.path.join(base_dir, "media", "no_mask_screenshots")

            os.makedirs(screenshot_dir, exist_ok=True)

            filepath = os.path.join(screenshot_dir, filename)

            # 🔴 Red border
            img = cv2.copyMakeBorder(
                img, 10, 10, 10, 10,
                cv2.BORDER_CONSTANT,
                value=(0, 0, 255)
            )

            # 📝 Text
            text = f"No Mask {confidence:.1f}%" if confidence else "No Mask"
            cv2.putText(img, text, (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                        (0, 0, 255), 2)

            cv2.imwrite(filepath, img)

            print("📸 Screenshot saved:", filepath)

            return f"no_mask_screenshots/{filename}"

        except Exception as e:
            print(f"❌ Screenshot error: {e}")
            return None


detector = MaskDetector()