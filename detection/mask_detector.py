import cv2
import numpy as np
import os
from datetime import datetime
import uuid

class MaskDetector:

    def __init__(self):
        self.model = None
        self.strict_yolo = os.getenv("YOLO_STRICT", "1").lower() not in ("0", "false", "no")
        try:
            from ultralytics import YOLO  # type: ignore

            base_dir = os.path.dirname(os.path.abspath(__file__))
            model_path = os.path.join(base_dir, "models", "best.pt")
            self.model = YOLO(model_path)
        except Exception as e:
            print(f"⚠ ultralytics/YOLO not available ({e}). Using OpenCV fallback detector.")
            if self.strict_yolo:
                raise

    def detect_face_mask(self, image_bytes):

        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            return "without_mask", 0.0

        # If YOLO model is available, use it
        if self.model is not None:
            results = self.model(img)

            probs = results[0].probs.data.tolist()

            class_id = probs.index(max(probs))
            confidence = max(probs)

            label = "with_mask" if class_id == 0 else "without_mask"

            return label, confidence

        if self.strict_yolo:
            raise RuntimeError("YOLO model not loaded; set YOLO_STRICT=0 to allow OpenCV fallback")

        # OpenCV fallback heuristic (fast, no external dependency)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(60, 60),
        )

        if len(faces) == 0:
            return "without_mask", 0.0

        x, y, w, h = faces[0]
        face = img[y : y + h, x : x + w]
        lower = face[int(h * 0.5) :]
        hsv = cv2.cvtColor(lower, cv2.COLOR_BGR2HSV)
        color_std = float(np.std(hsv[:, :, 1]))

        # Lower saturation variance tends to indicate mask-like uniformity
        if color_std < 25:
            return "with_mask", 0.75
        return "without_mask", 0.75

    def save_no_mask_screenshot(self, image_bytes, confidence=None):
        """
        Auto screenshot functionality - saves image when no mask is detected
        """
        try:
            # Convert bytes to numpy array
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                return None
                
            # Generate unique filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]  # Short unique ID
            filename = f"no_mask_{timestamp}_{unique_id}.jpg"
            
            # Get media directory path
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Go up to backend folder
            screenshot_dir = os.path.join(base_dir, "media", "no_mask_screenshots")
            
            # Create directory if it doesn't exist
            os.makedirs(screenshot_dir, exist_ok=True)
            
            # Full file path
            filepath = os.path.join(screenshot_dir, filename)
            
            # Add timestamp text overlay on image
            font = cv2.FONT_HERSHEY_SIMPLEX
            text = f"No Mask - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            if confidence:
                text += f" - {confidence:.1f}%"
            
            # Add red border for no mask detection
            border_color = (0, 0, 255)  # Red in BGR
            border_thickness = 10
            img_with_border = cv2.copyMakeBorder(img, border_thickness, border_thickness, 
                                               border_thickness, border_thickness, 
                                               cv2.BORDER_CONSTANT, value=border_color)
            
            # Add text to image
            cv2.putText(img_with_border, text, (20, 40), font, 0.8, (0, 0, 255), 2)
            
            # Save the image
            cv2.imwrite(filepath, img_with_border)
            
            # Return relative path for database storage
            return f"no_mask_screenshots/{filename}"
            
        except Exception as e:
            print(f"Error saving screenshot: {e}")
            return None

detector = MaskDetector()