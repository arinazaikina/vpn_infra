#!/bin/bash

source /usr/bin/load_config.sh

# Переменные директорий
CLIENTS_KEYS_DIR="/home/$CA_USER/clients/keys"
BASE_CONFIG_DIR="/home/$CA_USER/clients"
SERVER_DIR="/etc/openvpn/server"

# Проверяем и создаем поддиректорию keys, если она не существует
if [ ! -d "$CLIENTS_KEYS_DIR" ]; then
    echo "Поддиректория 'keys' не найдена. Создаем..."
    if ! mkdir -p "$CLIENTS_KEYS_DIR"; then
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
copy_file "$SERVER_DIR/ca.crt" "$CLIENTS_KEYS_DIR"

# Копирование файла ta.key
copy_file "$SERVER_DIR/ta.key" "$CLIENTS_KEYS_DIR"

echo "Создание файла base.conf..."
cat <<EOF > "$BASE_CONFIG_DIR/base.conf"
client
dev tun
proto udp
remote $VPN_SERVER_IP 1194
resolv-retry infinite
nobind
user nobody
group nogroup
persist-key
persist-tun
remote-cert-tls server
tls-crypt ta.key
cipher AES-256-GCM
auth SHA256
verb 3
key-direction 1
EOF

echo "Файл base.conf успешно создан в $BASE_CONFIG_DIR"
