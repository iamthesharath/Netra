import os
import shutil
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from database import get_db
from models import Video, Case, AuditLog
from config import settings

router = APIRouter(prefix="/api/cases", tags=["videos"])


@router.post("/{case_id}/videos")
async def upload_video(
    case_id: str,
    file: UploadFile = File(...),
    camera_name: Optional[str] = Form(None),
    camera_lat: Optional[float] = Form(None),
    camera_lng: Optional[float] = Form(None),
    db: Session = Depends(get_db),
):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    dest_dir = os.path.join(settings.upload_dir, "videos", case_id)
    os.makedirs(dest_dir, exist_ok=True)
    dest_path = os.path.join(dest_dir, file.filename)

    with open(dest_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    video = Video(
        case_id=case_id,
        file_path=dest_path,
        camera_name=camera_name,
        camera_lat=camera_lat,
        camera_lng=camera_lng,
    )
    db.add(video)
    db.add(
        AuditLog(
            case_id=case_id,
            action=f"video_uploaded:{file.filename}",
            performed_by=case.officer_name,
        )
    )
    db.commit()
    db.refresh(video)

    return {
        "id": video.id,
        "file_path": video.file_path,
        "camera_name": video.camera_name,
        "processing_status": video.processing_status,
    }
