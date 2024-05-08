#!/bin/bash

set -e

source venv/bin/activate

echo "Создание виртуальных машин..."
python main.py

echo "Разворачивание VPN-инфраструктуры выполнено успешно!"
