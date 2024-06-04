import http
import typing

import requests


class HttpClientError(Exception):
    def __init__(self, code: int, *args: typing.Any) -> None:
        super().__init__(*args)
        self.code = code


class HttpClientProtocol(typing.Protocol):
    def get(self, *args, **kwargs) -> dict:
        ...

    def post(self, *args, **kwargs) -> dict:
        ...

    def delete(self, *args, **kwargs) -> dict:
        ...


class HttpClient:
    """Class wrap for the Requests.

    TODO: Remove the rest-modules dependency on the Requests
    https://github.com/AlexPunches/python-connector/issues/2
    """
    def __init__(self, verify: bool | None):
        self.session = requests.Session()
        self.session.verify = verify

    def get(self, *args, **kwargs) -> dict:
        response = self.session.get(*args, **kwargs)
        if self._is_ok_status_code(status_code=response.status_code):
            return response.json().get("data")
        raise HttpClientError(code=response.status_code)

    def post(self, *args, **kwargs) -> dict:
        response = self.session.post(*args, **kwargs)
        if self._is_ok_status_code(status_code=response.status_code):
            return response.json().get("data")
        raise HttpClientError(code=response.status_code)

    def delete(self, *args, **kwargs) -> dict:
        response = self.session.delete(*args, **kwargs)
        if self._is_ok_status_code(status_code=response.status_code):
            return response.json().get("data")
        raise HttpClientError(code=response.status_code)

    @staticmethod
    def _is_ok_status_code(status_code: int) -> bool:
        return status_code in (http.HTTPStatus.OK,)
