import requests

from vds.endpoints import ApiEndpoints
from vds.vars import API_TOKEN, BASE_URL


class Client:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"Authorization": API_TOKEN})
        self.endpoints = ApiEndpoints()

    def _send_request(self, method: str, endpoint: str, expected_status: int = 200, **kwargs):
        url = f"{BASE_URL}/{endpoint}"
        response = self.session.request(method, url, **kwargs)
        if response.status_code != expected_status:
            raise Exception(f'Код ответа: ожидается {expected_status}, текущий {response.status_code}')
        try:
            return response.json()
        except ValueError:
            return response.text

    def get(self, **kwargs):
        return self._send_request(method='GET', **kwargs)

    def post(self, status: int = 201, **kwargs):
        return self._send_request(method='POST', expected_status=status, **kwargs)

    def put(self, **kwargs):
        return self._send_request(method='PUT', **kwargs)

    def delete(self, **kwargs):
        return self._send_request(method='DELETE', **kwargs)
