from datetime import datetime
from pathlib import Path


def create_run_dir(bundle_dir: Path) -> Path:
    """
    Create a unique timestamped run folder inside runs/.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = Path("runs") / f"{timestamp}_{bundle_dir.name}"
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir