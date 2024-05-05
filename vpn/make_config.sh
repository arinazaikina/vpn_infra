#!/bin/bash

# Первый аргумент: Идентификатор клиента
# Второй аргумент (необязательный): -m email@example.com

if [ -z "$1" ]; then
    echo "Необходимо указать идентификатор клиента как первый аргумент."
    exit 1
fi

EMAIL=
SEND_MAIL=false

if [ "$2" == "-m" ] && [ -n "$3" ]; then
    EMAIL="$3"
    SEND_MAIL=true
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
    "$KEY_DIR/ta.key" \
    <(echo -e '</tls-crypt>') \
    > "$OUTPUT_DIR/${1}.ovpn"

if [ "$SEND_MAIL" = true ]; then
    echo "Отправка конфигурации $1 на $EMAIL..."
    if echo "Конфигурация VPN для $1" | msmtp -a yandex -s "Конфигурация VPN для $1" -a "$OUTPUT_DIR/${1}.ovpn" "$EMAIL"; then
        echo "Конфигурация для $1 успешно отправлена на $EMAIL"
    else
        echo "Ошибка при отправке конфигурации для $1"
        exit 1
    fi
else
    if cat "$OUTPUT_DIR/${1}.ovpn"; then
        echo "Конфигурация для $1 успешно создана в $OUTPUT_DIR/${1}.ovpn"
    else
        echo "Ошибка при создании конфигурации для $1"
        exit 1
    fi
fi
