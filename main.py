import time

from utils import create_instances, create_snapshot_schedule, write_inventory, run_ansible

if __name__ == "__main__":
    print("Создание виртуальных машин...")
    instance_ips = create_instances()
    write_inventory(instance_ips)
    print('Создание расписания снимков дисков...')
    create_snapshot_schedule('vpn', 'vpn')
    print("Ожидание 60 секунд...")
    time.sleep(60)
    print("Запуск Ansible playbook для настройки машин...")
    run_ansible()
