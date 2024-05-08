import time

from .client import Client
from .images import Images
from .ssh_keys import SSHKeys
from .subnets import Subnets
from vars import FOLDER_ID, USER


class Instances:

    def __init__(self) -> None:
        self.session = Client()

    def get_instances(self):
        resp = self.session.get(endpoint=f'{self.session.endpoints.instances}?folderId={FOLDER_ID}')
        return resp

    def get_instance_by_id(self, instance_id: str):
        resp = self.session.get(endpoint=self.session.endpoints.instance.format(instanceId=instance_id))
        return resp

    def create_instance(
            self,
            name: str,
            core_fraction: int,
            cores: int,
            memory: int,
            disk_size: int,
            os: str = 'Ubuntu 22.04 OsLogin',
            username: str = USER,
            zone_id: str = 'ru-central1-a',
            platform_id: str = 'standard-v3',
            folder_id: str = FOLDER_ID):
        ssh_key = SSHKeys().read_public_key()
        user_data = f"""#cloud-config
        users:
          - name: {username}
            sudo: ['ALL=(ALL) NOPASSWD:ALL']
            shell: /bin/bash
            ssh_authorized_keys:
              - {ssh_key}
        """
        subnet_id = Subnets().get_subnet_id_by_zone(zone_id)
        image_id = Images().get_image_id(description=os, min_disk_size=str(disk_size))
        payload = {
            "folderId": folder_id,
            "networkInterfaceSpecs": [
                {
                    "subnetId": subnet_id,
                    "primaryV4AddressSpec": {
                        "address": "",
                        "oneToOneNatSpec": {
                            "ipVersion": "IPV4"
                        },
                        "dnsRecordSpecs": []
                    },
                    "securityGroupIds": []
                }
            ],
            "name": name,
            "zoneId": zone_id,
            "resourcesSpec": {
                "cores": cores,
                "memory": memory,
                "coreFraction": core_fraction
            },
            "platformId": platform_id,
            "bootDiskSpec": {
                "diskSpec": {
                    "size": disk_size,
                    "typeId": "network-hdd",
                    "imageId": image_id
                }
            },
            "secondaryDiskSpecs": [],
            "localDiskSpecs": [],
            "metadata": {
                "user-data": user_data,
                "ssh-keys": f"{username}:{ssh_key}",
                "serial-port-enable": "0",
                "install-unified-agent": "0"
            }
        }
        response = self.session.post(endpoint=self.session.endpoints.instances, json=payload)
        instance_id = response.get('metadata', {}).get('instanceId')
        return instance_id

    def wait_for_instance_running(self, instance_id: str, timeout=600, interval=10):
        start_time = time.time()
        while time.time() - start_time < timeout:
            instance_info = self.get_instance_by_id(instance_id)
            if instance_info.get('status') == 'RUNNING':
                print(f"Виртуальная машина {instance_id} запущена.")
                return True, instance_info.get('networkInterfaces', [])[0].get('primaryV4Address', {}).get(
                    'oneToOneNat', {}).get('address')
            else:
                print(f"Статус виртуальной машины {instance_id}: '{instance_info.get('status')}'. Ожидаем...")
                time.sleep(interval)
        print(f"Время ожидания истекло, виртуальная машина {instance_id} не запустилась.")
        return False, None

    def setup_instance(
            self,
            name: str,
            core_fraction: int,
            cores: int,
            memory: int,
            disk_size: int,
            os: str = 'Ubuntu 22.04 OsLogin',
            username: str = USER,
            zone_id: str = 'ru-central1-a',
            platform_id: str = 'standard-v3',
            folder_id: str = FOLDER_ID):
        instance_id = self.create_instance(
            name, core_fraction, cores, memory, disk_size, os, username, zone_id, platform_id, folder_id)
        is_active, server_ip = self.wait_for_instance_running(instance_id)
        if is_active:
            return server_ip
        else:
            raise Exception(f"Запуск виртуальной машины {name} не удался")
