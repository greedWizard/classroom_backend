from dataclasses import dataclass

import httpx

from core.apps.integrations.authentications.vk.schemas import (
    VKResponseAccessDataSchema,
    VKResponseUserInfoSchema,
)
from core.apps.integrations.exceptions import IntegrationException
from core.common.config import config


@dataclass
class VKIntegratioinClient:
    client_id: str
    client_secret: str
    redirect_uri: str

    def __get_oauth_client(self):
        return httpx.AsyncClient(base_url=config.VK_OAUTH_URL)

    def __get_api_client(self):
        return httpx.AsyncClient(base_url=config.VK_API_URL)

    async def get_user_access_data(self, code: str) -> VKResponseAccessDataSchema:
        async with self.__get_oauth_client() as client:
            response = await client.get(
                url='access_token', params={
                    'client_id': self.client_id,
                    'client_secret': self.client_secret,
                    'redirect_uri': self.redirect_uri,
                    'code': code,
                },
            )

            if response.is_error:
                raise IntegrationException(response.content.decode())

            return VKResponseAccessDataSchema(**response.json())

    async def get_user_data(
        self,
        access_token: str,
        user_id: int,
    ) -> VKResponseUserInfoSchema:
        async with self.__get_api_client() as client:
            response = await client.post(
                url='/method/users.get/',
                data={
                    'access_token': access_token,
                    'user_ids': [user_id],
                    'fields': ['photo_400_orig'],
                },
                params={
                    'v': config.VK_API_VERSION,
                },
            )

            if response.is_error:
                raise IntegrationException(response.content.decode())

            user_info = response.json()['response'][0]
            user_info['user_id'] = user_id

            return VKResponseUserInfoSchema(**user_info)
