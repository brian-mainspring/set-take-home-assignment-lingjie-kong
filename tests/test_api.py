"""
API tests for the Smart Garden Hub.

One example test is provided to show the pattern. Add your own tests below.
"""

from tests.conftest import BASE_URL

EXPECTED_CONTROLLERS = {"tc", "hc", "lc", "sc", "fm"}


def test_list_controllers_returns_all_peripherals(hub_client):
    """All five peripheral controllers must be registered with the hub."""
    response = hub_client.get(f"{BASE_URL}/controllers")

    assert response.status_code == 200

    controllers = response.json()
    assert isinstance(controllers, list)

    names = {c["name"] for c in controllers}
    assert names == EXPECTED_CONTROLLERS


# Add your tests below.
