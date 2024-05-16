from vars import FOLDER_ID
from .client import Client


class Subnets:
    """Класс для управления подсетями в облачной инфраструктуре."""

    def __init__(self) -> None:
        """Инициализирует экземпляр клиента для отправки запросов к API."""
        self.session = Client()

    def get_subnets(self, folder_id: str = FOLDER_ID):
        """
        Получает список всех подсетей в указанной папке.

        :param folder_id: Идентификатор папки.
        :return: Ответ API с информацией о подсетях.
        """
        resp = self.session.get(endpoint=f'{self.session.endpoints.subnets}?folderId={folder_id}')
        return resp

    def get_subnet_id_by_zone(self, zone_id: str):
        """
        Получает идентификатор подсети по идентификатору зоны размещения.

        :param zone_id: Идентификатор зоны размещения, по которому осуществляется поиск подсети.
        :return: Идентификатор подсети, соответствующей указанной зоне, если таковая найдена.
        """
        subnets_info = self.get_subnets()
        if 'subnets' in subnets_info:
            for subnet in subnets_info.get('subnets', []):
                if zone_id.lower() in subnet.get('name').lower():
                    return subnet.get('id')
        return None
