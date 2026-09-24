import json
import time
from pathlib import Path
from typing import Callable

import config


def cached_json(name: str, fetch: Callable[[], object], max_age_hours: float = 24):
    """Return fetch() result, cached under .cache/ for max_age_hours."""
    path: Path = config.CACHE_DIR / f"{name}.json"
    if path.exists() and time.time() - path.stat().st_mtime < max_age_hours * 3600:
        return json.loads(path.read_text())
    data = fetch()
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(data))
    return data
