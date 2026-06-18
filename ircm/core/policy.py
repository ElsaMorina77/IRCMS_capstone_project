from functools import lru_cache
from pathlib import Path
from typing import Any, Dict

import yaml


DEFAULT_REFERENCE_DATE = "2026-06-18"


@lru_cache(maxsize=1)
def load_policy_pack() -> Dict[str, Any]:
    policy_path = Path(__file__).resolve().parents[1] / "policies" / "rules.yaml"

    if not policy_path.exists():
        return {}

    with policy_path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file) or {}

    return data if isinstance(data, dict) else {}


def get_policy_value(*keys: str, default=None):
    current: Any = load_policy_pack()

    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]

    return current


def load_bundle_manifest(bundle_dir: Path) -> Dict[str, Any]:
    manifest_path = Path(bundle_dir) / "manifest.yaml"

    if not manifest_path.exists():
        return {}

    with manifest_path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file) or {}

    return data if isinstance(data, dict) else {}


def resolve_reference_date(bundle_dir: Path) -> str:
    manifest = load_bundle_manifest(bundle_dir)
    manifest_reference_date = manifest.get("reference_date")

    if manifest_reference_date:
        return str(manifest_reference_date)

    return str(
        get_policy_value(
            "runtime",
            "reference_date",
            default=DEFAULT_REFERENCE_DATE,
        )
    )
