# 项目关键代码汇总

本目录从原项目中复制关键实现代码，便于阅读、提交和归档。原项目文件未被移动或删除。

## 目录说明

### `01_视觉算法核心/`

离线机器视觉处理链，共 7 个 Python 文件：

- `data_preprocessing.py`：数据预处理与增强。
- `object_detection.py`：YOLO 目标检测与模拟检测器。
- `multi_object_tracking.py`：多目标跟踪与轨迹管理。
- `temporal_feature_extraction.py`：时序与战术特征提取。
- `tactical_classification.py`：Temporal GCN 战术分类。
- `visualization.py`：检测、热力图和控球可视化。
- `main.py`：离线分析流程入口与模块编排。

### `02_PC主机端/`

PC 端桌面界面、视频/图片分析、事件筛选、USB 传输和离线演示代码，共 17 个文件。主要入口为：

- `football_gui.py`：桌面 GUI。
- `football_vision_runner.py`：图片序列视觉分析。
- `football_video_runner.py`：视频视觉分析。
- `football_host.py`：事件封装和 USB/TCP 传输。
- `launch_football_gui.bat`：Windows 启动脚本。

已排除测试文件、缓存、演示媒体、输出结果和 `third_party/`。

### `03_M55嵌入式端/`

M55 自有应用代码，共 50 个文件，保留原 `applications/` 模块结构，包括：

- FBP1 帧协议、CRC 和共享内存链路。
- USB CDC 接收与事件分发。
- 足球状态、事件总线与 LVGL 页面。
- Wi-Fi、LLM、ASR、TTS 与语音控制。
- 配置持久化、通信和存储接口。

已排除 RT-Thread、芯片 SDK、第三方包、构建产物、音频资源、1.2 MB 的自动生成音频数组 `football_prompt_data.c`，以及构建脚本明确停用的旧版 `companion`/`recent` 页面。

## 安全处理

原文件 `M55/applications/football/football_settings/football_settings.c` 含硬编码的测试凭据。汇总副本中 5 个默认值已替换为 `<REDACTED>`；原文件未修改。使用汇总代码时请通过安全配置方式提供 Wi-Fi、AI API 和腾讯云凭据。

## 已知限制

- PC 端 `football_host.py` 引用了 `tools/football_wire.py`，但当前项目中不存在该文件。
- PC 端部分脚本依赖原项目的深层目录结构；本目录用于代码阅读和归档，不保证脱离原项目直接运行。
- M55 代码依赖未收集的 RT-Thread、板级 SDK、网络库、LVGL 和音频资源，不能单独编译。
- Python 主要第三方依赖包括 OpenCV、NumPy、PyTorch、Ultralytics、SciPy、scikit-learn、Pillow、Matplotlib、Supervision 和 pyserial。

## 筛选原则

保留入口、核心算法、业务规则、通信协议、界面和必要配置；排除数据集、模型权重、图片/视频、运行输出、缓存、编译产物、生成型大文件和第三方依赖。
