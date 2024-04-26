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

ENTITY="$1"

# Проверяем, указан ли тип сущности
if [ -z "$ENTITY" ]; then
    echo "Не указан тип сущности (например, server или user1)"
    exit 1
fi

# Определение директории для сохранения ключей и сертификатов
ENTITY_DIR="/home/$CA_USER/clients/"
if [ "$ENTITY" = "server" ]; then
    ENTITY_DIR="/etc/openvpn/server"
else
    # Проверка на существование сертификата клиента
    if [ -f "$ENTITY_DIR/$ENTITY.crt" ]; then
        echo "Клиент с именем $ENTITY уже существует. Процесс создания прерван."
        exit 1
    fi
fi

# Создание директории, если не существует
sudo mkdir -p "$ENTITY_DIR"
sudo chmod 755 "$ENTITY_DIR"

EASY_RSA="/etc/easy-rsa"
cd "$EASY_RSA" || { echo "Ошибка: Не удалось перейти в директорию $EASY_RSA"; exit 1; }

# Функция для создания ключа и CSR
generate_key_and_csr() {
    if ./easyrsa --batch gen-req "$ENTITY" nopass && cp "pki/private/$ENTITY.key" "$ENTITY_DIR/$ENTITY.key"; then
        chmod 600 "$ENTITY_DIR/$ENTITY.key"
    else
        echo "Ошибка при создании ключа или CSR для $ENTITY"
        exit 1
    fi
}

# Функция для отправки и подписания CSR
sign_csr() {
    # Удаление старого CSR, если есть
    if ! ssh -i /home/"${CA_USER}"/.ssh/id_rsa_vpn_server "${CA_USER}@${CA_IP}" "cd ${CA_DIR} && rm -f pki/reqs/$ENTITY.req"; then
        echo "Не удалось удалить старый CSR на ЦС"
        exit 1
    fi
    # Отправка нового CSR
    if ! scp -i /home/"${CA_USER}"/.ssh/id_rsa_vpn_server "pki/reqs/$ENTITY.req" "${CA_USER}@${CA_IP}:${CA_DIR}/pki/reqs/"; then
        echo "Ошибка при отправке CSR на ЦС"
        exit 1
    fi
    # Подписание CSR
    if ! ssh -i /home/"${CA_USER}"/.ssh/id_rsa_vpn_server "${CA_USER}@${CA_IP}" "cd ${CA_DIR} && ./easyrsa --batch sign-req $ENTITY $ENTITY"; then
        echo "Ошибка при подписании сертификата для $ENTITY на ЦС"
        exit 1
    fi
}

# Функция для получения сертификатов
get_certificate() {
    if ! scp -i /home/"${CA_USER}"/.ssh/id_rsa_vpn_server "${CA_USER}@${CA_IP}:${CA_DIR}/pki/issued/$ENTITY.crt" "$ENTITY_DIR/$ENTITY.crt"; then
        echo "Ошибка при получении сертификата $ENTITY"
        exit 1
    fi
}

# Генерация ключа и CSR
generate_key_and_csr "$ENTITY"
# Отправка и подписание CSR
sign_csr "$ENTITY"
# Получение сертификата
get_certificate "$ENTITY"

if [ "$ENTITY" = "server" ]; then
    # Генерация TLS ключа для дополнительной защиты, если еще не существует
    if [ ! -f "$ENTITY_DIR/ta.key" ]; then
        if ! openvpn --genkey secret ta.key; then
            echo "Ошибка генерации TLS ключа"
            exit 1
        fi
        sudo cp ta.key "$ENTITY_DIR/ta.key"
    fi

    if ! scp -i /home/"${CA_USER}"/.ssh/id_rsa_vpn_server "${CA_USER}"@"${CA_IP}":"${CA_DIR}"/pki/ca.crt $ENTITY_DIR; then
        echo "Ошибка получения ca.crt для сервера"
        exit 1
    fi
fi

# Убедимся, что ca.crt и ta.key доступны как в серверной, так и в клиентской директориях
CLIENTS_DIR="/home/$CA_USER/clients/"
SERVER_DIR="/etc/openvpn/server"

# Копирование ca.crt, если он еще не скопирован
if [ ! -f "$CLIENTS_DIR/ca.crt" ]; then
    sudo cp "$SERVER_DIR/ca.crt" "$CLIENTS_DIR/ca.crt"
fi

# Копирование ta.key, если он еще не скопирован
if [ ! -f "$CLIENTS_DIR/ta.key" ]; then
    sudo cp "$SERVER_DIR/ta.key" "$CLIENTS_DIR/ta.key"
fi

echo "Операция завершена успешно для сущности: $ENTITY"
