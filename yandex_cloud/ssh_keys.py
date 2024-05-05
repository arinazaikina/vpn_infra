import os

from vars import SSH_KEY_NAME


class SSHKeys:

    def __init__(self) -> None:
        self.key_name = SSH_KEY_NAME
        self.public_key_path = os.path.expanduser(f'~/.ssh/{self.key_name}.pub')
        self.private_key_path = os.path.expanduser(f'~/.ssh/{self.key_name}')

    def create_ssh_key(self):
        if not os.path.exists(self.private_key_path):
            print("SSH ключ не найден, создаем новый...")
            os.system(f"ssh-keygen -t rsa -b 4096 -f {self.private_key_path} -N '' -q")
        else:
            print("SSH ключ уже существует, используем существующий...")

    def read_public_key(self):
        with open(self.public_key_path, 'r') as file:
            public_key = file.read().strip()
        return public_key
