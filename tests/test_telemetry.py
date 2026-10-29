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
