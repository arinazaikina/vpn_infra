#!/bin/bash

# Путь к конфигурационному файлу
CONFIG_FILE="/etc/myvpn/vpn_config.conf"

# Чтение конфигурационного файла
# shellcheck source=/etc/myvpn/vpn_config.conf
if [ -f "$CONFIG_FILE" ]; then
    source "$CONFIG_FILE"
else
    echo "Конфигурационный файл не найден: $CONFIG_FILE"
    exit 1
fi

# Проверка необходимых переменных
if [ -z "$CA_USER" ] || [ -z "$CA_IP" ] || [ -z "$CA_DIR" ]; then
    echo "Конфигурационный файл не содержит необходимых настроек."
    exit 1
fi

echo "Конфигурация успешно загружена."
