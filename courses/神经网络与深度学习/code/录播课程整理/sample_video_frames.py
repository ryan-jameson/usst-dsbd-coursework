import json
import os
from pathlib import Path
from urllib.parse import urlparse

os.environ.setdefault(
    "OPENCV_FFMPEG_CAPTURE_OPTIONS",
    "http_proxy;http://127.0.0.1:7897|rw_timeout;15000000",
)

import cv2
import requests


ROOT = Path(__file__).resolve().parent
VIDEO_INFO_FILE = ROOT / "data" / "video_infos.json"
OUTPUT_DIR = ROOT / "tmp" / "sample_frames"


def main() -> None:
    os.environ.setdefault("http_proxy", "http://127.0.0.1:7897")
    os.environ.setdefault("https_proxy", "http://127.0.0.1:7897")
    os.environ.setdefault("HTTP_PROXY", "http://127.0.0.1:7897")
    os.environ.setdefault("HTTPS_PROXY", "http://127.0.0.1:7897")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    payload = json.loads(VIDEO_INFO_FILE.read_text(encoding="utf-8"))
    streams = payload["lectures"]["01"]["data"]["videoPlayResponseVoList"]

    for stream_index, stream in enumerate(streams, start=1):
        url = stream.get("rtmpUrlHdv") or stream.get("rtmpUrlDistinct") or stream.get("rtmpUrlFluency")
        if not url:
            print(f"stream={stream_index} missing_url")
            continue
        probe = requests.get(
            url,
            headers={"Range": "bytes=0-4095"},
            timeout=30,
            proxies={"http": "http://127.0.0.1:7897", "https": "http://127.0.0.1:7897"},
        )
        print(
            f"stream={stream_index} range_status={probe.status_code} range_len={len(probe.content)} "
            f"content_range={probe.headers.get('Content-Range')} content_length={probe.headers.get('Content-Length')}"
        )
        capture = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
        opened = capture.isOpened()
        fps = capture.get(cv2.CAP_PROP_FPS)
        frame_count = capture.get(cv2.CAP_PROP_FRAME_COUNT)
        duration = frame_count / fps if fps else 0
        print(
            f"stream={stream_index} host={urlparse(url).hostname} opened={opened} "
            f"fps={fps:.3f} frames={frame_count:.0f} duration={duration:.1f}"
        )
        if not opened:
            capture.release()
            continue

        for second in (60, 300, 900, 1800, 2700):
            capture.set(cv2.CAP_PROP_POS_MSEC, second * 1000)
            ok, frame = capture.read()
            if not ok or frame is None:
                print(f"stream={stream_index} second={second} read_failed")
                continue
            output = OUTPUT_DIR / f"lecture_01_stream_{stream_index}_{second:04d}s.jpg"
            cv2.imwrite(str(output), frame, [cv2.IMWRITE_JPEG_QUALITY, 92])
            height, width = frame.shape[:2]
            print(f"stream={stream_index} second={second} saved={output.name} size={width}x{height}")
        capture.release()


if __name__ == "__main__":
    main()
