import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from database import engine
from models import Base
from routers import cases, photos, videos, sightings
from config import settings

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Netra API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cases.router)
app.include_router(photos.router)
app.include_router(videos.router)
app.include_router(sightings.router)

# Serve face crops and clips as static files
app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")
app.mount("/clips", StaticFiles(directory=settings.clips_dir), name="clips")


@app.get("/health")
def health():
    return {"status": "ok"}
