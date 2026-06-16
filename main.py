"""
Command-line entry point for IRCMS.
"""

import argparse
import sys
from pathlib import Path

from ircm.core.file_utils import create_run_dir


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the Intelligent Regulatory Change Management System pipeline."
    )

    parser.add_argument(
        "--bundle",
        required=True,
        help="Path to the scenario bundle folder to process.",
    )

    return parser.parse_args()


def main() -> int:
    print("IRCMS project started.")

    args = parse_args()
    bundle_dir = Path(args.bundle)

    try:
        if not bundle_dir.exists() or not bundle_dir.is_dir():
            print(f"Error: Bundle folder does not exist: {bundle_dir}", file=sys.stderr)
            return 1

        run_dir = create_run_dir(bundle_dir)

        print(f"Selected bundle: {bundle_dir}")
        print(f"Run directory: {run_dir}")

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