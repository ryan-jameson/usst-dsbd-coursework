import cv2
import numpy as np
import torch
from ultralytics import YOLO
import os

class FootballDetector:
    def __init__(self, model_path=None, conf_threshold=0.3, iou_threshold=0.5, use_mock=False):
        self.conf_threshold = conf_threshold
        self.iou_threshold = iou_threshold
        self.class_names = ['home_player', 'away_player', 'goalkeeper', 'referee', 'ball', 'field_point']
        # Try to load a local model; if unavailable or loading fails, fall back to a mock detector
        self.model = None
        self.use_mock = bool(use_mock)
        try:
            if self.use_mock:
                self.model = None
            else:
                if model_path and os.path.exists(model_path):
                    self.model = YOLO(model_path)
                else:
                    # default to local file path; ultralytics will try to download if missing
                    if os.path.exists('yolov8n.pt'):
                        self.model = YOLO('yolov8n.pt')
                    else:
                        # leave model as None to trigger mock behavior
                        self.model = None
        except Exception:
            # loading failed (e.g. corrupted file, network issue) -> use mock detector
            self.model = None

    def detect(self, image):
        # If real model is available, use it; otherwise use mock detector
        if self.model is not None:
            results = self.model(image, conf=self.conf_threshold, iou=self.iou_threshold)
            detections = []
            for result in results:
                for box in result.boxes:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                    cls = int(box.cls[0].cpu().numpy())
                    conf = float(box.conf[0].cpu().numpy())
                    class_name = self.class_names[cls] if cls < len(self.class_names) else 'unknown'
                    detections.append({
                        'bbox': [int(x1), int(y1), int(x2), int(y2)],
                        'class': class_name,
                        'class_id': cls,
                        'confidence': conf,
                        'center': [(x1+x2)//2, (y1+y2)//2]
                    })
            return detections
        else:
            mock = MockDetector(image.shape)
            return mock.detect(image)

    def draw_detections(self, image, detections):
        colors = {
            'home_player': (0, 0, 255),
            'away_player': (255, 0, 0),
            'goalkeeper': (0, 255, 255),
            'referee': (0, 128, 128),
            'ball': (255, 255, 0),
            'field_point': (255, 0, 255)
        }
        
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            color = colors.get(det['class'], (255, 0, 255))
            
            cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
            
            label = f"{det['class']}: {det['confidence']:.2f}"
            cv2.putText(image, label, (x1, y1-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        return image
    
    def train(self, data_config, epochs=100, imgsz=1280):
        if self.model is not None:
            self.model.train(data=data_config, epochs=epochs, imgsz=imgsz, batch=8)
    
    def validate(self, data_config):
        if self.model is not None:
            metrics = self.model.val(data=data_config)
            return metrics


class MockDetector:
    """A simple offline mock detector for testing pipeline without YOLO."""
    def __init__(self, image_shape=(720,1280,3)):
        self.image_shape = image_shape

    def detect(self, image):
        h, w = image.shape[:2]
        # create some fake detections: ball + a few players
        detections = []
        # ball near center
        bx, by, br = w//2, h//2, 20
        detections.append({'bbox':[bx-br, by-br, bx+br, by+br], 'class':'ball', 'class_id':4, 'confidence':0.9, 'center':[bx,by]})
        # home players on left
        for i in range(3):
            x = int(w*0.25)
            y = int(h*(0.2 + 0.2*i))
            detections.append({'bbox':[x-15,y-30,x+15,y+30],'class':'home_player','class_id':0,'confidence':0.8,'center':[x,y]})
        # away players on right
        for i in range(3):
            x = int(w*0.75)
            y = int(h*(0.2 + 0.2*i))
            detections.append({'bbox':[x-15,y-30,x+15,y+30],'class':'away_player','class_id':1,'confidence':0.8,'center':[x,y]})
        return detections
    
    # end of MockDetector
    
    # draw/train/validate moved to FootballDetector

def main():
    detector = FootballDetector()
    
    input_dir = r'../Soccer/S_BHA vs MU'
    output_dir = r'../outputs/detection'
    os.makedirs(output_dir, exist_ok=True)
    
    for filename in sorted(os.listdir(input_dir))[:10]:
        if not filename.endswith('.jpg'):
            continue
        
        img_path = os.path.join(input_dir, filename)
        image = cv2.imread(img_path)
        
        if image is None:
            continue
        
        detections = detector.detect(image)
        image = detector.draw_detections(image, detections)
        
        output_path = os.path.join(output_dir, f'det_{filename}')
        cv2.imwrite(output_path, image)
        
        print(f"Processed {filename}: {len(detections)} detections")

if __name__ == '__main__':
    main()