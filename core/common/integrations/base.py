from dataclasses import dataclass
from functools import partialmethod
from typing import (
    Optional,
    Protocol,
)
from urllib.parse import urljoin

import httpx

from core.common.integrations.const import SAFE_METHODS
from core.common.integrations.exceptions import IntegrationException


@dataclass
class IClient(Protocol):
    def get(
        self,
        uri: str,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
    ) -> None:
        ...

    def post(
        self,
        uri: str,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
        json: Optional[dict] = None,
        data: Optional[dict] = None,
    ) -> None:
        ...

    def put(
        self,
        uri: str,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
        json: Optional[dict] = None,
        data: Optional[dict] = None,
    ) -> None:
        ...

    def patch(
        self,
        uri: str,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
        json: Optional[dict] = None,
        data: Optional[dict] = None,
    ) -> None:
        ...

    def delete(
        self,
        uri: str,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
    ) -> None:
        ...


@dataclass
class HTTPXClient(IClient):
    base_url: str

    def __post_init__(self):
        self.headers = {}

    def set_headers(self, new_headers: dict) -> None:
        self.headers.update(new_headers)

    def __get_client(self):
        return httpx.Client(base_url=self.base_url, headers=self.headers)

    def _make_request(
        self,
        method: str,
        uri: str,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
        **kwargs,
    ) -> None:
        json: Optional[dict] = kwargs.get('json')
        data: Optional[dict] = kwargs.get('data')

        with self.__get_client() as client:
            request_kwargs = self.__build_request_kwargs(
                method,
                params,
                headers,
                json,
                data,
            )

            request_method = getattr(client, method)
            response = request_method(
                urljoin(self.base_url, uri),
                **request_kwargs,
            )

            if response.is_error:
                raise IntegrationException(response.content)
            return response.json()

    def __build_request_kwargs(
        self,
        method: str,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
        json: Optional[dict] = None,
        data: Optional[dict] = None,
    ):
        request_kwargs = {
            'params': params,
            'headers': headers,
        }

        if method not in SAFE_METHODS:
            request_kwargs['json'] = json
            request_kwargs['data'] = data

        return request_kwargs

    get = partialmethod(_make_request, 'get')
    post = partialmethod(_make_request, 'post')
    put = partialmethod(_make_request, 'put')
    patch = partialmethod(_make_request, 'patch')
    delete = partialmethod(_make_request, 'delete')
