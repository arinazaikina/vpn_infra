import concurrent.futures
import os
import shlex
import subprocess

import requests

from instances_config import INSTANCES_CONFIG
from vars import (
    USER, FOLDER_ID, SSH_PRIVATE_KEY_PATH, SSH_PUBLIC_KEY_PATH, YANDEX_EMAIL, YANDEX_EMAIL_PASSWORD, MONITORING_PASSWORD
)
from yandex_cloud.disks import Disks
from yandex_cloud.instances import Instances
from yandex_cloud.snapshot_schedules import SnapshotSchedule
from yandex_cloud.ssh_keys import SSHKeys

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))


def create_instances() -> dict:
    """
    Создаёт виртуальные машины на основе конфигурации, указанной в INSTANCES_CONFIG.
    Использует многопоточность для ускорения процесса создания виртуальных машин.
    :return: Словарь с именами виртуальных машин и их IP-адресами.
    """
    instance_data = {}

    ssh_keys = SSHKeys()
    ssh_keys.create_ssh_key()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_instance = {
            executor.submit(
                Instances().setup_instance,
                instance['name'],
                instance['core_fraction'],
                instance['cores'],
                instance['memory'],
                instance['disk_size'],
                instance['os'],
                instance['username'],
                instance['zone_id'],
                instance['platform_id'],
                FOLDER_ID
            ): instance['name'] for instance in INSTANCES_CONFIG
        }
        for future in concurrent.futures.as_completed(future_to_instance):
            instance_name = future_to_instance[future]
            try:
                ip = future.result()
                instance_data[instance_name] = ip
                print(f"Виртуальная машина {instance_name} успешно создана и доступна по адресу {ip}.")
            except Exception as exc:
                print(f"При настройке виртуальной машины {instance_name} произошла ошибка: {exc}")

    print("Итоговый список IP-адресов виртуальных машин:", instance_data)
    return instance_data


def create_snapshot_schedule(
        schedule_name: str,
        description: str,
        schedule_expression: str = "0 0 */1 * *",
        max_snapshot_to_keep: int = 10,
        folder_id: str = FOLDER_ID) -> None:
    """
    Создаёт расписание снимков дисков для всех виртуальных машин, определённых в INSTANCES_CONFIG.

    :param schedule_name: Имя для расписания снимков.
    :param description: Описание расписания снимков.
    :param schedule_expression: Выражение cron для расписания.
    :param max_snapshot_to_keep: Максимальное количество хранимых снимков.
    :param folder_id: Идентификатор папки в Yandex Cloud.
    """
    instance_names = [instance.get('name') for instance in INSTANCES_CONFIG]
    instance_ids = [Instances().get_instance_by_name(name).get('id') for name in instance_names]
    disk_ids = [Disks().get_disk_id_by_instance_id(instance_id) for instance_id in instance_ids]
    SnapshotSchedule().setup_snapshot_schedule(
        schedule_name, description, disk_ids, schedule_expression, max_snapshot_to_keep, folder_id)


def get_public_ip() -> str:
    """
    Получает публичный IP-адрес машины, на которой выполняется скрипт.
    :return: Публичный IP-адрес.
    """
    try:
        response = requests.get('https://api.ipify.org')
        public_ip = response.text
    except requests.RequestException:
        public_ip = '127.0.0.1'
    return public_ip


def write_inventory(ips) -> None:
    """
    Записывает файл inventory для Ansible с IP-адресами созданных виртуальных машин.
    :param ips: Словарь с именами виртуальных машин и их IP-адресами.
    """
    inventory_path = os.path.join(PROJECT_ROOT, 'ansible', 'inventory')
    os.makedirs(inventory_path, exist_ok=True)
    hosts_file_path = os.path.join(inventory_path, 'hosts')

    with open(hosts_file_path, 'w') as f:
        for name, ip in ips.items():
            f.write(f"[{name}]\n")
            f.write(f"{name.lower()}_server ansible_host={ip}\n")
    print(f"hosts файл: {hosts_file_path}")


def run_ansible():
    """
    Запускает Ansible playbook, передавая ему необходимые переменные для настройки виртуальных машин.
    Использует внешние переменные, такие как пользователь, ключи SSH, email и пароль для мониторинга.
    """
    extra_vars = {
        'ansible_ssh_user': USER,
        'ansible_ssh_private_key_file': SSH_PRIVATE_KEY_PATH,
        'ansible_ssh_public_key_file': SSH_PUBLIC_KEY_PATH,
        'local_host_ip': get_public_ip(),
        'yandex_email': YANDEX_EMAIL,
        'yandex_email_password': YANDEX_EMAIL_PASSWORD,
        'monitoring_password': MONITORING_PASSWORD
    }
    extra_vars_string = ' '.join(f"{key}={shlex.quote(str(value))}" for key, value in extra_vars.items())
    playbook_path = os.path.join(PROJECT_ROOT, 'ansible', 'playbooks', 'playbook.yml')
    subprocess.run(['ansible-playbook', playbook_path, '--extra-vars', extra_vars_string], check=True)
