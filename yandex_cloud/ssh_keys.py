import os

from vars import SSH_KEY_NAME


class SSHKeys:
    """
    Класс для управления SSH ключами.
    Позволяет создавать новые SSH ключи и читать существующие публичные ключи из файла.
    """

    def __init__(self, key_name: str = SSH_KEY_NAME) -> None:
        """
        Инициализирует пути к файлам публичного и приватного ключей на основе заданного имени ключа.
        :param key_name: Имя файла ключа.
        """
        self.key_name = key_name
        self.public_key_path = os.path.expanduser(f'~/.ssh/{self.key_name}.pub')
        self.private_key_path = os.path.expanduser(f'~/.ssh/{self.key_name}')

    def create_ssh_key(self):
        """
        Создает новый SSH ключ, если он еще не существует.

        Проверяет наличие файла приватного ключа.
        Если файл не найден, выполняет команду `ssh-keygen` для генерации новой пары ключей.
        Информирует пользователя о создании ключа или о том, что ключ уже существует.
        """
        if not os.path.exists(self.private_key_path):
            print("SSH ключ не найден, создаем новый...")
            os.system(f"ssh-keygen -t rsa -b 4096 -f {self.private_key_path} -N '' -q")
        else:
            print("SSH ключ уже существует, используем существующий...")

    def read_public_key(self) -> str:
        """
        Читает публичный ключ из файла.
        Открывает файл публичного ключа, читает его содержимое и возвращает его значение,
        убирая пробелы в начале и конце строки.

        :return: Строка, содержащая публичный ключ.
        """
        with open(self.public_key_path, 'r') as file:
            public_key = file.read().strip()
        return public_key
