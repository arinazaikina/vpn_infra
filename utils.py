import concurrent.futures
import os
import shlex
import subprocess

import requests

from instances_config import INSTANCES_CONFIG
from vars import (
    USER, FOLDER_ID, SSH_PRIVATE_KEY_PATH, SSH_PUBLIC_KEY_PATH, YANDEX_EMAIL, YANDEX_EMAIL_PASSWORD, MONITORING_PASSWORD
)
from yandex_cloud.instances import Instances
from yandex_cloud.ssh_keys import SSHKeys

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))


def create_instances():
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


def get_public_ip():
    try:
        response = requests.get('https://api.ipify.org')
        public_ip = response.text
    except requests.RequestException:
        public_ip = '127.0.0.1'
    return public_ip


def write_inventory(ips):
    inventory_path = os.path.join(PROJECT_ROOT, 'ansible', 'inventory')
    os.makedirs(inventory_path, exist_ok=True)
    hosts_file_path = os.path.join(inventory_path, 'hosts')

    with open(hosts_file_path, 'w') as f:
        for name, ip in ips.items():
            f.write(f"[{name}]\n")
            f.write(f"{name.lower()}_server ansible_host={ip}\n")
    print(f"hosts файл создан: {hosts_file_path}")


def run_ansible():
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
