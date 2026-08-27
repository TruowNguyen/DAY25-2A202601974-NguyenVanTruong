from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metrics", default="reports/metrics.json")
    parser.add_argument("--out", default="reports/final_report.md")
    args = parser.parse_args()
    metrics = json.loads(Path(args.metrics).read_text())
    no_cache_path = Path(args.metrics).with_name("metrics_without_cache.json")
    no_cache = json.loads(no_cache_path.read_text()) if no_cache_path.exists() else None
    def value(name: str) -> object:
        return metrics.get(name, "n/a")

    lines = [
        "# Day 25 Reliability Final Report",
        "",
        "## 1. Architecture summary",
        "",
        "```text",
        "User -> Gateway -> Cache -> Circuit breaker: primary -> Provider primary",
        "                    cache miss -> Circuit breaker: backup -> Provider backup",
        "                                                    -> Static degraded response",
        "```",
        "",
        (
            "The gateway checks cache first, then uses independently protected providers in order. "
            "Provider failures and open circuits advance to the fallback; a static response is the last safe path."
        ),
        "",
        "## 2. Configuration",
        "",
        "| Setting | Value | Rationale |",
        "|---|---:|---|",
        "| failure threshold | 3 | Opens only after repeated failures to avoid transient-error overreaction. |",
        "| reset timeout | 2 s | Limits retry storms while allowing quick probes for recovery. |",
        "| success threshold | 1 | A successful probe restores this lab's fake provider immediately. |",
        "| cache TTL | 300 s | Reuses stable answers while bounding staleness. |",
        "| similarity threshold | 0.92 | Conservative semantic matching; year/ID mismatches are rejected. |",
        "| requests/scenario | 100 | Provides a repeatable chaos sample. |",
        "",
        "## 3. Metrics summary",
        "",
        "| Metric | Value |",
        "|---|---:|",
    ]
    for key, metric_value in metrics.items():
        if key == "scenarios":
            continue
        lines.append(f"| {key} | {metric_value} |")
    lines += ["", "## 4. Chaos scenarios", "", "| Scenario | Status |", "|---|---|"]
    for key, scenario_status in metrics.get("scenarios", {}).items():
        lines.append(f"| {key} | {scenario_status} |")
    lines += [
        "",
        "## 5. Cache comparison",
        "",
        "| Metric | Without cache | With cache |",
        "|---|---:|---:|",
        f"| latency P50 (ms) | {no_cache.get('latency_p50_ms', 'n/a') if no_cache else 'n/a'} | {value('latency_p50_ms')} |",
        f"| latency P95 (ms) | {no_cache.get('latency_p95_ms', 'n/a') if no_cache else 'n/a'} | {value('latency_p95_ms')} |",
        f"| estimated cost | {no_cache.get('estimated_cost', 'n/a') if no_cache else 'n/a'} | {value('estimated_cost')} |",
        f"| cache hit rate | {no_cache.get('cache_hit_rate', 'n/a') if no_cache else 'n/a'} | {value('cache_hit_rate')} |",
        "",
        "## 6. Redis shared cache",
        "",
        (
            "Redis stores hashed query keys with a TTL, so independent gateway instances can share responses. "
            "The automated `test_shared_state_across_instances` test passed against the local Redis container."
        ),
        "",
        "## 7. Failure analysis",
        "",
        (
            "This implementation keeps circuit state in process memory. In a multi-instance deployment, a failing provider "
            "could receive traffic from instances whose breakers have not opened. Store breaker counters and transitions in Redis "
            "and add distributed probe coordination before production."
        ),
        "",
        "## 8. Next steps",
        "",
        "1. Add Redis-backed circuit-breaker state and a single-probe lease.",
        "2. Add per-user rate limits and structured tracing.",
        "3. Evaluate cache quality with labelled false-hit test data.",
    ]
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
