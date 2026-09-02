from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CaseCreate(BaseModel):
    case_name: str
    officer_name: str


class CaseResponse(BaseModel):
    id: str
    case_name: str
    officer_name: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class VerifyRequest(BaseModel):
    verified: bool
