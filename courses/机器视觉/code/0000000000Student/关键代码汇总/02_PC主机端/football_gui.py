from __future__ import annotations

import os
import json
import queue
import subprocess
import sys
import threading
import time
from pathlib import Path
from tkinter import BOTH, END, LEFT, RIGHT, X, BooleanVar, StringVar, Text, Tk, messagebox
from tkinter import ttk

from PIL import Image, ImageTk

from football_console_support import parse_vision_status
from football_offline_assets import MANUAL_TIMELINE_FILE, MANUAL_YOLO_VIDEO, SOURCE_VIDEO
from football_playback_clock import frame_index_at


ROOT = Path(__file__).resolve().parents[1]
OFFLINE_PLAYER_SCRIPT = Path(__file__).resolve().with_name("football_offline_player.py")
VIDEO_PATH = SOURCE_VIDEO


def python_console_executable() -> str:
    executable = Path(sys.executable)
    if executable.name.lower() == "pythonw.exe":
        candidate = executable.with_name("python.exe")
        if candidate.exists():
            return str(candidate)
    return str(executable)


class FootballCompanionGui:
    def __init__(self, root: Tk) -> None:
        self.root = root
        self.root.title("AI Football Companion PC")
        self.root.geometry("1180x780")
        self.root.minsize(980, 660)

        self.usb_port = StringVar(value="COM10")
        self.fps = StringVar(value="5")
        self.max_frames = StringVar(value="0")
        self.dry_run = BooleanVar(value=False)
        self.status = StringVar(value="Ready - COM10")
        self.frame_status = StringVar(value="Frame: 0/0")
        self.tactic_status = StringVar(value="Tactic: waiting")
        self.event_status = StringVar(value="Events: 0 | ACK: 0")

        self.process: subprocess.Popen[str] | None = None
        self.log_queue: queue.Queue[str] = queue.Queue()
        self._source_photo: ImageTk.PhotoImage | None = None
        self._overlay_photo: ImageTk.PhotoImage | None = None
        self._stopping_pid: int | None = None
        self._source_capture = None
        self._overlay_capture = None
        self._playback_started_at = 0.0
        self._source_fps = 30.0
        self._overlay_fps = 10.0
        self._source_frame_count = 0
        self._overlay_frame_count = 0
        self._source_frame_index = -1
        self._overlay_frame_index = -1

        self._configure_style()
        self._build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.after(100, self._drain_logs)

    def _configure_style(self) -> None:
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass
        self.root.configure(bg="#101820")
        style.configure(".", font=("Microsoft YaHei UI", 10))
        style.configure("TFrame", background="#101820")
        style.configure("Panel.TFrame", background="#18242f")
        style.configure("Title.TLabel", background="#101820", foreground="#f4f7fb", font=("Microsoft YaHei UI", 20, "bold"))
        style.configure("Sub.TLabel", background="#101820", foreground="#9fb3c8")
        style.configure("TLabel", background="#18242f", foreground="#e7eef7")
        style.configure("Muted.TLabel", background="#18242f", foreground="#9fb3c8")
        style.configure("Status.TLabel", background="#101820", foreground="#70e000", font=("Consolas", 10, "bold"))
        style.configure("TButton", padding=(10, 6))
        style.configure("Accent.TButton", foreground="#071013", background="#4cc9f0")
        style.configure("Danger.TButton", foreground="#ffffff", background="#b23a48")
        style.configure("TRadiobutton", background="#18242f", foreground="#e7eef7")
        style.configure("TCheckbutton", background="#18242f", foreground="#e7eef7")
        style.configure("TEntry", fieldbackground="#f8fbff")

    def _build_ui(self) -> None:
        outer = ttk.Frame(self.root, padding=16)
        outer.pack(fill=BOTH, expand=True)
        ttk.Label(outer, text="AI Football Companion PC", style="Title.TLabel").pack(anchor="w")
        ttk.Label(outer, text="播放原始比赛视频，并将人工确认事件按时间轴发送给 M55", style="Sub.TLabel").pack(anchor="w", pady=(3, 12))

        body = ttk.Panedwindow(outer, orient="horizontal")
        body.pack(fill=BOTH, expand=True)
        controls = ttk.Frame(body, style="Panel.TFrame", padding=14)
        display = ttk.Frame(body, style="Panel.TFrame", padding=14)
        body.add(controls, weight=1)
        body.add(display, weight=3)
        self._build_controls(controls)
        self._build_display(display)

        footer = ttk.Frame(outer)
        footer.pack(fill=X, pady=(10, 0))
        ttk.Label(footer, textvariable=self.status, style="Status.TLabel").pack(side=LEFT)
        ttk.Label(footer, text="Offline video + precomputed FBP1 timeline | USB events: UTF-8 JSON", style="Sub.TLabel").pack(side=RIGHT)

    def _build_controls(self, parent: ttk.Frame) -> None:
        ttk.Label(parent, text="Demo Control", font=("Microsoft YaHei UI", 13, "bold")).pack(anchor="w")
        ttk.Label(parent, text="60-second original match clip\nManual event timeline + YOLO tracking video\nNo runtime YOLO inference", style="Muted.TLabel", justify="left").pack(anchor="w", pady=(8, 18))
        ttk.Label(parent, text="M55 USB Port").pack(anchor="w")
        ttk.Entry(parent, textvariable=self.usb_port).pack(fill=X, pady=(4, 10))
        ttk.Checkbutton(parent, text="Preview only (do not send to board)", variable=self.dry_run).pack(anchor="w", pady=(0, 16))
        actions = ttk.Frame(parent, style="Panel.TFrame")
        actions.pack(fill=X)
        self.start_button = ttk.Button(actions, text="Start Demo", style="Accent.TButton", command=self.start_session)
        self.start_button.pack(side=LEFT, fill=X, expand=True)
        self.stop_button = ttk.Button(actions, text="Stop Demo", style="Danger.TButton", command=self.stop_session, state="disabled")
        self.stop_button.pack(side=RIGHT, padx=(6, 0))
        ttk.Label(parent, text="Reset M55 before Start Demo.\nLeft and right videos play in sync; M55 receives one prepared event every five seconds.", style="Muted.TLabel", wraplength=240, justify="left").pack(anchor="w", pady=(20, 0))

    def _build_display(self, parent: ttk.Frame) -> None:
        counters = ttk.Frame(parent, style="Panel.TFrame")
        counters.pack(fill=X)
        ttk.Label(counters, textvariable=self.frame_status).pack(side=LEFT)
        ttk.Label(counters, textvariable=self.tactic_status).pack(side=LEFT, padx=18)
        ttk.Label(counters, textvariable=self.event_status).pack(side=RIGHT)

        preview = ttk.Frame(parent, style="Panel.TFrame")
        preview.pack(fill=BOTH, expand=True, pady=(10, 8))
        source = ttk.Frame(preview, style="Panel.TFrame")
        overlay = ttk.Frame(preview, style="Panel.TFrame")
        source.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 5))
        overlay.pack(side=RIGHT, fill=BOTH, expand=True, padx=(5, 0))
        ttk.Label(source, text="Original Match Video").pack(anchor="w")
        ttk.Label(overlay, text="YOLO Tracking Video").pack(anchor="w")
        self.source_label = ttk.Label(source, text="Waiting for source frame", anchor="center")
        self.overlay_label = ttk.Label(overlay, text="Waiting for overlay", anchor="center")
        self.source_label.pack(fill=BOTH, expand=True, pady=8)
        self.overlay_label.pack(fill=BOTH, expand=True, pady=8)

        log_top = ttk.Frame(parent, style="Panel.TFrame")
        log_top.pack(fill=X)
        ttk.Label(log_top, text="Runtime Log").pack(side=LEFT)
        ttk.Button(log_top, text="Clear", command=self._clear_log).pack(side=RIGHT)
        self.log_text = Text(parent, bg="#071013", fg="#d8f3dc", insertbackground="#ffffff", relief="flat", padx=10, pady=10, wrap="word", font=("Consolas", 10), height=12)
        self.log_text.pack(fill=BOTH, expand=True, pady=(6, 0))
        self._append_log("Ready. Reset M55, then click Start Demo. COM10 sends events to the board.")

    def _offline_command(self) -> list[str] | None:
        if not VIDEO_PATH.is_file() or not MANUAL_YOLO_VIDEO.is_file() or not MANUAL_TIMELINE_FILE.is_file():
            messagebox.showerror("AI Football Companion", "Manual-review demo assets are missing.")
            return None
        if not self.dry_run.get() and not self.usb_port.get().strip():
            messagebox.showerror("AI Football Companion", "USB COM port is required outside dry run.")
            return None
        command = [python_console_executable(), "-u", str(OFFLINE_PLAYER_SCRIPT), "--timeline", str(MANUAL_TIMELINE_FILE),
                   "--duration-ms", "60000"]
        command.append("--dry-run") if self.dry_run.get() else command.extend(["--usb", self.usb_port.get().strip()])
        return command

    def start_session(self) -> None:
        if self.process is not None:
            return
        command = self._offline_command()
        if command is None:
            return
        self._start_source_video()
        self._append_log("$ " + " ".join(f'"{item}"' if " " in item else item for item in command))
        try:
            creationflags = 0
            if os.name == "nt":
                creationflags = subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP
            self.process = subprocess.Popen(command, cwd=str(ROOT), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, creationflags=creationflags)
        except OSError as exc:
            self.process = None
            messagebox.showerror("AI Football Companion", f"Cannot start offline demo: {exc}")
            return
        self.status.set("Playing prepared video and sending timeline")
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        threading.Thread(target=self._read_process_output, daemon=True).start()

    def stop_session(self) -> None:
        if self.process is not None:
            self._append_log("[gui] stopping offline demo")
            self.status.set("Stopping offline demo")
            self.stop_button.configure(state="disabled")
            self._stopping_pid = self.process.pid
            self.process.terminate()
            self.root.after(1200, self._force_stop_process)
        self._stop_source_video()

    def _force_stop_process(self) -> None:
        pid = self._stopping_pid
        self._stopping_pid = None
        if pid is None or self.process is None or self.process.poll() is not None:
            return
        self._append_log("[gui] runner did not exit in time; forcing process tree stop")
        if os.name == "nt":
            subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], check=False,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            self.process.kill()

    def _start_source_video(self) -> None:
        import cv2
        self._stop_source_video()
        self._source_capture = cv2.VideoCapture(str(VIDEO_PATH))
        self._overlay_capture = cv2.VideoCapture(str(MANUAL_YOLO_VIDEO))
        self._source_fps = self._source_capture.get(cv2.CAP_PROP_FPS) or 30.0
        self._overlay_fps = self._overlay_capture.get(cv2.CAP_PROP_FPS) or 10.0
        self._source_frame_count = int(self._source_capture.get(cv2.CAP_PROP_FRAME_COUNT))
        self._overlay_frame_count = int(self._overlay_capture.get(cv2.CAP_PROP_FRAME_COUNT))
        self._source_frame_index = -1
        self._overlay_frame_index = -1
        self._playback_started_at = time.monotonic()
        self._play_source_video()

    def _stop_source_video(self) -> None:
        if self._source_capture is not None:
            self._source_capture.release()
            self._source_capture = None
        if self._overlay_capture is not None:
            self._overlay_capture.release()
            self._overlay_capture = None
        self._playback_started_at = 0.0

    @staticmethod
    def _read_capture_to(capture, current_index: int, target_index: int):
        frame = None
        while current_index < target_index:
            ok, frame = capture.read()
            if not ok:
                return None, current_index, False
            current_index += 1
        return frame, current_index, True

    def _play_source_video(self) -> None:
        if self._source_capture is None or self._overlay_capture is None:
            return
        elapsed = time.monotonic() - self._playback_started_at
        source_target = frame_index_at(elapsed, self._source_fps, self._source_frame_count)
        overlay_target = frame_index_at(elapsed, self._overlay_fps, self._overlay_frame_count)
        source_frame, self._source_frame_index, source_ok = self._read_capture_to(
            self._source_capture, self._source_frame_index, source_target)
        overlay_frame, self._overlay_frame_index, overlay_ok = self._read_capture_to(
            self._overlay_capture, self._overlay_frame_index, overlay_target)
        if not source_ok or not overlay_ok:
            return
        if source_frame is not None:
            import cv2
            image = Image.fromarray(cv2.cvtColor(source_frame, cv2.COLOR_BGR2RGB))
            image.thumbnail((460, 360), Image.LANCZOS)
            self._source_photo = ImageTk.PhotoImage(image)
            self.source_label.configure(image=self._source_photo, text="")
        if overlay_frame is not None:
            import cv2
            overlay_image = Image.fromarray(cv2.cvtColor(overlay_frame, cv2.COLOR_BGR2RGB))
            overlay_image.thumbnail((460, 360), Image.LANCZOS)
            self._overlay_photo = ImageTk.PhotoImage(overlay_image)
            self.overlay_label.configure(image=self._overlay_photo, text="")
        self.root.after(33, self._play_source_video)

    def _read_process_output(self) -> None:
        assert self.process is not None
        if self.process.stdout is not None:
            for line in self.process.stdout:
                self.log_queue.put(line.rstrip("\n"))
        code = self.process.wait()
        self.log_queue.put(f"[gui] offline player exited with code {code}")
        self.log_queue.put("__PROCESS_DONE__")

    def _drain_logs(self) -> None:
        while True:
            try:
                item = self.log_queue.get_nowait()
            except queue.Empty:
                break
            if item == "__PROCESS_DONE__":
                self.process = None
                self._stop_source_video()
                self._stopping_pid = None
                self.status.set("Ready")
                self.start_button.configure(state="normal")
                self.stop_button.configure(state="disabled")
            else:
                if item.startswith("@offline-status "):
                    data = json.loads(item[len("@offline-status "):])
                    self.tactic_status.set(f"Event: {data['event']}")
                    self.event_status.set(f"Events: {data['events_sent']} / {data['total_events']}")
                    continue
                status = parse_vision_status(item)
                if status is None:
                    self._append_log(item)
                else:
                    self.frame_status.set(f"Frame: {status.frame}/{status.total_frames}")
                    self.tactic_status.set(f"Tactic: {status.tactic}")
                    self.event_status.set(f"Events: {status.events_sent} | ACK: {status.acks}")
        self.root.after(100, self._drain_logs)

    def _clear_log(self) -> None:
        self.log_text.delete("1.0", END)

    def _append_log(self, text: str) -> None:
        self.log_text.insert(END, text + "\n")
        self.log_text.see(END)

    def on_close(self) -> None:
        if self.process is not None:
            if not messagebox.askyesno("AI Football Companion", "Vision stream is still running. Stop and exit?"):
                return
            self.stop_session()
        self.root.destroy()


def main() -> None:
    root = Tk()
    FootballCompanionGui(root)
    root.mainloop()


if __name__ == "__main__":
    main()
