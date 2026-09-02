#!/usr/bin/env python3
"""
Stage 1 standalone smoke-test.
Usage:
  python scripts/test_pipeline.py <reference_photo.jpg> <cctv_video.mp4> [threshold]

Example:
  python scripts/test_pipeline.py photo.jpg cctv.mp4 0.4
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from ml.pipeline import extract_embedding, scan_video


def main():
    if len(sys.argv) < 3:
        print("Usage: python test_pipeline.py <photo> <video> [threshold=0.4]")
        sys.exit(1)

    photo_path = sys.argv[1]
    video_path = sys.argv[2]
    threshold = float(sys.argv[3]) if len(sys.argv) > 3 else 0.4

    print(f"\n[1/3] Generating embedding from: {photo_path}")
    embedding = extract_embedding(photo_path)
    if embedding is None:
        print("  ERROR: No face detected in the reference photo.")
        print("  Make sure the photo has a clearly visible, unobstructed face.")
        sys.exit(1)
    print(f"  OK — 512-dim vector, sample: {[round(v, 4) for v in embedding[:5]]}")

    print(f"\n[2/3] Scanning video: {video_path}  (threshold={threshold})")
    sightings = scan_video(
        video_path=video_path,
        reference_embeddings=[embedding],
        case_id="test",
        video_id="test",
        threshold=threshold,
    )

    print(f"\n[3/3] Found {len(sightings)} sighting(s)")
    for s in sightings:
        t = s["timestamp_in_video"]
        m, sec = divmod(t, 60)
        print(f"  {int(m):02d}:{sec:05.2f}  confidence={s['confidence_score']:.3f}  crop={s.get('cropped_face_path')}")

    if not sightings:
        print("\n  No matches at this threshold.")
        lower = round(threshold - 0.05, 2)
        print(f"  Try: python test_pipeline.py {photo_path} {video_path} {lower}")


if __name__ == "__main__":
    main()
