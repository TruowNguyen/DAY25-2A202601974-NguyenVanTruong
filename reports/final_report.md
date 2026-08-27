# Day 25 Reliability Final Report

## 1. Architecture summary

```text
User -> Gateway -> Cache -> Circuit breaker: primary -> Provider primary
                    cache miss -> Circuit breaker: backup -> Provider backup
                                                    -> Static degraded response
```

The gateway checks cache first, then uses independently protected providers in order. Provider failures and open circuits advance to the fallback; a static response is the last safe path.

## 2. Configuration

| Setting | Value | Rationale |
|---|---:|---|
| failure threshold | 3 | Opens only after repeated failures to avoid transient-error overreaction. |
| reset timeout | 2 s | Limits retry storms while allowing quick probes for recovery. |
| success threshold | 1 | A successful probe restores this lab's fake provider immediately. |
| cache TTL | 300 s | Reuses stable answers while bounding staleness. |
| similarity threshold | 0.92 | Conservative semantic matching; year/ID mismatches are rejected. |
| requests/scenario | 100 | Provides a repeatable chaos sample. |

## 3. Metrics summary

| Metric | Value |
|---|---:|
| total_requests | 300 |
| availability | 0.9867 |
| error_rate | 0.0133 |
| latency_p50_ms | 279.61 |
| latency_p95_ms | 314.73 |
| latency_p99_ms | 320.29 |
| fallback_success_rate | 0.9524 |
| cache_hit_rate | 0.6167 |
| circuit_open_count | 10 |
| recovery_time_ms | 2481.771469116211 |
| estimated_cost | 0.047374 |
| estimated_cost_saved | 0.185 |

## 4. Chaos scenarios

| Scenario | Status |
|---|---|
| primary_timeout_100 | pass |
| primary_flaky_50 | pass |
| all_healthy | pass |

## 5. Cache comparison

| Metric | Without cache | With cache |
|---|---:|---:|
| latency P50 (ms) | 270.21 | 279.61 |
| latency P95 (ms) | 315.68 | 314.73 |
| estimated cost | 0.130178 | 0.047374 |
| cache hit rate | 0.0 | 0.6167 |

## 6. Redis shared cache

Redis stores hashed query keys with a TTL, so independent gateway instances can share responses. The automated `test_shared_state_across_instances` test passed against the local Redis container.

## 7. Failure analysis

This implementation keeps circuit state in process memory. In a multi-instance deployment, a failing provider could receive traffic from instances whose breakers have not opened. Store breaker counters and transitions in Redis and add distributed probe coordination before production.

## 8. Next steps

1. Add Redis-backed circuit-breaker state and a single-probe lease.
2. Add per-user rate limits and structured tracing.
3. Evaluate cache quality with labelled false-hit test data.