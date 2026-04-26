"""
lightning.observability  -  In-memory metrics for the admin console.

No external dependencies. State is process-local: restart the server and
counters reset, which is correct for a research demo (and avoids the
operational complexity of Redis or sqlite for live numbers).

What's tracked
    - Process start time (uptime).
    - A ring buffer of the last N classifications (decision, latency,
      timestamp, artifact summary, regimes that fired).
    - A rolling latency window (timestamp, latency_ms) bounded by minutes
      of wall-clock — used to compute the avg-latency tile and the
      performance chart.

Thread-safety
    All mutations and reads acquire a single threading.Lock. FastAPI workers
    that share a process all see the same counters; multi-worker uvicorn
    will produce per-worker counters (acceptable for the demo).
"""
from __future__ import annotations

import os
import resource
import threading
import time
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Literal


@dataclass
class DecisionRecord:
    decision:      Literal["ALLOW", "REFUSE", "ESCALATE"]
    latency_ms:    float
    timestamp:     float                # epoch seconds
    summary:       str                  # short artifact preview (<= 80 chars)
    regimes_fired: list[str]


class AppMetrics:
    """Process-wide, thread-safe metrics for the live admin tiles."""

    def __init__(self,
                 max_recent: int = 100,
                 latency_window_minutes: int = 30):
        self._lock      = threading.Lock()
        self._start     = time.time()
        self._recent    = deque(maxlen=max_recent)
        self._latencies = deque()                       # (timestamp, ms)
        self._latency_window_s = latency_window_minutes * 60

    # -- recording -----------------------------------------------------------
    def record(self,
               *,
               decision:      str,
               latency_ms:    float,
               summary:       str,
               regimes_fired: list[str]) -> None:
        now = time.time()
        rec = DecisionRecord(
            decision=decision,
            latency_ms=float(latency_ms),
            timestamp=now,
            summary=summary[:80],
            regimes_fired=list(regimes_fired or []),
        )
        with self._lock:
            self._recent.appendleft(rec)
            self._latencies.append((now, float(latency_ms)))
            cutoff = now - self._latency_window_s
            while self._latencies and self._latencies[0][0] < cutoff:
                self._latencies.popleft()

    # -- reads ---------------------------------------------------------------
    def status(self,
               rules_loaded:   int,
               active_regimes: int) -> dict:
        now = time.time()
        uptime_s = int(now - self._start)
        h, rem = divmod(uptime_s, 3600)
        m = rem // 60

        # Memory: ru_maxrss is KB on Linux, bytes on macOS/BSD.
        rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        memory_mb = rss / (1024 * 1024) if os.uname().sysname == "Darwin" \
                    else rss / 1024

        with self._lock:
            samples = list(self._latencies)

        avg_ms = sum(ms for _, ms in samples) / len(samples) if samples else 0.0
        p95_ms = _percentile([ms for _, ms in samples], 95) if samples else 0.0

        return {
            "uptime_seconds": uptime_s,
            "uptime_hours":   h,
            "uptime_minutes": m,
            "started_at":     self._start,
            "rules_loaded":   rules_loaded,
            "active_regimes": active_regimes,
            "memory_mb":      round(memory_mb, 1),
            "avg_response_ms": round(avg_ms, 1),
            "p95_response_ms": round(p95_ms, 1),
            "calls_in_window": len(samples),
        }

    def recent(self, n: int = 10) -> list[dict]:
        with self._lock:
            items = list(self._recent)[:n]
        return [
            {
                "decision":      r.decision,
                "latency_ms":    round(r.latency_ms, 1),
                "timestamp":     r.timestamp,
                "summary":       r.summary,
                "regimes_fired": r.regimes_fired,
            }
            for r in items
        ]

    def performance(self,
                    buckets:        int = 30,
                    window_minutes: int = 30) -> dict:
        """Bucketed avg latency over the last `window_minutes`.

        Returns a list of {t, avg_ms, n} dicts.  `avg_ms` is None for empty
        buckets so the chart can render gaps.
        """
        now    = time.time()
        window = window_minutes * 60
        size   = window / buckets
        cutoff = now - window

        with self._lock:
            samples = [(t, ms) for t, ms in self._latencies if t >= cutoff]

        out = []
        for i in range(buckets):
            t_start = cutoff + i * size
            t_end   = t_start + size
            in_b    = [ms for t, ms in samples if t_start <= t < t_end]
            avg     = sum(in_b) / len(in_b) if in_b else None
            out.append({
                "t":      int(t_start),
                "avg_ms": round(avg, 1) if avg is not None else None,
                "n":      len(in_b),
            })

        return {
            "buckets":         out,
            "window_minutes":  window_minutes,
            "total_samples":   len(samples),
        }


# -- helpers ----------------------------------------------------------------
def _percentile(values: list[float], pct: int) -> float:
    if not values:
        return 0.0
    s = sorted(values)
    k = int(len(s) * pct / 100)
    return s[min(k, len(s) - 1)]


def count_rules(rules_dir: Path | None = None) -> int:
    """Count .lp rule files under reasoning/rules/."""
    if rules_dir is None:
        rules_dir = Path(__file__).resolve().parent / "reasoning" / "rules"
    if not rules_dir.exists():
        return 0
    return sum(1 for _ in rules_dir.rglob("*.lp"))


def count_active_regimes(rules_dir: Path | None = None) -> int:
    """Count distinct regime directories (everything under rules/ except _common)."""
    if rules_dir is None:
        rules_dir = Path(__file__).resolve().parent / "reasoning" / "rules"
    if not rules_dir.exists():
        return 0
    return sum(
        1 for d in rules_dir.iterdir()
        if d.is_dir() and not d.name.startswith("_")
    )


# -- module-level singleton --------------------------------------------------
metrics = AppMetrics()
