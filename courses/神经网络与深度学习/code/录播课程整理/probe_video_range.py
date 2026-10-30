import json
from pathlib import Path

import requests


root = Path(__file__).resolve().parent
payload = json.loads((root / "data" / "video_infos.json").read_text(encoding="utf-8"))
url = payload["lectures"]["01"]["data"]["videoPlayResponseVoList"][0]["rtmpUrlHdv"]
response = requests.get(
    url,
    headers={"Range": "bytes=0-4095"},
    timeout=30,
    proxies={"http": "http://127.0.0.1:7897", "https": "http://127.0.0.1:7897"},
)
print(
    "status", response.status_code,
    "len", len(response.content),
    "content-range", response.headers.get("Content-Range"),
    "content-length", response.headers.get("Content-Length"),
    "type", response.headers.get("Content-Type"),
    "head", response.content[:16].hex(),
)
