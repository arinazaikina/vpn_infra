from vars import FOLDER_ID
from .client import Client


class Disks:
    """Класс для работы с дисками в YandexCloud."""

    def __init__(self) -> None:
        """Инициализирует экземпляр клиента для отправки запросов к API."""
        self.session = Client()

    def get_disks(self, folder_id: str = FOLDER_ID):
        """
        Получает список дисков в заданной папке.

        :param folder_id: Идентификатор папки.
        :return: Ответ API с информацией о дисках.
        """
        resp = self.session.get(endpoint=f'{self.session.endpoints.disks}?folderId={folder_id}')
        return resp

    def get_disk_id_by_instance_id(self, instance_id: str):
        """
        Возвращает идентификатор диска по идентификатору виртуальной машины.

        :param instance_id: Идентификатор виртуальной машины, для которой нужно найти диск.
        :return: Идентификатор диска, связанного с указанной виртуальной машиной.
        """
        disk_info = self.get_disks()
        for disk in disk_info.get('disks', []):
            if instance_id in disk.get('instanceIds', []):
                return disk.get('id')
