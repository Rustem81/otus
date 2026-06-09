"""Prometheus custom metrics for MEXC P2P application."""

from __future__ import annotations

from prometheus_client import Counter, Gauge, Histogram

# P2P polling duration (seconds) — tracks how long each polling cycle takes
p2p_polling_duration_seconds = Histogram(
    "p2p_polling_duration_seconds",
    "Duration of P2P data polling cycle in seconds",
    buckets=(0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0),
)

# Active P2P ads gauge — current number of active advertisements
p2p_ads_active_total = Gauge(
    "p2p_ads_active_total",
    "Current number of active P2P advertisements",
    ["direction"],  # BUY or SELL
)

# Auth logins counter — total number of successful logins
auth_logins_total = Counter(
    "auth_logins_total",
    "Total number of successful authentication logins",
    ["method"],  # password or google
)
