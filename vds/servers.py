import time

from client import Client
from ssh_keys import SSHKeys


class Servers:

    def __init__(self) -> None:
        self.session = Client()

    def get_servers(self):
        resp = self.session.get(endpoint=self.session.endpoints.servers)
        return resp

    def get_server_by_id(self, server_id: int):
        resp = self.session.get(endpoint=self.session.endpoints.server.format(server_id=server_id))
        return resp

    def create_server(self, server_name: str, datacenter: int, server_plan: int, template: int) -> int:
        key_id = SSHKeys().get_active_key_id()
        server_data = {
            'datacenter': datacenter,
            'server-plan': server_plan,
            'template': template,
            'ssh-key': key_id,
            'name': server_name
        }
        response = self.session.post(endpoint=self.session.endpoints.servers, json=server_data, status=202)
        server_id = response.get('data', {}).get('id')
        return server_id

    def wait_for_server_active(self, server_id: int, timeout=600, interval=10):
        start_time = time.time()
        while time.time() - start_time < timeout:
            server_info = self.get_server_by_id(server_id)
            if server_info.get('data', {}).get('status') == 'active':
                print(f"Сервер {server_id} активен.")
                return True, server_info.get('data', {}).get('ip', [])[0].get('ip')
            else:
                print(f"Статус сервера {server_id}: '{server_info.get('data', {}).get('status')}'. Ожидаем...")
                time.sleep(interval)
        print(f"Время ожидания истекло, сервер {server_id} не активен.")
        return False, None

    def setup_server(self, server_name, datacenter, server_plan, template):
        server_id = self.create_server(server_name, datacenter, server_plan, template)
        is_active, server_ip = self.wait_for_server_active(server_id)
        if is_active:
            return server_ip
        else:
            raise Exception(f"Активация сервера {server_name} не удалась")
