from __future__ import annotations

import logging
from pathlib import Path

from typeflow.assets import project_root


def setup_logger() -> logging.Logger:
    log_dir = project_root() / "logs"
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / "typeflow.log"

    logger = logging.getLogger("typeflow")
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    logger.propagate = False
    logger.info("Logger initialized. Log file: %s", log_file)
    return logger
