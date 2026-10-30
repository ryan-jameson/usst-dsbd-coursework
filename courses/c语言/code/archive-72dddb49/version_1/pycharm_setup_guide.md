# PyCharm OpenCV 配置指南

## 推荐方案：直接使用系统解释器

### 步骤 1：选择系统解释器

1. 在 "Add Python Interpreter" 对话框中
2. 选择 **"Select existing"** 单选按钮
3. 在解释器列表中找到：`D:\Python\python.exe`
4. 选择它并点击 **OK**

### 步骤 2：验证配置

在 PyCharm 的 Python 控制台中运行：

```python
import cv2
print("OpenCV version:", cv2.__version__)
```

### 步骤 3：运行脚本

直接右键点击 `image_processing.py` → `Run 'image_processing'`

## 为什么选择系统解释器？

1. **简单直接**：不需要创建虚拟环境
2. **已安装 OpenCV**：D 盘 Python 已经包含所需包
3. **避免冲突**：不会与现有文件夹冲突
4. **性能更好**：直接使用系统 Python，启动更快

## 如果必须创建虚拟环境

### 选项 A：使用建议的名称

- 点击 "Use 数据管理与课程分析设计 1"
- 虚拟环境将创建在 `D:\数据管理与课程分析设计1`

### 选项 B：手动修改位置

- 将 Location 改为：`D:\Python\envs\数据管理与课程分析设计`
- 或任何其他不冲突的路径

## 验证成功标志

配置成功后，您应该能看到：

- Python 解释器显示为 `D:\Python\python.exe`
- 可以成功导入 `cv2` 模块
- 脚本可以正常运行并显示图像处理结果
