from .client import Client
from vars import FOLDER_ID


class Subnets:

    def __init__(self) -> None:
        self.session = Client()

    def get_subnets(self):
        resp = self.session.get(endpoint=f'{self.session.endpoints.subnets}?folderId={FOLDER_ID}')
        return resp

    def get_subnet_id_by_zone(self, zone_id: str):
        subnets_info = self.get_subnets()
        if 'subnets' in subnets_info:
            for subnet in subnets_info.get('subnets', []):
                if zone_id.lower() in subnet.get('name').lower():
                    return subnet.get('id')
        return None
