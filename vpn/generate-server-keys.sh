#!/bin/bash

# Путь к конфигурационному файлу
CONFIG_FILE="/etc/myvpn/vpn_config.conf"

# Чтение конфигурационного файла, если он существует
# shellcheck source=/etc/myvpn/vpn_config.conf
if [ -f "$CONFIG_FILE" ]; then
    source "$CONFIG_FILE"
else
    echo "Конфигурационный файл не найден: $CONFIG_FILE"
    exit 1
fi

# Проверяем, заданы ли необходимые переменные
if [ -z "$CA_USER" ] || [ -z "$CA_IP" ] || [ -z "$CA_DIR" ] || [ -z "$ETH_INTERFACE" ]; then
    echo "Конфигурационный файл не содержит необходимых настроек (CA_USER, CA_IP, CA_DIR, ETH_INTERFACE)."
    exit 1
fi

echo "Используется конфигурация:"
echo "Пользователь удостоверяющего центра: $CA_USER"
echo "IP удостоверяющего центра: $CA_IP"
echo "Директория Easy-RSA на ЦС: $CA_DIR"
echo "Сетевой интерфейс: $ETH_INTERFACE"

# Проверка и создание каталога /etc/openvpn/server, если он не существует
if [ ! -d /etc/openvpn/server ]; then
    sudo mkdir -p /etc/openvpn/server
    sudo chmod 755 /etc/openvpn/server
    echo "Создан каталог: /etc/openvpn/server"
fi

# Генерация ключа и CSR для VPN-сервера
EASY_RSA="/etc/easy-rsa"
cd "$EASY_RSA" || { echo "Ошибка: Не удалось перейти в директорию $EASY_RSA"; exit 1; }
./easyrsa --batch gen-req server nopass
cp "pki/private/server.key" /etc/openvpn/server/


if ! ssh -i /home/"${CA_USER}"/.ssh/id_rsa_vpn_server "${CA_USER}@${CA_IP}" "cd ${CA_DIR} && \
    if [ -f pki/reqs/server.req ]; then \
        echo 'Найден старый CSR, удаляю...'; \
        rm -f pki/reqs/server.req; \
        echo 'Старый CSR удалён.'; \
    fi"
then
    echo "Не удалось выполнить операции на удостоверяющем центре"
    exit 1
fi

# Отправка CSR на ЦС для подписи
if ! scp -i /home/"${CA_USER}"/.ssh/id_rsa_vpn_server "pki/reqs/server.req" "${CA_USER}"@"${CA_IP}":"${CA_DIR}"/pki/reqs/; then
    echo "Ошибка отправки CSR на удостоверяющий центр"
    exit 1
fi


# Импорт и подписание CSR на ЦС
if ! ssh -i /home/"${CA_USER}"/.ssh/id_rsa_vpn_server "${CA_USER}"@"${CA_IP}" "cd ${CA_DIR} && echo 'Подписываю CSR...' && ./easyrsa --batch sign-req server server"; then
    echo "Ошибка подписания сертификата на ЦС"
    exit 1
fi

# Получение подписанного сертификата server.crt
if ! scp -i /home/"${CA_USER}"/.ssh/id_rsa_vpn_server "${CA_USER}"@"${CA_IP}":"${CA_DIR}"/pki/issued/server.crt /etc/openvpn/server/server.crt; then
    echo "Ошибка получения подписанного сертификата server.crt"
    exit 1
fi

# Получение ca.crt
if ! scp -i /home/"${CA_USER}"/.ssh/id_rsa_vpn_server "${CA_USER}"@"${CA_IP}":"${CA_DIR}"/pki/ca.crt /etc/openvpn/server/; then
   echo "Ошибка получения ca.crt"
   exit 1
fi

# Генерация TLS ключа для дополнительной защиты
if ! openvpn --genkey secret ta.key; then
    echo "Ошибка генерации TLS ключа"
    exit 1
fi
sudo cp ta.key /etc/openvpn/server/
