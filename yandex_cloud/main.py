import concurrent.futures
import os

import requests

from instances import Instances
from ssh_keys import SSHKeys
from vars import SSH_PUBLIC_KEY_PATH, SSH_PRIVATE_KEY_PATH, USER, FOLDER_ID, YANDEX_EMAIL, YANDEX_EMAIL_PASSWORD


def create_instances():
    instances_config = [
        {
            "name": "ca",
            "core_fraction": 20,
            "cores": 2,
            "memory": 1024 ** 3,
            "disk_size": 10 * 1024 ** 3,
            "os": "Ubuntu 22.04 OsLogin",
            "username": USER,
            "zone_id": "ru-central1-a",
            "platform_id": "standard-v3"
        },
        {
            "name": "vpn",
            "core_fraction": 20,
            "cores": 2,
            "memory": 1024 ** 3,
            "disk_size": 10 * 1024 ** 3,
            "os": "Ubuntu 22.04 OsLogin",
            "username": USER,
            "zone_id": "ru-central1-a",
            "platform_id": "standard-v3"
        }
    ]

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
            ): instance['name'] for instance in instances_config
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
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    inventory_path = os.path.join(project_root, 'ansible', 'inventory')
    os.makedirs(inventory_path, exist_ok=True)

    group_vars_path = os.path.join(project_root, 'ansible', 'inventory', 'group_vars')
    os.makedirs(group_vars_path, exist_ok=True)

    hosts_file_path = os.path.join(inventory_path, 'hosts.ini')
    all_vars_path = os.path.join(group_vars_path, 'all')

    public_ip = get_public_ip()

    with open(all_vars_path, 'w') as f:
        f.write(f"ansible_ssh_user: {USER}\n")
        f.write(f"ansible_ssh_private_key_file: {SSH_PRIVATE_KEY_PATH}\n")
        f.write(f"ansible_ssh_public_key_file: {SSH_PUBLIC_KEY_PATH}\n")
        f.write("ansible_ssh_common_args: '-o StrictHostKeyChecking=no -o IdentitiesOnly=yes -o ControlMaster=no'\n")
        f.write(f"local_host_ip: {public_ip}\n")
        f.write(f"yandex_email: {YANDEX_EMAIL}\n")
        f.write(f"yandex_email_password: {YANDEX_EMAIL_PASSWORD}\n")
    print(f"Файл group_vars/all создан: {all_vars_path}")

    with open(hosts_file_path, 'w') as f:
        for name, ip in ips.items():
            f.write(f"[{name}]\n")
            f.write(f"{name.lower()}_server ansible_host={ip}\n")
    print(f"hosts.ini файл создан: {hosts_file_path}")


if __name__ == "__main__":
    instance_ips = create_instances()
    write_inventory(instance_ips)
