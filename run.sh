#!/bin/bash

set -e

source venv/bin/activate

echo "Создание виртуальных машин..."
python yandex_cloud/main.py

echo "Ожидание 60 секунд...".
sleep 60

echo "Запуск Ansible playbook..."
ansible-playbook ansible/playbooks/playbook.yml

echo "Разворачивание VPN-инфраструктуры выполнено успешно!"
