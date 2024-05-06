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
    # Подготовка письма и отправка
    subject="VPN конфигурация для ${1}"
    filename="$OUTPUT_DIR/${1}.ovpn"
    basename=$(basename "$filename")
    tempfile="/tmp/email-$$.txt"

    echo "From: arina.viejo@yandex.ru
To: $EMAIL
Subject: $subject
MIME-Version: 1.0
Content-Type: multipart/mixed; boundary=\"sep\"

--sep
Content-Type: text/plain; charset=\"UTF-8\"
Content-Transfer-Encoding: 8bit

Привет!

Файл конфигурации VPN находится во вложении.

--sep
Content-Type: application/x-openvpn-profile; name=\"$basename\"
Content-Disposition: attachment; filename=\"$basename\"
Content-Transfer-Encoding: base64" > "$tempfile"

    base64 "$filename" >> "$tempfile"
    echo "--sep--" >> "$tempfile"

    # Отправка письма
    if ! msmtp -a yandex "$EMAIL" < "$tempfile"; then
        echo "Ошибка при отправке конфигурации для $1"
        rm "$tempfile"
        exit 1
    else
        echo "Конфигурация для $1 успешно отправлена на $EMAIL"
    fi

    # Удаление временного файла
    rm "$tempfile"
else
    if [ -f "$OUTPUT_DIR/${1}.ovpn" ]; then
        echo "Конфигурация для $1 успешно создана в $OUTPUT_DIR/${1}.ovpn"
    else
        echo "Ошибка при создании конфигурации для $1"
        exit 1
    fi
fi
