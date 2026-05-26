"""
src/utils/logger.py
Structured logging with Rich console output.
"""

import logging
import sys
from pathlib import Path
from rich.console import Console
from rich.logging import RichHandler

console = Console()


def get_logger(name: str, log_file: str | Path | None = None) -> logging.Logger:
    """Get a configured logger with Rich console handler."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        return logger  # already configured

    # Console handler (Rich)
    console_handler = RichHandler(
        console=console,
        show_path=False,
        markup=True,
        rich_tracebacks=True,
    )
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
        )
        logger.addHandler(file_handler)

    return logger


def log_progress(current: int, total: int, label: str = "Progress") -> None:
    """Log a progress percentage to console."""
    pct = (current / total) * 100 if total else 0
    console.print(f"[cyan]{label}:[/cyan] {current}/{total} ({pct:.1f}%)")
