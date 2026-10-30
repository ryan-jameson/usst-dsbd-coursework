from __future__ import annotations


def frame_index_at(elapsed_seconds: float, fps: float, frame_count: int) -> int:
    """Map a shared playback time to a zero-based video frame index."""
    if fps <= 0.0 or frame_count <= 0:
        return 0
    index = int(max(0.0, elapsed_seconds) * fps)
    return min(index, frame_count - 1)
