#!/bin/bash

set -e

source venv/bin/activate

#echo "Создание виртуальных машин..."
#python vds/main.py

echo "Ожидание 60 секунд..."
sleep 60

echo "Запуск Ansible playbook для настройки пользователей..."
ansible-playbook -i ansible/inventory/hosts ansible/playbooks/setup_user.yml

echo "Запуск Python скрипта для обновления файла hosts..."
python vds/ansible_ssh_user.py

echo "Запуск Ansible playbook для настройки SSH..."
ansible-playbook -i ansible/inventory/hosts ansible/playbooks/setup_ssh.yml

echo "Все операции выполнены успешно!"
