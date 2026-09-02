import subprocess
import os


def cut_clip(video_path: str, timestamp: float, output_path: str, duration: float = 10.0) -> bool:
    """Cut a clip around the given timestamp. Returns True on success."""
    start = max(0.0, timestamp - 5.0)
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    cmd = [
        "ffmpeg", "-y",
        "-ss", str(start),
        "-i", video_path,
        "-t", str(duration),
        "-c:v", "libx264",
        "-c:a", "aac",
        "-movflags", "+faststart",
        output_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0
