#!/usr/bin/env python3
"""
Single entrypoint for the whole project workflow.

Stages:
1) preprocess_sensor_b
2) preprocess_sensor_a
3) compare_pair
4) full_report
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Dict

import yaml

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.analysis import compare_single_pair_from_config, run_full_report_from_config
from src.preprocessing import preprocess_adxl355, preprocess_setup5_keep_channels


def load_project_config(config_path: str = "configs/project.yaml") -> Dict[str, Any]:
    path = PROJECT_ROOT / config_path
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def run_pipeline(config_path: str = "configs/project.yaml", verbose: bool = True) -> None:
    cfg = load_project_config(config_path)
    pipe = cfg["pipeline"]
    stages = pipe.get("stages", {})

    sensor_a_raw = PROJECT_ROOT / pipe["sensor_a"]["raw_file"]
    sensor_a_out = PROJECT_ROOT / pipe["sensor_a"]["processed_file"]
    sensor_b_raw = PROJECT_ROOT / pipe["sensor_b"]["raw_file"]
    sensor_b_out = PROJECT_ROOT / pipe["sensor_b"]["processed_file"]

    # Read filter params from config
    filter_cfg = cfg.get("preprocessing", {}).get("filtering", {})
    filter_params = {
        "highpass_hz": float(filter_cfg.get("highpass_hz", 0.5)),
        "highpass_order": int(filter_cfg.get("highpass_order", 2)),
        "lowpass_hz": float(filter_cfg.get("lowpass_hz", 500)),
        "lowpass_order": int(filter_cfg.get("lowpass_order", 4)),
    }

    if stages.get("preprocess_sensor_b", True):
        b_opt = pipe["sensor_b"].get("preprocess", {})
        preprocess_adxl355(
            input_file=sensor_b_raw,
            output_file=sensor_b_out,
            apply_filter=bool(b_opt.get("apply_filter", True)),
            remove_dc_offset=bool(b_opt.get("remove_dc_offset", True)),
            timezone_offset_hours=int(b_opt.get("timezone_offset_hours", 0)),
            verbose=verbose,
            **filter_params,
        )

    if stages.get("preprocess_sensor_a", True):
        a_opt = pipe["sensor_a"].get("preprocess", {})
        preprocess_setup5_keep_channels(
            input_file=sensor_a_raw,
            output_file=sensor_a_out,
            apply_filter=bool(a_opt.get("apply_filter", True)),
            remove_dc=bool(a_opt.get("remove_dc", True)),
            convert_to_g=bool(a_opt.get("convert_to_g", True)),
            timezone_offset_hours=int(a_opt.get("timezone_offset_hours", 0)),
            verbose=verbose,
            **filter_params,
        )

    if stages.get("compare_pair", True):
        result = compare_single_pair_from_config(config_path)
        print("[compare] metrics:", result["metrics_path"])
        print("[compare] aligned:", result["aligned_path"])

    if stages.get("full_report", True):
        out = run_full_report_from_config(config_path)
        print("[report] report:", out["report_md"])
        print("[report] figures:", out["figures_dir"])


def main() -> None:
    parser = argparse.ArgumentParser(description="Single run entrypoint for the project.")
    parser.add_argument(
        "--config",
        default="configs/project.yaml",
        help="Path to unified project config (relative to project root).",
    )
    parser.add_argument("--quiet", action="store_true", help="Reduce logging output.")
    args = parser.parse_args()

    run_pipeline(config_path=args.config, verbose=not args.quiet)


if __name__ == "__main__":
    main()
