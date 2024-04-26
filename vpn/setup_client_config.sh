#!/bin/bash

source /usr/bin/load_config.sh

# Переменные директорий
CLIENTS_DIR="/home/$CA_USER/clients/keys"
SERVER_DIR="/etc/openvpn/server"

# Проверяем и создаем поддиректорию keys, если она не существует
if [ ! -d "$CLIENTS_DIR" ]; then
    echo "Поддиректория 'keys' не найдена. Создаем..."
    if ! mkdir -p "$CLIENTS_DIR"; then
        echo "Не удалось создать поддиректорию 'keys'."
        exit 1
    else
        echo "Поддиректория 'keys' успешно создана."
    fi
fi

copy_file() {
    local src_file="$1"
    local dest_dir="$2"
    local file_name

    # Проверяем и присваиваем имя файла напрямую
    if file_name=$(basename "$src_file"); then
        echo "Обработка файла $file_name."
    else
        echo "Ошибка при получении имени файла из $src_file"
        exit 1
    fi

    if [ -f "$src_file" ]; then
        echo "Найден файл $file_name. Производим копирование..."
        if cp "$src_file" "$dest_dir"; then
            echo "Файл $file_name успешно скопирован в $dest_dir"
        else
            echo "Ошибка копирования файла $file_name в $dest_dir"
            exit 1
        fi
    else
        echo "Файл $file_name не найден в $SERVER_DIR"
        exit 1
    fi
}

# Копирование файла ca.crt
copy_file "$SERVER_DIR/ca.crt" "$CLIENTS_DIR"

# Копирование файла ta.key
copy_file "$SERVER_DIR/ta.key" "$CLIENTS_DIR"
