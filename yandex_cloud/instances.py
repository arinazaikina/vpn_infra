import time

from vars import FOLDER_ID, USER
from .client import Client
from .images import Images
from .ssh_keys import SSHKeys
from .subnets import Subnets


class Instances:
    """Класс для управления виртуальными машинами в облачной среде."""

    def __init__(self) -> None:
        """Инициализирует экземпляр клиента для отправки запросов к API."""
        self.session = Client()

    def get_instances(self, folder_id: str = FOLDER_ID):
        """
        Получает список виртуальных машин в указанной папке.

        :param folder_id: Идентификатор папки.
        :return: Ответ API с информацией о виртуальных машинах.
        """
        resp = self.session.get(endpoint=f'{self.session.endpoints.instances}?folderId={folder_id}')
        return resp

    def get_instance_by_id(self, instance_id: str):
        """
        Получает информацию о виртуальной машине по её идентификатору.

        :param instance_id: Идентификатор виртуальной машины.
        :return: Информация о виртуальной машине.
        """
        resp = self.session.get(endpoint=self.session.endpoints.instance.format(instanceId=instance_id))
        return resp

    def get_instance_by_name(self, name: str):
        """
        Получает информацию о виртуальной машине по её имени.

        :param name: Имя виртуальной машины.
        :return: Информация о виртуальной машине, если найдена.
        """
        instances = self.get_instances()
        for instance in instances.get('instances', []):
            if instance.get('name') == name:
                return instance
        return None

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
        """
        Создает виртуальную машину с заданными параметрами.

        :param name: Имя виртуальной машины.
        :param core_fraction: Доля выделенных ядер.
        :param cores: Количество ядер.
        :param memory: Количество памяти в байтах.
        :param disk_size: Размер диска в байтах.
        :param os: Операционная система.
        :param username: Пользователь.
        :param zone_id: Идентификатор зоны.
        :param platform_id: Идентификатор платформы.
        :param folder_id: Идентификатор папки.
        :return: Идентификатор созданной виртуальной машины.
        """
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

    def wait_for_instance_running(self, instance_id: str, timeout=600, interval=10) -> (bool, str):
        """
        Ожидает, пока виртуальная машина не перейдет в состояние RUNNING.

        :param instance_id: Идентификатор виртуальной машины.
        :param timeout: Максимальное время ожидания в секундах.
        :param interval: Интервал между проверками состояния в секундах.
        :return: Кортеж, содержащий статус запуска машины (True, если запущена) и IP-адрес.
        """
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
        """
        Настраивает и запускает виртуальную машину, если она еще не существует. Возвращает IP-адрес запущенной машины.

        :param name: Имя виртуальной машины.
        :param core_fraction: Доля выделенных ядер.
        :param cores: Количество ядер.
        :param memory: Количество памяти в байтах.
        :param disk_size: Размер диска в байтах.
        :param os: Операционная система.
        :param username: Пользователь.
        :param zone_id: Идентификатор зоны.
        :param platform_id: Идентификатор платформы.
        :param folder_id: Идентификатор папки.
        :return: IP-адрес виртуальной машины.

        :raises Exception: Если виртуальная машина не удалось запустить.
        """
        instance = self.get_instance_by_name(name)
        if instance:
            instance_ip = instance.get(
                'networkInterfaces', [])[0].get('primaryV4Address', {}).get('oneToOneNat', {}).get('address')
            print(f'Виртуальная машина с именем "{name}" уже существует по адресу {instance_ip}')
            return instance_ip
        else:
            instance_id = self.create_instance(
                name, core_fraction, cores, memory, disk_size, os, username, zone_id, platform_id, folder_id)
            is_active, instance_ip = self.wait_for_instance_running(instance_id)
            if is_active:
                return instance_ip
            else:
                raise Exception(f"Запуск виртуальной машины {name} не удался")
