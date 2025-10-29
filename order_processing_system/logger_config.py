import os
import logging
from logging.handlers import RotatingFileHandler

# Create logs directory automatically
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "app.log")

# Configure logger
logger = logging.getLogger("order-system")
logger.setLevel(logging.INFO)

# Prevent adding duplicate handlers if re-imported
if not logger.handlers:
    file_handler = RotatingFileHandler(LOG_FILE, maxBytes=2_000_000, backupCount=3)
    console_handler = logging.StreamHandler()

    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s - %(message)s")
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

__all__ = ["logger"]
