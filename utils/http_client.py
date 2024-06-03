import typing

import requests


class HttpClientProtocol(typing.Protocol):
    def get(self, *args, **kwargs) -> requests.Response:
        ...

    def post(self, *args, **kwargs) -> requests.Response:
        ...

    def delete(self, *args, **kwargs) -> requests.Response:
        ...


class HttpClient:
    """Class wrap for the Requests.

    TODO: Remove the rest-modules dependency on the Requests
    https://github.com/AlexPunches/python-connector/issues/2
    """
    def __init__(self, verify: bool | None):
        self.session = requests.Session()
        self.session.verify = verify

    def get(self, *args, **kwargs) -> requests.Response:
        return self.session.get(*args, **kwargs)

    def post(self, *args, **kwargs) -> requests.Response:
        return self.session.post(*args, **kwargs)

    def delete(self, *args, **kwargs) -> requests.Response:
        return self.session.delete(*args, **kwargs)
