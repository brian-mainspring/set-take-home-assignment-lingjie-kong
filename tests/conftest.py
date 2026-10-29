"""
Test fixtures for the Smart Garden Hub test suite.

The GardenHub server is started once per test session in a background thread.
Individual tests interact with it exclusively through HTTP — no direct imports
of hub internals.

Two fixtures are provided as a starting point. Add your own below.
"""

import threading
import time

import pytest
import requests

from garden_hub import app

BASE_URL = "http://localhost:5001"


@pytest.fixture(scope="session")
def garden_server():
    """
    Start the GardenHub Flask server once for the entire test session.

    Runs in a daemon thread so it exits automatically when the process ends.
    Blocks until the server is accepting connections before yielding.
    """
    thread = threading.Thread(
        target=lambda: app.run(port=5001, debug=False, use_reloader=False),
        daemon=True,
    )
    thread.start()

    deadline = time.time() + 5.0
    while time.time() < deadline:
        try:
            requests.get(f"{BASE_URL}/status", timeout=0.5)
            break
        except requests.ConnectionError:
            time.sleep(0.1)

    yield


@pytest.fixture(scope="session")
def hub_client(garden_server):
    """
    A requests.Session pointed at the running GardenHub server.

    Example usage:

        def test_something(hub_client):
            response = hub_client.get(f"{BASE_URL}/status")
            assert response.status_code == 200
            data = response.json()
            assert "state" in data
    """
    return requests.Session()


# Add your own fixtures below.
