import pytest
from surepetcare.const import BATT_VOLTAGE_FULL, BATT_VOLTAGE_LOW, BATT_VOLTAGE_DIFF, TIMEOUT, API_ENDPOINT_V1, API_ENDPOINT_V2, LOGIN_ENDPOINT, SUREPY_USER_AGENT, REQUEST_TYPES, HEADER_TEMPLATE

def test_constants():
    assert BATT_VOLTAGE_FULL == pytest.approx(1.6)
    assert BATT_VOLTAGE_LOW == pytest.approx(1.2)
    assert BATT_VOLTAGE_DIFF == pytest.approx(0.4)
    assert TIMEOUT == 10
    assert API_ENDPOINT_V1.startswith("https://")
    assert API_ENDPOINT_V2.startswith("https://")
    assert "auth/login" in LOGIN_ENDPOINT
    assert "surepy" in SUREPY_USER_AGENT
    assert "GET" in REQUEST_TYPES
    assert isinstance(HEADER_TEMPLATE, dict)
    assert "Authorization" in HEADER_TEMPLATE
