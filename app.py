import os
import random
import time

from flask import Flask, Response, jsonify, request
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Histogram,
    generate_latest,
)


app = Flask(__name__)


# ============================================================
# Application configuration
# ============================================================

APP_VERSION = os.getenv("APP_VERSION", "v1.0")
ROLLOUT_REVISION = os.getenv("ROLLOUT_REVISION", "unknown")

# Probability of returning HTTP 500.
# Example:
#   0.0 = 0%
#   0.2 = 20%
FAILURE_RATE = float(os.getenv("FAILURE_RATE", "0"))

# Normal request latency.
BASE_LATENCY_MS = float(os.getenv("BASE_LATENCY_MS", "20"))
JITTER_MS = float(os.getenv("JITTER_MS", "10"))

# Slow request injection.
# Example:
#   SLOW_REQUEST_RATE=0.05 -> 5% of requests are slow
#   SLOW_LATENCY_MS=500    -> slow requests take about 500 ms
SLOW_REQUEST_RATE = float(os.getenv("SLOW_REQUEST_RATE", "0"))
SLOW_LATENCY_MS = float(os.getenv("SLOW_LATENCY_MS", "500"))


# ============================================================
# Prometheus metrics
# ============================================================

REQUESTS = Counter(
    "demo_http_requests_total",
    "Total HTTP requests handled by the demo application",
    [
        "method",
        "path",
        "status",
        "app_version",
        "rollout_revision",
    ],
)


LATENCY = Histogram(
    "demo_http_request_duration_seconds",
    "HTTP request duration in seconds",
    [
        "method",
        "path",
        "app_version",
        "rollout_revision",
    ],
    buckets=(
        0.01,
        0.025,
        0.05,
        0.1,
        0.2,
        0.3,
        0.5,
        1,
        2,
        5,
    ),
)


# ============================================================
# Request handling
# ============================================================

def _recorded_response(path: str):
    start = time.perf_counter()

    # --------------------------------------------------------
    # Latency injection
    #
    # Most requests use the normal latency:
    #   BASE_LATENCY_MS + random jitter
    #
    # A configurable percentage of requests use:
    #   SLOW_LATENCY_MS
    #
    # Example:
    #   SLOW_REQUEST_RATE=0.05
    #   SLOW_LATENCY_MS=500
    #
    # approximately:
    #   95% -> 20-30 ms
    #    5% -> 500 ms
    # --------------------------------------------------------

    is_slow_request = random.random() < SLOW_REQUEST_RATE

    if is_slow_request:
        latency_ms = SLOW_LATENCY_MS
    else:
        latency_ms = max(
            0,
            BASE_LATENCY_MS + random.uniform(0, JITTER_MS),
        )

    time.sleep(latency_ms / 1000)


    # --------------------------------------------------------
    # Failure injection
    #
    # This is intentionally independent from slow requests.
    #
    # A slow request can still return HTTP 200.
    # --------------------------------------------------------

    if random.random() < FAILURE_RATE:
        status = 500

        body = {
            "message": "simulated failure",
            "version": APP_VERSION,
        }

    else:
        status = 200

        body = {
            "message": "GitOps canary demo",
            "version": APP_VERSION,
            "rollout_revision": ROLLOUT_REVISION,
            "latency_ms": round(latency_ms, 2),
            "slow_request": is_slow_request,
        }


    # --------------------------------------------------------
    # Measure the actual request duration
    # --------------------------------------------------------

    elapsed = time.perf_counter() - start


    # --------------------------------------------------------
    # Prometheus labels
    # --------------------------------------------------------

    labels = {
        "method": request.method,
        "path": path,
        "app_version": APP_VERSION,
        "rollout_revision": ROLLOUT_REVISION,
    }


    # --------------------------------------------------------
    # Record Prometheus metrics
    # --------------------------------------------------------

    REQUESTS.labels(
        status=str(status),
        **labels,
    ).inc()

    LATENCY.labels(
        **labels,
    ).observe(elapsed)


    return jsonify(body), status


# ============================================================
# Application endpoints
# ============================================================

@app.get("/")
def root():
    return _recorded_response("/")


@app.get("/api/work")
def work():
    return _recorded_response("/api/work")


@app.get("/healthz")
def healthz():
    return jsonify(
        status="ok",
        version=APP_VERSION,
    ), 200


@app.get("/readyz")
def readyz():
    return jsonify(
        status="ready",
        version=APP_VERSION,
    ), 200


@app.get("/metrics")
def metrics():
    return Response(
        generate_latest(),
        mimetype=CONTENT_TYPE_LATEST,
    )


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
    )