import concurrent.futures
import os

from vds.servers import Servers


def main():
    servers_config = [
        ("CA", 1, 11, 15),
        ("VPN-server", 1, 11, 15)
        # ("Monitoring", 1, 11, 15),
        # ("Backup", 1, 11, 15)
    ]

    server_data = {}

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_server = {
            executor.submit(Servers().setup_server, name, 1, 11, 15): name for name, _, _, _ in servers_config
        }
        for future in concurrent.futures.as_completed(future_to_server):
            server_name = future_to_server[future]
            try:
                ip = future.result()
                server_data[server_name] = ip
                print(f"Сервер {server_name} успешно создан и доступен по адресу {ip}.")
            except Exception as exc:
                print(f"При настройке сервера {server_name} произошла ошибка: {exc}")

    print("Итоговый список IP-адресов серверов:", server_data)
    return server_data


def write_inventory(ips):
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    inventory_path = os.path.join(project_root, 'ansible', 'inventory')
    hosts_file_path = os.path.join(inventory_path, 'hosts')

    os.makedirs(inventory_path, exist_ok=True)

    with open(hosts_file_path, 'w') as f:
        for name, ip in ips.items():
            f.write(f"[{name}]\n")
            f.write(f"{ip}\n\n")

    print(f"Inventory файл создан: {hosts_file_path}")


if __name__ == "__main__":
    server_ips = main()
    write_inventory(server_ips)
