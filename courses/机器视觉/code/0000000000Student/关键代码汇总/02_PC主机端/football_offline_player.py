from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from football_offline_assets import TIMELINE_FILE, due_events, load_timeline, playback_end_ms
from football_host import UsbSerialTransport


def run(args: argparse.Namespace) -> int:
    events = load_timeline(args.timeline)
    transport = None if args.dry_run else UsbSerialTransport(args.usb)
    sent: set[int] = set()
    end_ms = playback_end_ms(events, args.duration_ms)
    start = time.monotonic()
    try:
        while len(sent) < len(events) or int((time.monotonic() - start) * 1000) < end_ms:
            elapsed_ms = int((time.monotonic() - start) * 1000)
            for event in due_events(events, elapsed_ms, sent):
                if transport is not None:
                    transport.send_event(event.to_football_event())
                sent.add(event.message_id)
                print("@offline-status " + json.dumps({"event": event.event, "events_sent": len(sent),
                                                       "total_events": len(events), "elapsed_ms": elapsed_ms}, ensure_ascii=False), flush=True)
            time.sleep(0.02)
    finally:
        if transport is not None:
            transport.close()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeline", type=Path, default=TIMELINE_FILE)
    parser.add_argument("--usb", default="COM10")
    parser.add_argument("--duration-ms", type=int, default=60_000,
                        help="Minimum playback duration; keep USB event process alive until this time.")
    parser.add_argument("--dry-run", action="store_true")
    return run(parser.parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
