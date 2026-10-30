"""
API tests for the Smart Garden Hub.

One example test is provided to show the pattern. Add your own tests below.
"""

from tests.conftest import BASE_URL
import pytest

EXPECTED_CONTROLLERS = {"tc", "hc", "lc", "sc", "fm", "co2"}


def test_list_controllers_returns_all_peripherals(hub_client):
    """All five peripheral controllers must be registered with the hub."""
    response = hub_client.get(f"{BASE_URL}/controllers")

    assert response.status_code == 200

    controllers = response.json()
    assert isinstance(controllers, list)

    names = {c["name"] for c in controllers}
    assert names == EXPECTED_CONTROLLERS

# Add your tests below.
def test_initial_state(hub_client):
    response = hub_client.get(f"{BASE_URL}/status")
    assert response.status_code == 200

    data = response.json()
    assert data["state"] == 'ACTIVE'
    assert data["cycle"] == 0
    assert data["battery_remaining_pct"] == 100.0
    assert data["orchid_alive"] is True

@pytest.mark.parametrize("name", ["tc", "hc", "lc", "sc", "fm", "co2"])
def test_advance_cycle(hub_client, name):
    before = hub_client.get(f"{BASE_URL}/telemetry").json()
    
    response = hub_client.post(f"{BASE_URL}/cycle")
    assert response.status_code == 200
    
    after = hub_client.get(f"{BASE_URL}/telemetry").json()
    
    assert after["cycle"] == before["cycle"] + 1

    key = f"{name}_heartbeat"
    assert after["signals"][key] == before["signals"][key] + 1

def test_reset(hub_client):
    for _ in range(10):
        response = hub_client.post(f"{BASE_URL}/cycle")
        assert response.status_code == 200
    
    response = hub_client.post(f"{BASE_URL}/reset")
    assert response.status_code == 200
    
    data = hub_client.get(f"{BASE_URL}/telemetry").json()
    assert data["cycle"] == 0
    
def test_co2_telemetry(hub_client):
    response = hub_client.get(f"{BASE_URL}/telemetry")
    assert response.status_code == 200

    signals = response.json()["signals"]

    assert "co2_heartbeat" in signals
    assert "co2_ppm" in signals
    assert 400 <= signals["co2_ppm"] <= 2000