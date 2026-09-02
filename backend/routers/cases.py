import json
import os
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from database import get_db
from models import Case, ReferencePhoto, Video, Sighting, AuditLog
from schemas import CaseCreate, CaseResponse
from typing import List
from ml.pipeline import scan_video
from utils.clip import cut_clip
from config import settings

router = APIRouter(prefix="/api/cases", tags=["cases"])


@router.post("", response_model=CaseResponse)
def create_case(body: CaseCreate, db: Session = Depends(get_db)):
    case = Case(case_name=body.case_name, officer_name=body.officer_name)
    db.add(case)
    db.flush()
    db.add(AuditLog(case_id=case.id, action="case_created", performed_by=body.officer_name))
    db.commit()
    db.refresh(case)
    return case


@router.get("", response_model=List[CaseResponse])
def list_cases(db: Session = Depends(get_db)):
    return db.query(Case).order_by(Case.created_at.desc()).all()


@router.get("/{case_id}")
def get_case(case_id: str, db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    sightings_out = []
    for s in case.sightings:
        sightings_out.append(
            {
                "id": s.id,
                "video_id": s.video_id,
                "timestamp_in_video": s.timestamp_in_video,
                "confidence_score": s.confidence_score,
                # Serve face crop via /uploads/faces/<filename>
                "cropped_face_url": f"/uploads/{s.cropped_face_path}" if s.cropped_face_path else None,
                # Serve clip via /clips/<filename>
                "clip_url": f"/clips/{s.clip_path}" if s.clip_path else None,
                "officer_verified": s.officer_verified,
                "camera_name": s.video.camera_name if s.video else None,
            }
        )

    return {
        "id": case.id,
        "case_name": case.case_name,
        "officer_name": case.officer_name,
        "status": case.status,
        "created_at": case.created_at,
        "photos": [{"id": p.id, "image_path": p.image_path} for p in case.photos],
        "videos": [
            {"id": v.id, "camera_name": v.camera_name, "processing_status": v.processing_status}
            for v in case.videos
        ],
        "sightings": sorted(sightings_out, key=lambda x: x["timestamp_in_video"]),
    }


def _run_scan(case_id: str):
    """Background task: scan all videos for a case against its reference embeddings."""
    from database import SessionLocal

    db = SessionLocal()
    case = None
    try:
        case = db.query(Case).filter(Case.id == case_id).first()
        if not case:
            return

        case.status = "processing"
        db.commit()

        photos = db.query(ReferencePhoto).filter(ReferencePhoto.case_id == case_id).all()
        ref_embeddings = [json.loads(p.embedding) for p in photos if p.embedding]

        if not ref_embeddings:
            case.status = "failed"
            db.commit()
            return

        videos = db.query(Video).filter(Video.case_id == case_id).all()

        for video in videos:
            video.processing_status = "processing"
            db.commit()
            try:
                sightings = scan_video(
                    video_path=video.file_path,
                    reference_embeddings=ref_embeddings,
                    case_id=case_id,
                    video_id=video.id,
                )

                for s_data in sightings:
                    ts = s_data["timestamp_in_video"]
                    clip_filename = f"{case_id}_{video.id}_{int(ts * 10)}.mp4"
                    clip_abs = os.path.join(settings.clips_dir, clip_filename)
                    clipped = cut_clip(video.file_path, ts, clip_abs)

                    db.add(
                        Sighting(
                            case_id=case_id,
                            video_id=video.id,
                            timestamp_in_video=ts,
                            confidence_score=s_data["confidence_score"],
                            cropped_face_path=s_data.get("cropped_face_path"),
                            clip_path=clip_filename if clipped else None,
                        )
                    )

                video.processing_status = "done"
                db.commit()

            except Exception as exc:
                video.processing_status = "failed"
                db.commit()

        case.status = "done"
        db.add(AuditLog(case_id=case_id, action="scan_completed", performed_by="system"))
        db.commit()

    except Exception:
        if case:
            case.status = "failed"
            db.commit()
    finally:
        db.close()


@router.delete("/{case_id}")
def delete_case(case_id: str, db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    db.delete(case)
    db.commit()
    return {"message": "Case deleted"}


@router.post("/{case_id}/scan")
def trigger_scan(case_id: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    photos = db.query(ReferencePhoto).filter(ReferencePhoto.case_id == case_id).all()
    if not any(p.embedding for p in photos):
        raise HTTPException(status_code=400, detail="No reference photos with face embeddings found")

    if not db.query(Video).filter(Video.case_id == case_id).first():
        raise HTTPException(status_code=400, detail="No videos uploaded for this case")

    db.add(AuditLog(case_id=case_id, action="scan_triggered", performed_by=case.officer_name))
    db.commit()

    background_tasks.add_task(_run_scan, case_id)
    return {"message": "Scan started", "case_id": case_id}
