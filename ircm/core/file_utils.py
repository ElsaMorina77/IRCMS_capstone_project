from datetime import datetime
from pathlib import Path


def create_run_dir(bundle_dir: Path, run_id: str = None) -> Path:
    """
    Create a run folder inside runs/.
    """
    if run_id:
        run_dir = Path("runs") / run_id
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        run_dir = Path("runs") / f"{timestamp}_{bundle_dir.name}"

    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir
