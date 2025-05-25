BATT_VOLTAGE_FULL = 1.6
BATT_VOLTAGE_LOW = 1.2
BATT_VOLTAGE_DIFF = BATT_VOLTAGE_FULL - BATT_VOLTAGE_LOW

TIMEOUT = 10
# https://app-api.beta.surehub.io/api/v2"
API_ENDPOINT_V1 = "https://app.api.surehub.io/api"
API_ENDPOINT_V2 = "https://app.api.surehub.io/api/v2"
LOGIN_ENDPOINT = f"{API_ENDPOINT_V1}/auth/login"

SUREPY_USER_AGENT = "surepy {version} - https://github.com/benleb/surepy"
REQUEST_TYPES = ["GET", "PUT", "POST", "DELETE"]
HEADER_TEMPLATE = {
    "Host": "app.api.surehub.io",
    "Connection": "keep-alive",
    "Content-Type": "application/json",
    "Accept": '"application/json", "text/plain", */*',
    "Origin": "https://surepetcare.io",
    "User-Agent": "{user_agent}",
    "Referer": "https://surepetcare.io",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "en-US,en-GB;q=0.9",
    "X-Requested-With": "com.sureflap.surepetcare",
    "Authorization": "Bearer {token}",
    "X-Device-Id": "{device_id}",
}
