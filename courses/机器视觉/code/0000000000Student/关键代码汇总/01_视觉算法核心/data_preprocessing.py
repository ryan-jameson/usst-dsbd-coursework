import os
import cv2
import json
import numpy as np
from sklearn.model_selection import train_test_split
from PIL import Image, ImageEnhance
import random

class FootballDataPreprocessor:
    def __init__(self, data_dir, output_dir):
        self.data_dir = data_dir
        self.output_dir = output_dir
        self.class_names = ['home_player', 'away_player', 'goalkeeper', 'referee', 'ball', 'field_point']
        self.class_ids = {name: idx for idx, name in enumerate(self.class_names)}
        
    def load_images(self):
        images = []
        for filename in sorted(os.listdir(self.data_dir)):
            if filename.endswith('.jpg'):
                img_path = os.path.join(self.data_dir, filename)
                images.append((filename, img_path))
        return images
    
    def apply_augmentation(self, image):
        img = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        
        if random.random() > 0.5:
            img = img.transpose(Image.FLIP_LEFT_RIGHT)
        
        scale_factor = random.uniform(0.9, 1.1)
        width, height = img.size
        new_width, new_height = int(width * scale_factor), int(height * scale_factor)
        img = img.resize((new_width, new_height), Image.BILINEAR)
        left = (new_width - width) // 2
        top = (new_height - height) // 2
        img = img.crop((left, top, left + width, top + height))
        
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(random.uniform(0.8, 1.2))
        
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(random.uniform(0.8, 1.2))
        
        return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    
    def create_train_val_test_split(self, images, train_ratio=0.7, val_ratio=0.2):
        train_val, test = train_test_split(images, test_size=1-train_ratio-val_ratio, random_state=42)
        train, val = train_test_split(train_val, test_size=val_ratio/(train_ratio+val_ratio), random_state=42)
        return train, val, test
    
    def save_dataset(self, images, split_name):
        split_dir = os.path.join(self.output_dir, split_name)
        os.makedirs(split_dir, exist_ok=True)
        
        annotations = []
        for idx, (filename, img_path) in enumerate(images):
            image = cv2.imread(img_path)
            if image is None:
                continue
            
            if split_name == 'train' and random.random() > 0.5:
                image = self.apply_augmentation(image)
            
            output_path = os.path.join(split_dir, filename)
            cv2.imwrite(output_path, image)
            
            annotation = {
                'image_id': idx,
                'file_name': filename,
                'width': image.shape[1],
                'height': image.shape[0],
                'annotations': []
            }
            annotations.append(annotation)
        
        json_path = os.path.join(split_dir, 'annotations.json')
        with open(json_path, 'w') as f:
            json.dump(annotations, f)
        
        print(f"Saved {len(images)} images to {split_dir}")
    
    def process(self):
        images = self.load_images()
        print(f"Found {len(images)} images")
        
        train, val, test = self.create_train_val_test_split(images)
        
        self.save_dataset(train, 'train')
        self.save_dataset(val, 'val')
        self.save_dataset(test, 'test')
        
        print("Data preprocessing completed!")

if __name__ == '__main__':
    data_dir = r'../Soccer/S_BHA vs MU'
    output_dir = r'../outputs/dataset'
    
    preprocessor = FootballDataPreprocessor(data_dir, output_dir)
    preprocessor.process()