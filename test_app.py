# test_app.py — tests that don't require a database connection
# (health and version endpoints only)
# NOTE: In production CI, you'd spin up a test postgres and test the DB endpoints too.
import app

client = app.app.test_client()


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "healthy"}


def test_version():
    response = client.get("/version")
    assert response.status_code == 200
    assert response.get_json()["version"] == "4.0.0"
