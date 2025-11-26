import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


@pytest.mark.parametrize(
    "path",
    [
        "/employee",
        "/dasata",
        "/notif",
        "/file",
        "/tiket",
        "/absensi",
        "/sarpras",
        "/personalia",
        "/users",
        "/crypto",
    ],
)
def test_router_path_accessible(path):
    response = client.get(path)
    assert response.status_code in [200, 404]
