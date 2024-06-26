#!/bin/bash

source /usr/bin/load_config.sh

ENTITY="$1"

# Проверяем, указан ли тип сущности
if [ -z "$ENTITY" ]; then
    echo "Не указан тип сущности (например, server или user1)"
    exit 1
fi

# Определение директории для сохранения ключей и сертификатов
ENTITY_DIR="/home/$CA_USER/clients/keys"
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
    # Определение типа сертификата на основе $ENTITY
    if [ "$ENTITY" = "server" ]; then
        CERT_TYPE="server"
    else
        CERT_TYPE="client"
    fi

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
    if ! ssh -i /home/"${CA_USER}"/.ssh/id_rsa_vpn_server "${CA_USER}@${CA_IP}" "cd ${CA_DIR} && ./easyrsa --batch sign-req $CERT_TYPE $ENTITY"; then
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

echo "Для $ENTITY успешно создан ключ и сертификат"
