# -*- coding: utf-8 -*-
import cv2
import numpy as np

def test_opencv():
    """Test OpenCV basic functions"""
    print("=" * 50)
    print("OpenCV Function Test")
    print("=" * 50)
    
    # Test OpenCV version
    print(f"OpenCV version: {cv2.__version__}")
    
    # Read image
    image_path = "1.png"
    img = cv2.imread(image_path)
    
    if img is None:
        print(f"Error: Cannot read image {image_path}")
        return False
    
    print(f"Image size: {img.shape}")
    print(f"Image type: {img.dtype}")
    
    # Convert to RGB format
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Separate RGB channels
    r_channel = img_rgb[:, :, 0]
    g_channel = img_rgb[:, :, 1]
    b_channel = img_rgb[:, :, 2]
    
    print(f"Red channel pixel range: {r_channel.min()} - {r_channel.max()}")
    print(f"Green channel pixel range: {g_channel.min()} - {g_channel.max()}")
    print(f"Blue channel pixel range: {b_channel.min()} - {b_channel.max()}")
    
    # Convert to grayscale
    gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
    print(f"Grayscale image size: {gray.shape}")
    print(f"Grayscale pixel range: {gray.min()} - {gray.max()}")
    
    print("\nAll function tests passed!")
    return True

if __name__ == "__main__":
    test_opencv()
