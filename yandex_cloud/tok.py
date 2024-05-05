import jwt
import json
import time
import requests


with open('/home/arina/Downloads/authorized_key.json', 'r') as file:
    key_data = json.load(file)

# Подготовка данных для создания JWT
issued_at_time = int(time.time())
expiration_time = issued_at_time + 360  # Токен действителен 6 минут

# Создание JWT
headers = {
    'kid': key_data['id']  # Идентификатор ключа, который используется для подписи JWT
}

# Создание JWT
payload = {
    'iss': key_data['service_account_id'],
    'aud': 'https://iam.api.cloud.yandex.net/iam/v1/tokens',
    'iat': issued_at_time,
    'exp': expiration_time
}

# Подпись JWT закрытым ключом
private_key = key_data['private_key'].replace('\\n', '\n')
encoded_jwt = jwt.encode(payload, private_key, algorithm='PS256', headers=headers)

# Отправка запроса на получение IAM токена
def get_iam_token(jwt_token):
    url = 'https://iam.api.cloud.yandex.net/iam/v1/tokens'
    headers = {'Content-Type': 'application/json'}
    data = {'jwt': jwt_token}

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()['iamToken']
    else:
        raise Exception(f'Error retrieving IAM token: {response.status_code} - {response.text}')

iam_token = get_iam_token(encoded_jwt)
print(f'IAM Token: {iam_token}')
