"""
Command-line entry point for IRCMS.

This file starts a single IRCMS pipeline run from a scenario bundle folder.
It does not contain agent logic, UI code, database code, or reporting logic.
Those responsibilities belong to the orchestrator and the agents that will be
built later.
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path


def parse_args() -> argparse.Namespace:
    """Read and return command-line arguments for the IRCMS run."""
    parser = argparse.ArgumentParser(
        description="Run the Intelligent Regulatory Change Management System pipeline."
    )

    parser.add_argument(
        "--bundle",
        required=True,
        help="Path to the scenario bundle folder to process.",
    )

    return parser.parse_args()


def create_run_dir(bundle_dir: Path) -> Path:
    """
    Create a timestamped run directory under runs/.

    The folder name includes the current timestamp and the selected bundle name
    so each run has a clear, unique location for future outputs.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = Path("runs") / f"{timestamp}_{bundle_dir.name}"
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def main() -> int:
    """Validate input, create the run folder, and start the orchestrator."""
    print("IRCMS project started.")

    args = parse_args()
    bundle_dir = Path(args.bundle)

    try:
        # The bundle must already exist because it contains the scenario input.
        if not bundle_dir.exists() or not bundle_dir.is_dir():
            print(f"Error: Bundle folder does not exist: {bundle_dir}", file=sys.stderr)
            return 1

        run_dir = create_run_dir(bundle_dir)

        print(f"Selected bundle: {bundle_dir}")
        print(f"Run directory: {run_dir}")

        # The orchestrator owns the actual multi-agent pipeline.
        # main.py only passes in the input bundle and the output run folder.
        from ircm.core.orchestrator import Orchestrator

        orchestrator = Orchestrator(bundle_dir=bundle_dir, run_dir=run_dir)
        orchestrator.run_pipeline()

        print("Pipeline completed.")
        return 0

    except Exception as error:
        print(f"Error: Pipeline failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())