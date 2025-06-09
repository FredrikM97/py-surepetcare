BATT_VOLTAGE_FULL = 1.6
BATT_VOLTAGE_LOW = 1.2
BATT_VOLTAGE_DIFF = BATT_VOLTAGE_FULL - BATT_VOLTAGE_LOW

TIMEOUT = 10
# https://app-api.beta.surehub.io/api/v2"
API_ENDPOINT_V1 = "https://app.api.surehub.io/api"
API_ENDPOINT_V2 = "https://app.api.surehub.io/api/v2"
API_ENDPOINT_PRODUCTION = "https://app-api.production.surehub.io/api"
LOGIN_ENDPOINT = f"{API_ENDPOINT_PRODUCTION}/auth/login"

USER_AGENT = "version {version} https://github.com/FredrikM97/py-surepetcare"
REQUEST_TYPES = ["GET", "PUT", "POST", "DELETE"]

HEADER_TEMPLATE = {
    "Host": "app-api.production.surehub.io",
    "Connection": "keep-alive",
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "sv",
    "User-Agent": "{user_agent}",
    "X-Requested-With": "com.sureflap.surepetcare",
    "X-Device-Id": "{device_id}",
    "Authorization": "Bearer {token}",
    "Origin": "https://www.surepetcare.io",
    "Referer": "https://www.surepetcare.io/",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "cross-site",
    "sec-fetch-dest": "empty",
    "sec-ch-ua": '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "spc-client-type": "react",
    "dnt": "1",
    "priority": "u=1, i",
}
