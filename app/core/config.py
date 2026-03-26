import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / "data"
MODEL_DIR = DATA_DIR / "models"
DB_PATH   = DATA_DIR / "gold_trading.db"


class Settings:
    # Database
    DB_URL: str = f"sqlite:///{DB_PATH}"

    # Paths
    MODEL_DIR: Path = MODEL_DIR
    DATA_DIR:  Path = DATA_DIR

    # Data source
    SYMBOL:         str = "GC=F"       # Gold Futures — yfinance
    TIMEFRAME:      str = "1h"
    HISTORY_PERIOD: str = "2y"

    # Model
    N_ESTIMATORS: int   = 200
    RANDOM_STATE: int   = 42
    TRAIN_RATIO:  float = 0.80         # 80% train / 20% val (temporal split)

    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = int(os.getenv("PORT", "8000"))


settings = Settings()
