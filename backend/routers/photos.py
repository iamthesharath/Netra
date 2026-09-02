import json
import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from database import get_db
from models import ReferencePhoto, Case, AuditLog
from config import settings
from ml.pipeline import extract_embedding

router = APIRouter(prefix="/api/cases", tags=["photos"])


@router.post("/{case_id}/photos")
async def upload_photo(case_id: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    dest_dir = os.path.join(settings.upload_dir, "photos", case_id)
    os.makedirs(dest_dir, exist_ok=True)
    dest_path = os.path.join(dest_dir, file.filename)

    with open(dest_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    embedding = extract_embedding(dest_path)

    photo = ReferencePhoto(
        case_id=case_id,
        image_path=dest_path,
        embedding=json.dumps(embedding) if embedding else None,
    )
    db.add(photo)
    db.add(
        AuditLog(
            case_id=case_id,
            action=f"photo_uploaded:{file.filename}",
            performed_by=case.officer_name,
        )
    )
    db.commit()
    db.refresh(photo)

    return {
        "id": photo.id,
        "image_path": photo.image_path,
        "embedding_generated": embedding is not None,
    }
