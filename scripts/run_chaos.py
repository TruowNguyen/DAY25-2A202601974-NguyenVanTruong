from __future__ import annotations

import argparse

from reliability_lab.chaos import load_queries, run_simulation
from reliability_lab.config import load_config


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/default.yaml")
    parser.add_argument("--out", default="reports/metrics.json")
    parser.add_argument("--csv-out", help="Optional CSV export path for the same run")
    parser.add_argument("--disable-cache", action="store_true", help="Run a no-cache baseline for comparison")
    args = parser.parse_args()
    config = load_config(args.config)
    if args.disable_cache:
        config.cache.enabled = False
    metrics = run_simulation(config, load_queries())
    metrics.write_json(args.out)
    if args.csv_out:
        metrics.write_csv(args.csv_out)
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
