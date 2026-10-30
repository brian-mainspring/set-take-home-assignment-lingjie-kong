"""
Telemetry tests for the Smart Garden Hub.

GET /telemetry returns a snapshot structured as:
{
    "cycle": <int>,
    "signals": {
        "tc_heartbeat": <int>,   "tc_temperature": <float>, "tc_power_used": <float>,
        "hc_heartbeat": <int>,   "hc_humidity": <float>,    "hc_misting_active": <0|1>,
        "lc_heartbeat": <int>,   "lc_light_on": <0|1>,      "lc_hour_of_day": <int>,
        "sc_heartbeat": <int>,   "sc_moisture": <float>,    "sc_ph": <float>,
        "fm_heartbeat": <int>,   "fm_spore_count": <int>,
    }
}
"""

# Add your tests below.
from tests.conftest import BASE_URL
import pytest

def test_telemetry_structure(hub_client):
    response = hub_client.get(f"{BASE_URL}/telemetry")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data["cycle"], int)
    assert isinstance(data["signals"], dict)
    assert "tc_temperature" in data["signals"]
    assert "hc_humidity" in data["signals"]
    assert "fm_spore_count" in data["signals"]
    
def test_fungi_growth(hub_client):
    before = hub_client.get(f"{BASE_URL}/telemetry").json()

    response = hub_client.post(f"{BASE_URL}/cycle")
    assert response.status_code == 200

    after = hub_client.get(f"{BASE_URL}/telemetry").json()

    temperature = after["signals"]["tc_temperature"]

    before_spores = before["signals"]["fm_spore_count"]
    after_spores = after["signals"]["fm_spore_count"]

    if 25 <= temperature <= 26:
        assert after_spores == before_spores * 2
    else:
        assert after_spores == before_spores
    
def test_fungi_lethal_threshold(hub_client):
    for _ in range(100):
        response = hub_client.post(f"{BASE_URL}/cycle")
        assert response.status_code == 200

        telemetry = hub_client.get(f"{BASE_URL}/telemetry").json()
        spores = telemetry["signals"]["fm_spore_count"]

        if spores >= 512:
            orchid = hub_client.get(f"{BASE_URL}/orchid").json()
            assert orchid["alive"] is False
            break
    else:
        status = hub_client.get(f"{BASE_URL}/status").json()

        pytest.fail(
            f"Lethal threshold not reached."
            f"Spores={spores}, "
            f"Cycle={status['cycle']}, "
            f"State={status['state']}"
        )