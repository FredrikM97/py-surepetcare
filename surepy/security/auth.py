import aiohttp
from typing import Tuple, Any
from surepy.const import API_ENDPOINT_V1, LOGIN_ENDPOINT, SUREPY_USER_AGENT, HEADER_TEMPLATE
from surepy.security.exceptions import AuthenticationError
from http import HTTPStatus
from uuid import uuid1
import logging

logger = logging.getLogger(__name__)

class AuthClient:
    def __init__(self):
        self._token:str = None
        self.session:str = None  
        self._device_id: str = str(uuid1())
        self._surepy_version: str | None 

    async def login(self, email, password) -> "AuthClient":

        await self.set_session()
        
        authentication_data: dict[str, str | None] = dict(
            email_address=email, 
            password=password,
            device_id=self._device_id
        )

        async with self.session.request(
                "POST",
                LOGIN_ENDPOINT,
                json=authentication_data,
                headers=self._generate_headers()
            ) as response:
                logger.info(f"Response status: {response.status}")
            
                if response.status == HTTPStatus.OK:
                    self._token = (await response.json()).get("data").get("token")
                    if not self._token:
                        raise Exception("Token not found in response")
                
                    return self
                else:
                    raise AuthenticationError(f"Authentication error {response.status} {await response.json()}")
            
    def _generate_headers(self, token:str=None) -> dict[str, str]:
        """Build a HTTP header accepted by the API"""
        user_agent = SUREPY_USER_AGENT.format(version=None)

        return get_formatted_header(
            token=token, 
            user_agent=user_agent if user_agent else SUREPY_USER_AGENT,
            device_id=self._device_id
        )
            
    async def close(self):
        if self.session:
            await self.session.close()  # Close the session when done

    async def set_session(self):
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
