import logging
import warnings
from http import HTTPStatus
from uuid import uuid1

import aiohttp

from .cache import CacheHeaders
from .exceptions import AuthenticationError
from surepetcare.const import HEADER_TEMPLATE
from surepetcare.const import LOGIN_ENDPOINT
from surepetcare.const import USER_AGENT

logger = logging.getLogger(__name__)


class AuthClient(CacheHeaders):
    def __init__(self):
        self._token = None
        self.session = None
        self._device_id = None

    async def login(
        self,
        email: str | None = None,
        password: str | None = None,
        token: str | None = None,
        device_id: str | None = None,
    ) -> "AuthClient":
        await self.set_session()
        self.clear_resources()

        if token and device_id:
            # If token is provided, use it directly

            logger.info("Using provided token and device_id for authentication")
            self._token = token
            self._device_id = device_id
            return self
        elif email and password:
            logger.info("Using email and password for authentication")
            device_id = device_id if device_id else str(uuid1())
            self._device_id = device_id
            authentication_data: dict[str, str | None] = dict(
                email_address=email, password=password, device_id=device_id
            )
        else:
            raise AuthenticationError("Email and password or token and device_id must be provided")

        async with self.session.request(
            "POST",
            LOGIN_ENDPOINT,
            json=authentication_data,
            headers=self._generate_headers(),
        ) as response:
            if response.status == HTTPStatus.OK:
                self._token = (await response.json()).get("data").get("token")
                if not self._token:
                    raise Exception("Token not found in response")

                return self
            else:
                raise AuthenticationError(f"Authentication error {response.status} {await response.json()}")

    def _generate_headers(self, token=None, headers={}):
        """Build a HTTP header accepted by the API"""
        user_agent = USER_AGENT.format(version=None)

        headers = get_formatted_header(
            token=token if token is not None else self._token,
            user_agent=user_agent if user_agent else USER_AGENT,
            device_id=self._device_id,
        )
        all_headers = headers | headers
        return all_headers

    async def close(self):
        if self.session:
            logger.info("Closing session")
            await self.session.close()

    async def set_session(self) -> None:
        if not self.session or self.session.closed:
            self.session = aiohttp.ClientSession()

    @property
    def token(self):
        if not self._token:
            raise Exception("Authentication token is missing")
        return self._token

    @property
    def device_id(self):
        if not self._device_id:
            raise Exception("Device ID is missing")
        return self._device_id

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()

    def __del__(self):
        if self.session is not None and not self.session.closed:
            warnings.warn(
                f"{self.__class__.__name__} was deleted without closing the aiohttp session. "
                "Call await client.close() or use 'async with' to avoid resource leaks.",
                ResourceWarning,
            )


def get_formatted_header(user_agent=None, token=None, device_id=None):
    formatted_header = {
        key: value.format(user_agent=user_agent, token=token, device_id=device_id)
        for key, value in HEADER_TEMPLATE.items()
    }
    return formatted_header
