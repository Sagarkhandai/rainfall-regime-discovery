from pathlib import Path
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUTS_DIR = BASE_DIR / "outputs"
CSV_PATH = DATA_DIR / "weatherAUS.csv"
if not CSV_PATH.exists():
    CSV_PATH = BASE_DIR / "weatherAUS.csv"

class Settings(BaseModel):
    PROJECT_NAME: str = "Rainfall Atlas · 3D Climate Intelligence Platform"
    API_V1_STR: str = "/api"
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "*"
    ]
    DATA_PATH: Path = CSV_PATH
    OUTPUTS_PATH: Path = OUTPUTS_DIR
    DEFAULT_RANDOM_SEED: int = 42
    DEFAULT_K: int = 4
    DEFAULT_SAMPLE_SIZE: int = 5000
    MAX_PCA_POINTS: int = 2500

settings = Settings()

