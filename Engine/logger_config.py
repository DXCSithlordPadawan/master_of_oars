"""Centralised logging configuration for the War Galley engine.

All modules import the logger from here. Reads LOG_PATH and AUDIT_LOG_LEVEL
from the environment (.env). Raw secrets and HMAC keys are never logged.
"""
import logging
import logging.handlers
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

_CONFIGURED: bool = False


def get_logger(name: str) -> logging.Logger:
    """Return a named logger, configuring the root handler on first call.

    Call once per module at module level:
        logger = get_logger(__name__)
    """
    global _CONFIGURED
    if not _CONFIGURED:
        _configure_root_logger()
        _CONFIGURED = True
    return logging.getLogger(name)


def _configure_root_logger() -> None:
    """Set up file and stream handlers on the root logger."""
    log_path_str: str = os.getenv("LOG_PATH", "./Engine/logs/security.log")
    log_level_str: str = os.getenv("AUDIT_LOG_LEVEL", "INFO")
    log_level: int = getattr(logging, log_level_str.upper(), logging.INFO)

    log_path = Path(log_path_str)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )

    # Rotating file handler — max 5 MB, 5 backups (DISA STIG AU-9)
    file_handler = logging.handlers.RotatingFileHandler(
        log_path,
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(fmt)
    file_handler.setLevel(log_level)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(fmt)
    stream_handler.setLevel(log_level)

    root = logging.getLogger()
    root.setLevel(log_level)
    # Avoid adding duplicate handlers if called multiple times
    if not root.handlers:
        root.addHandler(file_handler)
        root.addHandler(stream_handler)
