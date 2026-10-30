# AI Football Companion PC Host

The desktop console reads local football JPG frames, runs the existing YOLO/tracking/rule pipeline, and sends only CRC-protected FBP1 `MATCH_EVENT` frames containing the existing UTF-8 JSON event to M55 USB CDC. Source images and analysis overlays remain on the PC; M55 owns LVGL, WiFi, DeepSeek, TTS, and speaker playback.

## Desktop Console

Launch the desktop application from Windows:

```powershell
pc_host/launch_football_gui.bat
```

The same launcher is available through the `AI Football Companion PC.lnk` desktop shortcut. The console defaults to the repository BHA vs MU test set (`451` JPG frames), the local `yolov8n.pt` model, and M55 USB `COM10`.

For the normal demonstration, reset M55 and click **Start Demo**. The first source frame appears immediately while YOLO loads; the source and overlay panels then advance continuously as frames are processed. Each detected tactical event is sent to M55 USB as the existing UTF-8 JSON event in an FBP1 frame. Use **Preview only** only when the board is not connected. **Stop Demo** terminates the worker and force-stops its process tree after 1.2 seconds if it does not exit.

If Windows assigns a different CDC port, change the single `M55 USB Port` field before starting. The live preview cache is written to `pc_host/outputs/live_preview/latest_source.jpg` and `pc_host/outputs/live_preview/latest_overlay.jpg`.

## VisionRunner Dry Run

```powershell
python pc_host/football_vision_runner.py --images "D:\RT-ThreadStudio\workspace\基于机器视觉的运动场景识别\基于机器视觉的运动场景识别\基于机器视觉的运动场景识别\Soccer\S_BHA vs MU" --detector-weights "D:\RT-ThreadStudio\workspace\基于机器视觉的运动场景识别\基于机器视觉的运动场景识别\基于机器视觉的运动场景识别\yolov8n.pt" --dry-run --fps 5 --max-frames 10 --preview-dir pc_host\outputs\live_preview --save-overlay pc_host\outputs\live_preview\overlays
```

The run writes `pc_host/outputs/vision_report.jsonl` and `pc_host/outputs/vision_report.csv`. `@vision-status` output is for the local GUI; it is not an additional board protocol.

## M55 Built-In Test Configuration

The current M55 test firmware contains private WiFi, DeepSeek, and Tencent settings. Flash the M55 image and press reset; do not use PC provisioning. The firmware ignores `/flash/football_cloud.cfg` while this test mode is enabled, so an older persisted record cannot override the boot configuration.

Before starting the PC stream, use `football_config` and `football_cloud` on M55 to verify that configuration and WiFi connection are progressing. The desktop program only needs the USB CDC COM port. This firmware contains private credentials and must not be distributed; rotate those credentials after testing and restore secure provisioning before any broader use.

## Device Bring-Up

The flashing order, WHD resources, shell checks, provisioning flow, and recovery steps are in [`../docs/football-console-bringup-zh.md`](../docs/football-console-bringup-zh.md).
