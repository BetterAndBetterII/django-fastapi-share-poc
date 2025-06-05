import os
import sys
import subprocess
import time
import pytest

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")

import django
from django.contrib.auth import get_user_model
from django.test import Client
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from fastapi_app.main import app

@pytest.fixture(scope="session", autouse=True)
def setup_django():
    django.setup()
    from django.core.management import call_command
    call_command("migrate", run_syncdb=True, verbosity=0)
    User = get_user_model()
    if not User.objects.filter(username="alice").exists():
        User.objects.create_user(username="alice", password="password")

@pytest.fixture(scope="session", autouse=True)
def redis_server():
    proc = subprocess.Popen(["redis-server", "--port", "6379", "--save", ""], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # wait for redis to start
    time.sleep(0.5)
    yield
    proc.terminate()
    proc.wait()

@pytest.fixture()
def django_client():
    return Client()

@pytest.fixture()
def fastapi_client():
    return TestClient(app)


def test_login_get(django_client):
    resp = django_client.get("/login/")
    assert resp.status_code == 200


def test_invalid_login(django_client):
    resp = django_client.post("/login/", {"username": "alice", "password": "wrong"})
    assert resp.status_code == 400


def test_session_shared(django_client, fastapi_client):
    resp = django_client.post("/login/", {"username": "alice", "password": "password"})
    assert resp.status_code in (302, 200)
    sessionid = resp.cookies["sessionid"].value

    whoami = django_client.get("/whoami/", cookies={"sessionid": sessionid})
    assert whoami.json() == {"username": "alice"}

    fast_resp = fastapi_client.get("/whoami", cookies={"sessionid": sessionid})
    assert fast_resp.json() == {"username": "alice"}
