import json
import time

import jwt
import requests

from vars import AUTHORIZED_KEY_PATH
from .endpoints import ApiEndpoints


class Client:
    """
    Клиент для выполнения API-запросов с авторизацией.
    :param key_file_path: Путь к файлу с ключом для авторизации.
    """

    def __init__(self, key_file_path: str = AUTHORIZED_KEY_PATH) -> None:
        self.endpoints = ApiEndpoints()
        self.session = requests.Session()
        self.key_file_path = key_file_path
        self.key_data = self.load_key_data()
        self.update_token()

    def load_key_data(self) -> dict:
        """
        Загружает данные из файла ключа.
        :raises Exception: Возникает, если не удается загрузить данные из файла.
        :return: Данные ключа.
        """
        try:
            with open(self.key_file_path, 'r') as file:
                key_data = json.load(file)
            return key_data
        except Exception as e:
            raise Exception(f"Ошибка при загрузке данных ключа: {e}")

    def update_token(self) -> None:
        """Обновляет токен авторизации, используя данные ключа."""
        issued_at_time = int(time.time())
        expiration_time = issued_at_time + 600

        headers = {'kid': self.key_data['id']}
        payload = {
            'iss': self.key_data['service_account_id'],
            'aud': self.endpoints.auth,
            'iat': issued_at_time,
            'exp': expiration_time
        }

        private_key = self.key_data['private_key'].replace('\\n', '\n')
        encoded_jwt = jwt.encode(payload, private_key, algorithm='PS256', headers=headers)

        iam_token = self.get_iam_token(encoded_jwt)
        self.session.headers.update({"Authorization": f"Bearer {iam_token}"})

    def get_iam_token(self, jwt_token: str) -> str:
        """
        Получает IAM токен, используя JWT.
        :param jwt_token: JSON Web Token для авторизации.
        :raises Exception: Возникает, если сервер возвращает ошибку при получении IAM-токена.
        :return: IAM токен.
        """
        url = self.endpoints.auth
        headers = {'Content-Type': 'application/json'}
        data = {'jwt': jwt_token}

        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()['iamToken']
        else:
            raise Exception(f'Ошибка при получении IAM-токена: {response.status_code} - {response.text}')

    def _send_request(self, method: str, endpoint: str, expected_status: int = 200, **kwargs):
        """
        Отправляет HTTP-запрос к API.

        :param method: HTTP метод запроса.
        :param endpoint: Конечная точка API, к которой будет отправлен запрос.
        :param expected_status: Ожидаемый HTTP статус код ответа (по умолчанию 200).
        :raises Exception: Возникает, если статус ответа отличается от ожидаемого.
        :return: Ответ сервера в формате JSON или текст, если JSON не предоставлен.
        """
        if "Authorization" not in self.session.headers:
            self.update_token()
        response = self.session.request(method, endpoint, **kwargs)
        if response.status_code != expected_status:
            error_message = response.text
            raise Exception(
                f'Код ответа: ожидается {expected_status}, текущий {response.status_code}. Ошибка: {error_message}')
        try:
            return response.json()
        except ValueError:
            return response.text

    def get(self, **kwargs):
        """
        Выполняет GET-запрос к API.
        :return: Ответ сервера.
        """
        return self._send_request(method='GET', **kwargs)

    def post(self, **kwargs):
        """
        Выполняет POST-запрос к API.
        :return: Ответ сервера.
        """
        return self._send_request(method='POST', **kwargs)

    def put(self, **kwargs):
        """
        Выполняет PUT-запрос к API.
        :return: Ответ сервера.
        """
        return self._send_request(method='PUT', **kwargs)

    def delete(self, **kwargs):
        """
        Выполняет DELETE-запрос к API.
        :return: Ответ сервера.
        """
        return self._send_request(method='DELETE', **kwargs)
