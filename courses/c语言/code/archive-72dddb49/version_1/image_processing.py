# -*- coding: utf-8 -*-
import cv2
import numpy as np
import matplotlib.pyplot as plt

# 设置中文字体支持
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def read_image_and_get_channels(image_path):
    """
    读取图片并获取各通道的像素值
    """
    # 读取彩色图像
    img = cv2.imread(image_path)
    
    if img is None:
        print(f"错误：无法读取图片 {image_path}")
        return None
    
    # OpenCV默认读取为BGR格式，转换为RGB格式
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # 分离RGB三个通道
    r_channel = img_rgb[:, :, 0]  # 红色通道
    g_channel = img_rgb[:, :, 1]  # 绿色通道
    b_channel = img_rgb[:, :, 2]  # 蓝色通道
    
    print(f"图像尺寸: {img_rgb.shape}")
    print(f"红色通道像素值范围: {r_channel.min()} - {r_channel.max()}")
    print(f"绿色通道像素值范围: {g_channel.min()} - {g_channel.max()}")
    print(f"蓝色通道像素值范围: {b_channel.min()} - {b_channel.max()}")
    
    return img_rgb, r_channel, g_channel, b_channel

def calculate_and_display_histograms(img_rgb, r_channel, g_channel, b_channel):
    """
    统计并显示RGB各通道的直方图
    """
    # 计算各通道的直方图
    hist_r = cv2.calcHist([r_channel], [0], None, [256], [0, 256])
    hist_g = cv2.calcHist([g_channel], [0], None, [256], [0, 256])
    hist_b = cv2.calcHist([b_channel], [0], None, [256], [0, 256])
    
    # 创建子图显示原图和直方图
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # 显示原图
    axes[0, 0].imshow(img_rgb)
    axes[0, 0].set_title('原始图像')
    axes[0, 0].axis('off')
    
    # 显示RGB直方图
    axes[0, 1].plot(hist_r, color='red', alpha=0.7, label='红色通道')
    axes[0, 1].plot(hist_g, color='green', alpha=0.7, label='绿色通道')
    axes[0, 1].plot(hist_b, color='blue', alpha=0.7, label='蓝色通道')
    axes[0, 1].set_title('RGB通道直方图')
    axes[0, 1].set_xlabel('像素值')
    axes[0, 1].set_ylabel('频次')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    
    # 分别显示各通道直方图
    axes[1, 0].plot(hist_r, color='red')
    axes[1, 0].set_title('红色通道直方图')
    axes[1, 0].set_xlabel('像素值')
    axes[1, 0].set_ylabel('频次')
    axes[1, 0].grid(True, alpha=0.3)
    
    axes[1, 1].plot(hist_g, color='green')
    axes[1, 1].set_title('绿色通道直方图')
    axes[1, 1].set_xlabel('像素值')
    axes[1, 1].set_ylabel('频次')
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    
    # 打印直方图统计信息
    print("\n直方图统计信息:")
    print(f"红色通道 - 最大值: {hist_r.max()}, 最小值: {hist_r.min()}")
    print(f"绿色通道 - 最大值: {hist_g.max()}, 最小值: {hist_g.min()}")
    print(f"蓝色通道 - 最大值: {hist_b.max()}, 最小值: {hist_b.min()}")
    
    return hist_r, hist_g, hist_b

def convert_to_grayscale(img_rgb):
    """
    将彩色图转换为灰度图
    """
    # 方法1：使用OpenCV的cvtColor函数
    gray_cv2 = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
    
    # 方法2：使用加权平均法 (推荐方法)
    # 使用标准的RGB到灰度转换公式: Gray = 0.299*R + 0.587*G + 0.114*B
    gray_weighted = np.dot(img_rgb[...,:3], [0.299, 0.587, 0.114]).astype(np.uint8)
    
    # 方法3：简单平均法
    gray_average = np.mean(img_rgb, axis=2).astype(np.uint8)
    
    # 显示不同灰度转换方法的结果
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # 原图
    axes[0, 0].imshow(img_rgb)
    axes[0, 0].set_title('原始彩色图像')
    axes[0, 0].axis('off')
    
    # OpenCV方法
    axes[0, 1].imshow(gray_cv2, cmap='gray')
    axes[0, 1].set_title('OpenCV灰度转换')
    axes[0, 1].axis('off')
    
    # 加权平均法
    axes[1, 0].imshow(gray_weighted, cmap='gray')
    axes[1, 0].set_title('加权平均法 (0.299R+0.587G+0.114B)')
    axes[1, 0].axis('off')
    
    # 简单平均法
    axes[1, 1].imshow(gray_average, cmap='gray')
    axes[1, 1].set_title('简单平均法')
    axes[1, 1].axis('off')
    
    plt.tight_layout()
    plt.show()
    
    # 计算并显示灰度图直方图
    hist_gray = cv2.calcHist([gray_cv2], [0], None, [256], [0, 256])
    
    plt.figure(figsize=(10, 6))
    plt.subplot(1, 2, 1)
    plt.imshow(gray_cv2, cmap='gray')
    plt.title('灰度图像')
    plt.axis('off')
    
    plt.subplot(1, 2, 2)
    plt.plot(hist_gray, color='black')
    plt.title('灰度图直方图')
    plt.xlabel('像素值')
    plt.ylabel('频次')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    
    print(f"\n灰度图统计信息:")
    print(f"灰度图尺寸: {gray_cv2.shape}")
    print(f"像素值范围: {gray_cv2.min()} - {gray_cv2.max()}")
    print(f"平均像素值: {gray_cv2.mean():.2f}")
    
    return gray_cv2, gray_weighted, gray_average

def main():
    """
    主函数
    """
    image_path = "1.png"  # 图片路径
    
    print("=" * 50)
    print("OpenCV 图像处理任务")
    print("=" * 50)
    
    # 1. 读取图片并获取各通道像素值
    print("\n1. 读取图片并获取各通道像素值...")
    result = read_image_and_get_channels(image_path)
    
    if result is None:
        return
    
    img_rgb, r_channel, g_channel, b_channel = result
    
    # 2. 统计并显示RGB各通道的直方图
    print("\n2. 统计并显示RGB各通道的直方图...")
    hist_r, hist_g, hist_b = calculate_and_display_histograms(img_rgb, r_channel, g_channel, b_channel)
    
    # 3. 将彩色图转换为灰度图
    print("\n3. 将彩色图转换为灰度图...")
    gray_cv2, gray_weighted, gray_average = convert_to_grayscale(img_rgb)
    
    print("\n" + "=" * 50)


if __name__ == "__main__":
    main()