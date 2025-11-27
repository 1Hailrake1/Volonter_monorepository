from loguru import logger
from pathlib import Path
from settings import settings
import os

logs_dir = Path(settings.LOG_DIR)
os.makedirs(logs_dir, exist_ok=True)

logger.add(
	f"{settings.LOG_DIR}/app.log",
	enqueue=True,
	format="{time} {level} {message}",
	level="DEBUG",
	rotation="10 MB",
    retention="14 days",
    compression="zip",
	backtrace=True,
    diagnose=True,
)

logger.info(f"✅ Logger initialized. Log file: {logs_dir}")