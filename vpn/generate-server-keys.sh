#!/bin/bash

# Определение переменных для настройки
EASY_RSA="/etc/easy-rsa"
OPENVPN_DIR="/etc/openvpn/server"
CA_USER="arina"
CA_IP="ca_ip_address"
CA_DIR="ca_directory"

# Переход в директорию Easy-RSA
cd $EASY_RSA || { echo "Ошибка: Не удалось перейти в директорию $EASY_RSA"; exit 1; }

# Генерация ключа и CSR для VPN-сервера
./easyrsa gen-req server nopass overwrite
cp "pki/private/server.key" $OPENVPN_DIR/

# Удаление старого CSR на ЦС перед копированием нового
if ! ssh ${CA_USER}@${CA_IP} "cd ${CA_DIR} && \
    echo 'Удаляю старый CSR, если он существует...' && \
    rm -f pki/reqs/server.req && \
    echo 'Старый CSR удалён.'"
then
    echo "Не удалось удалить старый CSR на удостоверяющем центре"
    exit 1
fi

# Отправка CSR на ЦС для подписи
if ! scp "pki/reqs/server.req" ${CA_USER}@${CA_IP}:${CA_DIR}/pki/reqs/
then
    echo "Ошибка отправки CSR на удостоверяющий центр"
    exit 1
fi

# Импорт и подписание CSR на ЦС
if ! ssh ${CA_USER}@${CA_IP} "cd ${CA_DIR} && \
    echo 'Подписываю CSR...' && \
    ./easyrsa sign-req server server"
then
    echo "Ошибка подписания сертификата на ЦС"
    exit 1
fi

# Получение подписанного сертификата и корневого CA сертификата
if ! scp ${CA_USER}@${CA_IP}:${CA_DIR}/pki/issued/server.crt $OPENVPN_DIR/server.crt
then
    echo "Ошибка получения подписанного сертификата server.crt"
    exit 1
fi

if ! scp ${CA_USER}@${CA_IP}:${CA_DIR}/pki/ca.crt $OPENVPN_DIR/ca.crt
then
    echo "Ошибка получения ca.crt"
    exit 1
fi

# Генерация TLS ключа для дополнительной защиты
if ! openvpn --genkey secret ta.key
then
    echo "Ошибка генерации TLS ключа"
    exit 1
fi
sudo cp ta.key $OPENVPN_DIR/

echo "Настройка VPN-сервера завершена."

