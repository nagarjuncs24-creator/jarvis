from fastapi.testclient import TestClient

from app.main import app


def test_health_response_has_security_headers() -> None:
    response = TestClient(app).get("/health")
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
