import pytest

from surepetcare.const import API_ENDPOINT_V1
from surepetcare.const import API_ENDPOINT_V2
from surepetcare.const import BATT_VOLTAGE_DIFF
from surepetcare.const import BATT_VOLTAGE_FULL
from surepetcare.const import BATT_VOLTAGE_LOW
from surepetcare.const import HEADER_TEMPLATE
from surepetcare.const import LOGIN_ENDPOINT
from surepetcare.const import REQUEST_TYPES
from surepetcare.const import USER_AGENT
from surepetcare.const import TIMEOUT


def test_constants():
    assert BATT_VOLTAGE_FULL == pytest.approx(1.6)
    assert BATT_VOLTAGE_LOW == pytest.approx(1.2)
    assert BATT_VOLTAGE_DIFF == pytest.approx(0.4)
    assert TIMEOUT == 10
    assert API_ENDPOINT_V1.startswith("https://")
    assert API_ENDPOINT_V2.startswith("https://")
    assert "auth/login" in LOGIN_ENDPOINT
    assert "surepy" in USER_AGENT
    assert "GET" in REQUEST_TYPES
    assert isinstance(HEADER_TEMPLATE, dict)
    assert "Authorization" in HEADER_TEMPLATE
