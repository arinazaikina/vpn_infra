#!/bin/bash

set -e

source venv/bin/activate

echo "Создание виртуальных машин..."
python vds/main.py

echo "Ожидание 60 секунд..."
sleep 60

echo "Запуск Ansible playbook для настройки пользователей..."
ansible-playbook -i ansible/inventory/hosts ansible/playbooks/setup_user.yml

echo "Запуск Python скрипта для обновления файла hosts..."
python vds/ansible_ssh_user.py -v

echo "Запуск Ansible playbook для настройки SSH..."
ansible-playbook -i ansible/inventory/hosts ansible/playbooks/setup_ssh.yml

echo "Запуск Ansible playbook для настройки firewall..."
ansible-playbook -i ansible/inventory/hosts ansible/playbooks/setup_firewall.yml

echo "Запуск Ansible playbook для настройки пользовательского APT репозитория..."
ansible-playbook -i ansible/inventory/hosts ansible/playbooks/setup_apt_repository.yml

echo "Запуск Ansible playbook для настройки сервера удостоверяющего центра..."
ansible-playbook -i ansible/inventory/hosts ansible/playbooks/install_ca_package.yml

echo "Запуск Ansible playbook для создания конфигурационного файла на VPN-сервере..."
ansible-playbook -i ansible/inventory/hosts ansible/playbooks/vpn_configurator.yml

echo "Запуск Ansible playbook для настройки VPN-сервера..."
ansible-playbook -i ansible/inventory/hosts ansible/playbooks/install_vpn_package.yml

echo "Все операции выполнены успешно!"
