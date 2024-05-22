#!/bin/bash

set -e

source venv/bin/activate

python main.py

echo "Разворачивание VPN-инфраструктуры выполнено успешно!"
