import os

from vds.client import Client


class SSHKeys:

    def __init__(self) -> None:
        self.session = Client()
        self.key_name = 'VDSina_key'
        self.public_key_path = os.path.expanduser(f'~/.ssh/{self.key_name}.pub')
        self.private_key_path = os.path.expanduser(f'~/.ssh/{self.key_name}')

    def create_ssh_key(self):
        if not os.path.exists(self.private_key_path):
            os.system(f"ssh-keygen -t rsa -b 4096 -f {self.private_key_path} -N ''")

    def read_public_key(self):
        self.create_ssh_key()
        with open(self.public_key_path, 'r') as file:
            public_key = file.read().strip()
        return public_key

    def get_ssh_keys(self):
        resp = self.session.get(endpoint=self.session.endpoints.ssh_keys)
        data = resp.get('data', [])
        return data

    def add_ssh_key(self) -> int:
        public_key = self.read_public_key()
        resp = self.session.post(
            endpoint=self.session.endpoints.ssh_keys,
            json={'data': public_key, 'name': self.key_name})
        key_id = resp.get('data', {}).get('id')
        return key_id

    def get_active_key_id(self) -> int:
        keys = self.get_ssh_keys()
        if keys is None:
            new_key_id = self.add_ssh_key()
            return new_key_id
        key_data = self.get_ssh_keys()
        current_key_id = key_data[0].get('id')
        return current_key_id
