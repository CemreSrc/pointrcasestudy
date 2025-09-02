import pytest
from fastapi.testclient import TestClient
from app.main import app
from sqlmodel import SQLModel


@pytest.fixture(scope="function")
def client():
    # Use in-memory sqlite for tests and ensure app uses the same engine
    from sqlmodel import create_engine
    from sqlalchemy.pool import StaticPool
    test_engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    from app import db as dbmodule
    dbmodule.engine = test_engine
    # initialize metadata on this engine
    SQLModel.metadata.drop_all(test_engine)
    SQLModel.metadata.create_all(test_engine)
    # Use TestClient as context manager to trigger FastAPI startup/shutdown
    with TestClient(app) as c:
        yield c


def test_site_crud(client):
    # create
    resp = client.post("/sites", json={"name": "Hospital", "description": "Main campus"})
    assert resp.status_code == 201
    site = resp.json()
    # retrieve
    resp = client.get(f"/sites/{site['id']}")
    assert resp.status_code == 200
    # delete
    resp = client.delete(f"/sites/{site['id']}")
    assert resp.status_code == 204
    # get missing
    resp = client.get(f"/sites/{site['id']}")
    assert resp.status_code == 404


def test_building_crud_with_site(client):
    # need a site first
    site = client.post("/sites", json={"name": "Campus"}).json()
    # create building
    resp = client.post("/buildings", json={"name": "Block A", "site_id": site["id"]})
    assert resp.status_code == 201
    building = resp.json()
    # retrieve
    assert client.get(f"/buildings/{building['id']}").status_code == 200
    # delete
    assert client.delete(f"/buildings/{building['id']}").status_code == 204


def test_building_create_without_site_should_fail(client):
    resp = client.post("/buildings", json={"name": "Orphan", "site_id": 999})
    assert resp.status_code == 400


def test_import_levels_single_and_multiple(client):
    # prepare site and building
    site = client.post("/sites", json={"name": "S1"}).json()
    building = client.post("/buildings", json={"name": "B1", "site_id": site["id"]}).json()

    # multiple levels
    levels_payload = [
        {"name": "Ground", "number": 0, "building_id": building["id"]},
        {"name": "First", "number": 1, "building_id": building["id"]},
    ]
    resp = client.post("/levels", json=levels_payload)
    assert resp.status_code == 201
    levels = resp.json()
    assert len(levels) == 2

    # invalid building in levels
    resp = client.post("/levels", json=[{"name": "Bad", "number": 2, "building_id": 9999}])
    assert resp.status_code == 400
