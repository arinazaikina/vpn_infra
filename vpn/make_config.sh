#!/bin/bash

# Первый аргумент: Идентификатор клиента
if [ -z "$1" ]; then
    echo "Необходимо указать идентификатор клиента как первый аргумент."
    exit 1
fi

source /usr/bin/load_config.sh

/usr/bin/generate_vpn_keys.sh "${1}"

# Переменные путей
KEY_DIR="/home/$CA_USER/clients/keys"
OUTPUT_DIR="/home/$CA_USER/clients/files"
BASE_CONFIG="/home/$CA_USER/clients/base.conf"

# Проверка наличия необходимых файлов
for FILE in "$BASE_CONFIG" "${KEY_DIR}/ca.crt" "${KEY_DIR}/${1}.crt" "${KEY_DIR}/${1}.key" "${KEY_DIR}/ta.key"; do
    if [ ! -f "$FILE" ]; then
        echo "Не найден файл: $FILE"
        exit 1
    fi
done

# Создание выходной директории если не существует
if [ ! -d "$OUTPUT_DIR" ]; then
    mkdir -p "$OUTPUT_DIR"
    if ! mkdir -p "$OUTPUT_DIR"; then
        echo "Не удалось создать директорию: $OUTPUT_DIR"
        exit 1
    fi
fi

# Создание конфигурации OVPN
cat "$BASE_CONFIG" \
    <(echo -e '<ca>') \
    "$KEY_DIR/ca.crt" \
    <(echo -e '</ca>\n<cert>') \
    "$KEY_DIR/${1}.crt" \
    <(echo -e '</cert>\n<key>') \
    "$KEY_DIR/${1}.key" \
    <(echo -e '</key>\n<tls-crypt>') \
    <(echo -e '#tls-crypt ta.key') \
    <(echo -e '</tls-crypt>') \
    > "$OUTPUT_DIR/${1}.ovpn"

if cat "$OUTPUT_DIR/${1}.ovpn"; then
    echo "Конфигурация для $1 успешно создана в $OUTPUT_DIR/${1}.ovpn"
else
    echo "Ошибка при создании конфигурации для $1"
    exit 1
fi

# Отправка файла конфигурации через SSH
echo "Отправка файла конфигурации на удаленный сервер..."
if scp "$OUTPUT_DIR/${1}.ovpn" "$CA_USER@$LOCAL_HOST_IP:/home/$CA_USER/"; then
    echo "Файл успешно отправлен на вашу локальную машину в в директорию /home/$CA_USER/"
else
    echo "Ошибка при отправке файла на $LOCAL_HOST_IP"
    exit 1
fi
