import app as app_module
import pytest


@pytest.fixture()
def client(monkeypatch):
    monkeypatch.setattr(app_module, "FAILURE_RATE", 0.0)
    monkeypatch.setattr(app_module, "BASE_LATENCY_MS", 0.0)
    monkeypatch.setattr(app_module, "JITTER_MS", 0.0)
    app_module.app.config.update(TESTING=True)
    return app_module.app.test_client()


def test_root_returns_version(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.get_json()["version"] == app_module.APP_VERSION


def test_health_and_readiness(client):
    assert client.get("/healthz").status_code == 200
    assert client.get("/readyz").status_code == 200


def test_metrics_exposed(client):
    client.get("/api/work")
    response = client.get("/metrics")
    assert response.status_code == 200
    assert b"demo_http_requests_total" in response.data
    assert b"demo_http_request_duration_seconds" in response.data


def test_failure_injection(monkeypatch):
    monkeypatch.setattr(app_module, "FAILURE_RATE", 1.0)
    monkeypatch.setattr(app_module, "BASE_LATENCY_MS", 0.0)
    monkeypatch.setattr(app_module, "JITTER_MS", 0.0)
    app_module.app.config.update(TESTING=True)
    client = app_module.app.test_client()
    assert client.get("/api/work").status_code == 500
