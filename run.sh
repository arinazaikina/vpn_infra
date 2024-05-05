#!/bin/bash

set -e

source venv/bin/activate

echo "Создание виртуальных машин..."
python yandex_cloud/main.py

echo "Ожидание 30 секунд..."
sleep 30

echo "Запуск Ansible playbook для настройки SSH..."
ansible-playbook -i ansible/inventory/hosts ansible/playbooks/setup_ssh.yml

echo "Запуск Ansible playbook для настройки firewall..."
ansible-playbook -i ansible/inventory/hosts ansible/playbooks/setup_firewall.yml

echo "Запуск Ansible playbook для настройки пользовательского APT репозитория..."
ansible-playbook -i ansible/inventory/hosts ansible/playbooks/setup_apt_repository.yml

echo "Запуск Ansible playbook для настройки SMTP..."
ansible-playbook -i ansible/inventory/hosts ansible/playbooks/setup_smtp.yml

echo "Запуск Ansible playbook для настройки сервера удостоверяющего центра..."
ansible-playbook -i ansible/inventory/hosts ansible/playbooks/install_ca_package.yml

echo "Запуск Ansible playbook для создания конфигурационного файла на VPN-сервере..."
ansible-playbook -i ansible/inventory/hosts ansible/playbooks/vpn_configurator.yml

echo "Запуск Ansible playbook для настройки VPN-сервера..."
ansible-playbook -i ansible/inventory/hosts ansible/playbooks/install_vpn_package.yml

echo "Все операции выполнены успешно!"
