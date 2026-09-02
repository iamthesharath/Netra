from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Sighting, AuditLog, Case
from schemas import VerifyRequest

router = APIRouter(prefix="/api", tags=["sightings"])


@router.patch("/sightings/{sighting_id}/verify")
def verify_sighting(sighting_id: str, body: VerifyRequest, db: Session = Depends(get_db)):
    sighting = db.query(Sighting).filter(Sighting.id == sighting_id).first()
    if not sighting:
        raise HTTPException(status_code=404, detail="Sighting not found")

    sighting.officer_verified = body.verified
    case = db.query(Case).filter(Case.id == sighting.case_id).first()
    db.add(
        AuditLog(
            case_id=sighting.case_id,
            action=f"sighting_{'confirmed' if body.verified else 'rejected'}:{sighting_id}",
            performed_by=case.officer_name if case else "unknown",
        )
    )
    db.commit()
    db.refresh(sighting)
    return {"id": sighting.id, "officer_verified": sighting.officer_verified}
