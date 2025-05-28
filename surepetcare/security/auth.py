import logging
from http import HTTPStatus
from typing import Optional
from uuid import uuid1

import aiohttp

from surepetcare.const import HEADER_TEMPLATE
from surepetcare.const import LOGIN_ENDPOINT
from surepetcare.const import SUREPY_USER_AGENT
from surepetcare.security.exceptions import AuthenticationError

logger = logging.getLogger(__name__)


class AuthClient:
    def __init__(self):
        self._token = None
        self.session = None
        self._device_id = None
        self._surepy_version = None

    async def login(
        self,
        email: str | None = None,
        password: str | None = None,
        token: str | None = None,
        device_id: str | None = None,
    ) -> "AuthClient":
        await self.set_session()

        if token and device_id:
            # If token is provided, use it directly
            self._token = token
            self._device_id = device_id
            authentication_data = {"token": token, "device_id": device_id}
            authentication_data = {}
            return
        elif email and password:
            device_id = device_id if device_id else str(uuid1())
            self._device_id = device_id
            authentication_data: dict[str, str | None] = dict(
                email_address=email, password=password, device_id=device_id
            )
        else:
            raise AuthenticationError(
                "Email and password or token and device_id must be provided"
            )

        async with self.session.request(
            "POST",
            LOGIN_ENDPOINT,
            json=authentication_data,
            headers=self._generate_headers(),
        ) as response:
            logger.info(f"Response status: {response.status}")

            if response.status == HTTPStatus.OK:
                self._token = (await response.json()).get("data").get("token")
                if not self._token:
                    raise Exception("Token not found in response")

                return self
            else:
                raise AuthenticationError(
                    f"Authentication error {response.status} {await response.json()}"
                )

    def _generate_headers(self, token: Optional[str] = None) -> dict[str, str]:
        """Build a HTTP header accepted by the API"""
        user_agent = SUREPY_USER_AGENT.format(version=None)

        return get_formatted_header(
            token=token, user_agent=user_agent if user_agent else SUREPY_USER_AGENT, device_id=self._device_id
        )

    async def close(self):
        if self.session:
            logger.info("Closing session")
            await self.session.close()

    async def set_session(self) -> None:
        if not self.session:
            self.session = aiohttp.ClientSession()

    def get_token(self):
        if not self._token:
            raise Exception("Authentication token is missing")
        return self._token


def get_formatted_header(user_agent, token, device_id):
    formatted_header = {
        key: value.format(user_agent=user_agent, token=token, device_id=device_id)
        for key, value in HEADER_TEMPLATE.items()
    }
    return formatted_header
