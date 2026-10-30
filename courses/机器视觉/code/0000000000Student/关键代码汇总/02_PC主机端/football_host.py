from __future__ import annotations

import argparse
import getpass
import json
import socket
import sys
import threading
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Protocol

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from football_wire import Frame, FrameDecoder, MessageType, encode_frame, json_payload


PROTOCOL_VERSION = 1
DEFAULT_EVENT_TYPE = "football_event"


@dataclass
class FootballEvent:
    protocol_version: int
    message_id: int
    event_type: str
    timestamp: int
    event: str
    team: str
    confidence: float
    danger: int
    ball_x: int
    ball_y: int
    checksum: str
    commentary: str = ""

    def to_ndjson(self) -> bytes:
        return (json.dumps(asdict(self), separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")

    def to_payload(self) -> bytes:
        return json_payload(asdict(self))


class Transport(Protocol):
    def send_event(self, item: FootballEvent) -> None:
        ...

    def close(self) -> None:
        ...


class TcpTransport:
    def __init__(self, bind_host: str, port: int) -> None:
        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server.bind((bind_host, port))
        self._server.listen(1)
        print(f"[pc_host] waiting for board TCP client on {bind_host}:{port}")
        self._conn, self._addr = self._server.accept()
        print(f"[pc_host] board connected from {self._addr[0]}:{self._addr[1]}")

    def send_event(self, item: FootballEvent) -> None:
        self._conn.sendall(item.to_ndjson())

    def close(self) -> None:
        self._conn.close()
        self._server.close()


class UsbSerialTransport:
    def __init__(self, port: str, baudrate: int = 115200) -> None:
        try:
            import serial  # type: ignore
        except ImportError as exc:
            raise RuntimeError("USB mode requires pyserial: pip install pyserial") from exc

        self._serial = serial.Serial(port=port, baudrate=baudrate, timeout=0.1)
        self._decoder = FrameDecoder()
        self._sequence = 1
        self._condition = threading.Condition()
        self._acknowledged: dict[int, Frame] = {}
        self._running = True
        self._reader = threading.Thread(target=self._read_loop, name="football-usb-rx", daemon=True)
        self._reader.start()
        print(f"[pc_host] opened USB serial {port} at {baudrate}")

    def send_event(self, item: FootballEvent) -> None:
        self.send(MessageType.MATCH_EVENT, item.to_payload())

    def _next_sequence(self) -> int:
        with self._condition:
            value = self._sequence
            self._sequence = 1 if value == 0xFFFFFFFF else value + 1
            return value

    def _read_loop(self) -> None:
        while self._running:
            try:
                data = self._serial.read(1024)
            except Exception as exc:
                if self._running:
                    print(f"[pc_host] USB read failed: {exc}")
                break
            if not data:
                continue
            for frame in self._decoder.feed(data):
                if frame.message_type in (MessageType.ACK, MessageType.ERROR):
                    with self._condition:
                        self._acknowledged[frame.acknowledgement] = frame
                        self._condition.notify_all()
                else:
                    text = frame.payload.decode("utf-8", errors="replace")
                    print(f"[pc_host] RX type=0x{frame.message_type:02x} seq={frame.sequence} {text}")

    def send(self, message_type: int, payload: bytes = b"", *, flags: int = 0,
             timeout: float = 2.0, retries: int = 3) -> Frame:
        sequence = self._next_sequence()
        packet = encode_frame(Frame(message_type, sequence, flags=flags, payload=payload))
        for attempt in range(1, retries + 1):
            written = self._serial.write(packet)
            self._serial.flush()
            print(f"[pc_host] USB TX seq={sequence} type=0x{message_type:02x} bytes={written}/{len(packet)}")
            if written != len(packet):
                raise OSError(f"USB serial short write: {written}/{len(packet)} bytes")
            deadline = time.monotonic() + timeout
            with self._condition:
                while sequence not in self._acknowledged:
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        break
                    self._condition.wait(remaining)
                response = self._acknowledged.pop(sequence, None)
            if response is not None:
                if response.message_type == MessageType.ERROR:
                    raise RuntimeError(response.payload.decode("utf-8", errors="replace"))
                return response
            print(f"[pc_host] ACK timeout seq={sequence}, retry {attempt}/{retries}")
        raise TimeoutError(f"device did not acknowledge sequence {sequence}")

    def provision_wifi(self, ssid: str, password: str) -> Frame:
        return self.send(MessageType.WIFI_CONFIG, json_payload({"ssid": ssid, "password": password}))

    def provision_cloud(self, endpoint: str, model: str, api_key: str,
                        secret_id: str, secret_key: str) -> Frame:
        return self.send(MessageType.CLOUD_CONFIG, json_payload({
            "endpoint": endpoint, "model": model, "api_key": api_key,
            "secret_id": secret_id, "secret_key": secret_key,
        }))

    def close(self) -> None:
        self._running = False
        self._reader.join(timeout=1.0)
        self._serial.close()


def make_event(message_id: int, timestamp: int, event_name: str, team: str, confidence: float, danger: int, ball_x: int, ball_y: int) -> FootballEvent:
    return FootballEvent(
        protocol_version=PROTOCOL_VERSION,
        message_id=message_id,
        event_type=DEFAULT_EVENT_TYPE,
        timestamp=timestamp,
        event=event_name,
        team=team,
        confidence=confidence,
        danger=danger,
        ball_x=ball_x,
        ball_y=ball_y,
        checksum="",
    )


def iter_simulated_events(count: int = 120, interval_s: float = 0.5) -> Iterable[FootballEvent]:
    event_names = ["counter_attack", "pressing", "through_ball", "shot_chance", "defensive_recover"]

    for message_id in range(1, count + 1):
        idx = (message_id - 1) % len(event_names)
        yield make_event(
            message_id=message_id,
            timestamp=int(message_id * interval_s * 1000),
            event_name=event_names[idx],
            team="home" if message_id % 2 == 0 else "away",
            confidence=0.70 + ((message_id % 20) / 100.0),
            danger=1 + (message_id % 5),
            ball_x=120 + ((message_id * 37) % 760),
            ball_y=60 + ((message_id * 23) % 360),
        )
        time.sleep(interval_s)


def iter_video_events(video_path: Path | None, fps_sample: int) -> Iterable[FootballEvent]:
    if video_path is None:
        yield from iter_simulated_events()
        return

    try:
        import cv2  # type: ignore
    except ImportError:
        print("[pc_host] cv2 not installed; falling back to simulated events")
        yield from iter_simulated_events()
        return

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        print(f"[pc_host] cannot open {video_path}; falling back to simulated events")
        yield from iter_simulated_events()
        return

    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 1024)
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 576)
    frame_idx = 0
    message_id = 1
    sample_every = max(1, int(fps // max(1, fps_sample)))

    while True:
        ok, _frame = cap.read()
        if not ok:
            break

        frame_idx += 1
        if frame_idx % sample_every != 0:
            continue

        timestamp = int((frame_idx / fps) * 1000)
        if message_id % 9 == 0:
            event_name = "shot_chance"
            danger = 5
        elif message_id % 5 == 0:
            event_name = "pressing"
            danger = 3
        elif message_id % 3 == 0:
            event_name = "through_ball"
            danger = 4
        else:
            event_name = "counter_attack"
            danger = 4

        yield make_event(
            message_id=message_id,
            timestamp=timestamp,
            event_name=event_name,
            team="home" if message_id % 2 == 0 else "away",
            confidence=0.74 + ((message_id % 18) / 100.0),
            danger=danger,
            ball_x=(message_id * 41) % max(1, width),
            ball_y=(message_id * 29) % max(1, height),
        )
        message_id += 1

    cap.release()


def parse_host_port(value: str) -> tuple[str, int]:
    if ":" not in value:
        return value, 5055
    host, port_value = value.rsplit(":", 1)
    return host, int(port_value)


def build_transport(args: argparse.Namespace) -> Transport:
    if args.usb:
        return UsbSerialTransport(args.usb, args.baudrate)

    host, port = parse_host_port(args.tcp_server)
    return TcpTransport(host, port)


def run(args: argparse.Namespace) -> int:
    video = Path(args.video) if args.video else None
    transport = build_transport(args)
    sent = 0

    try:
        if args.provision:
            if not isinstance(transport, UsbSerialTransport):
                raise RuntimeError("provisioning requires --usb COMx")
            ssid = input("Wi-Fi SSID: ").strip()
            wifi_password = getpass.getpass("Wi-Fi password: ")
            api_key = getpass.getpass("DeepSeek API key: ")
            secret_id = getpass.getpass("Tencent SecretId: ")
            secret_key = getpass.getpass("Tencent SecretKey: ")
            transport.provision_wifi(ssid, wifi_password)
            transport.provision_cloud(args.ai_endpoint, args.ai_model, api_key, secret_id, secret_key)
            del wifi_password, api_key, secret_id, secret_key
            print("[pc_host] device configuration accepted; secret values were not logged")
            if args.provision_only:
                return 0
        for item in iter_video_events(video, args.fps_sample):
            transport.send_event(item)
            sent += 1
            print(f"[pc_host] sent #{item.message_id} {item.event} team={item.team} danger={item.danger}")
            if args.max_events and sent >= args.max_events:
                break
    finally:
        transport.close()

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="AI Football Companion PC host sender")
    parser.add_argument("--video", help="input football video path")
    parser.add_argument("--tcp-server", default="0.0.0.0:5055", help="TCP bind address, default 0.0.0.0:5055")
    parser.add_argument("--usb", help="USB serial port, for example COM7")
    parser.add_argument("--baudrate", type=int, default=115200)
    parser.add_argument("--fps-sample", type=int, default=10)
    parser.add_argument("--max-events", type=int, default=0)
    parser.add_argument("--provision", action="store_true", help="interactively provision Wi-Fi/cloud over USB")
    parser.add_argument("--provision-only", action="store_true", help="exit after interactive provisioning")
    parser.add_argument("--ai-endpoint", default="https://api.deepseek.com/chat/completions")
    parser.add_argument("--ai-model", default="deepseek-v4-flash")
    args = parser.parse_args()

    return run(args)


if __name__ == "__main__":
    sys.exit(main())
