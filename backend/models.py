import uuid
from sqlalchemy import Column, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


def gen_uuid():
    return str(uuid.uuid4())


class Case(Base):
    __tablename__ = "cases"

    id = Column(String, primary_key=True, default=gen_uuid)
    case_name = Column(String, nullable=False)
    officer_name = Column(String, nullable=False)
    status = Column(String, default="pending")  # pending | processing | done | failed
    created_at = Column(DateTime, server_default=func.now())

    photos = relationship("ReferencePhoto", back_populates="case", cascade="all, delete")
    videos = relationship("Video", back_populates="case", cascade="all, delete")
    sightings = relationship("Sighting", back_populates="case", cascade="all, delete")
    audit_logs = relationship("AuditLog", back_populates="case", cascade="all, delete")


class ReferencePhoto(Base):
    __tablename__ = "reference_photos"

    id = Column(String, primary_key=True, default=gen_uuid)
    case_id = Column(String, ForeignKey("cases.id"), nullable=False)
    image_path = Column(String, nullable=False)
    embedding = Column(Text)  # JSON-serialised 512-dim ArcFace vector
    uploaded_at = Column(DateTime, server_default=func.now())

    case = relationship("Case", back_populates="photos")


class Video(Base):
    __tablename__ = "videos"

    id = Column(String, primary_key=True, default=gen_uuid)
    case_id = Column(String, ForeignKey("cases.id"), nullable=False)
    file_path = Column(String, nullable=False)
    camera_name = Column(String)
    camera_lat = Column(Float)
    camera_lng = Column(Float)
    recording_start_time = Column(DateTime)
    duration_seconds = Column(Float)
    processing_status = Column(String, default="pending")  # pending | processing | done | failed

    case = relationship("Case", back_populates="videos")
    sightings = relationship("Sighting", back_populates="video", cascade="all, delete")


class Sighting(Base):
    __tablename__ = "sightings"

    id = Column(String, primary_key=True, default=gen_uuid)
    case_id = Column(String, ForeignKey("cases.id"), nullable=False)
    video_id = Column(String, ForeignKey("videos.id"), nullable=False)
    timestamp_in_video = Column(Float, nullable=False)  # seconds from start
    real_world_time = Column(DateTime)
    confidence_score = Column(Float, nullable=False)
    cropped_face_path = Column(String)  # relative path under upload_dir
    clip_path = Column(String)          # relative path under clips_dir
    officer_verified = Column(Boolean)  # None = unreviewed

    case = relationship("Case", back_populates="sightings")
    video = relationship("Video", back_populates="sightings")


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(String, primary_key=True, default=gen_uuid)
    case_id = Column(String, ForeignKey("cases.id"), nullable=False)
    action = Column(String, nullable=False)
    performed_by = Column(String, nullable=False)
    timestamp = Column(DateTime, server_default=func.now())

    case = relationship("Case", back_populates="audit_logs")
