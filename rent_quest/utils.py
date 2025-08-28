from __future__ import annotations

import os


def ensure_directory(path: str) -> None:
    """Create the directory if it doesn't exist."""
    if not path:
        return
    os.makedirs(path, exist_ok=True)

