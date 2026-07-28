import os
import random
import time
from flask import Flask, Response, jsonify, request
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

app = Flask(__name__)

APP_VERSION = os.getenv("APP_VERSION", "v1.0")
ROLLOUT_REVISION = os.getenv("ROLLOUT_REVISION", "unknown")
FAILURE_RATE = float(os.getenv("FAILURE_RATE", "0"))
BASE_LATENCY_MS = float(os.getenv("BASE_LATENCY_MS", "20"))
JITTER_MS = float(os.getenv("JITTER_MS", "10"))

REQUESTS = Counter(
    "demo_http_requests_total",
    "Total HTTP requests handled by the demo application",
    ["method", "path", "status", "app_version", "rollout_revision"],
)
LATENCY = Histogram(
    "demo_http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "path", "app_version", "rollout_revision"],
    buckets=(0.01, 0.025, 0.05, 0.1, 0.2, 0.3, 0.5, 1, 2, 5),
)


def _recorded_response(path: str):
    start = time.perf_counter()
    latency_ms = max(0, BASE_LATENCY_MS + random.uniform(0, JITTER_MS))
    time.sleep(latency_ms / 1000)

    if random.random() < FAILURE_RATE:
        status = 500
        body = {"message": "simulated failure", "version": APP_VERSION}
    else:
        status = 200
        body = {
            "message": "GitOps canary demo",
            "version": APP_VERSION,
            "rollout_revision": ROLLOUT_REVISION,
            "latency_ms": round(latency_ms, 2),
        }

    elapsed = time.perf_counter() - start
    labels = {
        "method": request.method,
        "path": path,
        "app_version": APP_VERSION,
        "rollout_revision": ROLLOUT_REVISION,
    }
    REQUESTS.labels(status=str(status), **labels).inc()
    LATENCY.labels(**labels).observe(elapsed)
    return jsonify(body), status


@app.get("/")
def root():
    return _recorded_response("/")


@app.get("/api/work")
def work():
    return _recorded_response("/api/work")


@app.get("/healthz")
def healthz():
    return jsonify(status="ok", version=APP_VERSION), 200


@app.get("/readyz")
def readyz():
    return jsonify(status="ready", version=APP_VERSION), 200


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    app.run(port=5000)
