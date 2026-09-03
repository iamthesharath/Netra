import os
import cv2
import numpy as np
import json


def _register_cuda_dll_dirs() -> None:
    """Make CUDA + cuDNN discoverable so onnxruntime can load its GPU provider.

    Covers the cuDNN/cuBLAS DLLs shipped in the pip 'nvidia-*' wheels plus a
    system CUDA Toolkit install. Both os.add_dll_directory and a PATH prepend
    are needed; add_dll_directory alone does not resolve transitive deps here.
    Must run before onnxruntime is imported.
    """
    dll_dirs = []
    try:
        import nvidia
        for base in getattr(nvidia, "__path__", []):
            if not os.path.isdir(base):
                continue
            for sub in os.listdir(base):
                bin_dir = os.path.join(base, sub, "bin")
                if os.path.isdir(bin_dir):
                    dll_dirs.append(bin_dir)
    except ImportError:
        pass

    cuda_root = r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA"
    if os.path.isdir(cuda_root):
        for ver in sorted(os.listdir(cuda_root), reverse=True):
            bin_dir = os.path.join(cuda_root, ver, "bin")
            if os.path.isdir(bin_dir):
                dll_dirs.append(bin_dir)

    for d in dll_dirs:
        try:
            os.add_dll_directory(d)
        except (OSError, AttributeError):
            pass
        os.environ["PATH"] = d + os.pathsep + os.environ.get("PATH", "")


_register_cuda_dll_dirs()

from insightface.app import FaceAnalysis
from config import settings

_app = None


def get_face_app() -> FaceAnalysis:
    global _app
    if _app is None:
        # Use the NVIDIA GPU when CUDA + cuDNN load; fall back to CPU automatically.
        providers = ["CUDAExecutionProvider", "CPUExecutionProvider"]
        _app = FaceAnalysis(name="buffalo_l", providers=providers)
        _app.prepare(ctx_id=0, det_size=(640, 640))
    return _app


def extract_embedding(image_path: str) -> list | None:
    """Return a 512-dim ArcFace embedding for the largest face in the image."""
    app = get_face_app()
    img = cv2.imread(image_path)
    if img is None:
        return None
    faces = app.get(img)
    if not faces:
        return None
    # Pick the largest detected face
    face = max(faces, key=lambda f: (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1]))
    return face.embedding.tolist()


def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def _crop_face(frame: np.ndarray, bbox, padding: int = 20) -> np.ndarray:
    x1, y1, x2, y2 = (int(v) for v in bbox)
    h, w = frame.shape[:2]
    x1 = max(0, x1 - padding)
    y1 = max(0, y1 - padding)
    x2 = min(w, x2 + padding)
    y2 = min(h, y2 + padding)
    return frame[y1:y2, x1:x2]


def scan_video(
    video_path: str,
    reference_embeddings: list[list],
    case_id: str,
    video_id: str,
    threshold: float | None = None,
    sample_rate: float | None = None,
) -> list[dict]:
    """
    Scan a video and return a list of sighting dicts:
      { timestamp_in_video, confidence_score, cropped_face_path }

    cropped_face_path is a relative path under upload_dir (URL-safe).
    Non-matching face embeddings are never stored.
    """
    threshold = threshold if threshold is not None else settings.similarity_threshold
    sample_rate = sample_rate if sample_rate is not None else settings.sample_rate

    app = get_face_app()
    ref_embs = [np.array(e) for e in reference_embeddings]

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    frame_interval = max(1, int(fps * sample_rate))

    sightings: list[dict] = []
    face_counter = 0
    frame_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % frame_interval == 0:
            timestamp = frame_count / fps
            try:
                faces = app.get(frame)
            except Exception:
                frame_count += 1
                continue

            for face in faces:
                emb = face.embedding
                best_sim = max(_cosine_similarity(emb, ref_emb) for ref_emb in ref_embs)

                if best_sim >= threshold:
                    crop = _crop_face(frame, face.bbox)
                    crop_filename = f"{case_id}_{video_id}_{face_counter}.jpg"
                    # Store relative path so URL construction is portable
                    crop_rel = f"faces/{crop_filename}"
                    crop_abs = os.path.join(settings.upload_dir, crop_rel)
                    os.makedirs(os.path.dirname(crop_abs), exist_ok=True)
                    cv2.imwrite(crop_abs, crop)

                    sightings.append(
                        {
                            "timestamp_in_video": round(timestamp, 2),
                            "confidence_score": round(best_sim, 4),
                            "cropped_face_path": crop_rel,
                        }
                    )
                    face_counter += 1

        frame_count += 1

    cap.release()
    return sightings
