from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    database_url: str = "postgresql://netra:netra123@localhost:5432/netra"
    upload_dir: str = "uploads"
    clips_dir: str = "clips"
    similarity_threshold: float = 0.4
    sample_rate: float = 0.5

    model_config = {"env_file": ".env"}


settings = Settings()

os.makedirs(settings.upload_dir, exist_ok=True)
os.makedirs(settings.clips_dir, exist_ok=True)
os.makedirs(os.path.join(settings.upload_dir, "photos"), exist_ok=True)
os.makedirs(os.path.join(settings.upload_dir, "faces"), exist_ok=True)
