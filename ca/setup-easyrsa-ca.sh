#!/bin/bash

# Создание рабочей директории для Easy-RSA и создание в ней символических ссылок
EASY_RSA_DIR=~/easy-rsa
mkdir -p "$EASY_RSA_DIR"
ln -s /usr/share/easy-rsa/* "$EASY_RSA_DIR/"

# Установка прав доступа
chmod 700 "$EASY_RSA_DIR"

# Путь к исходному файлу vars.example
VARS_EXAMPLE_FILE="$EASY_RSA_DIR/vars.example"

# Проверка существования файла vars.example и создание копии с именем vars
if [ -f "$VARS_EXAMPLE_FILE" ]; then
    cp "$VARS_EXAMPLE_FILE" "${EASY_RSA_DIR}/vars"
    echo "Файл vars.example скопирован в vars."
else
    echo "Файл vars.example не найден. Убедитесь, что Easy-RSA установлен и путь к файлу vars.example указан верно."
    exit 1
fi

# Путь к файлу vars
VARS_FILE="${EASY_RSA_DIR}/vars"

# Замена значений переменных в файле vars
sed -i 's/^#*set_var EASYRSA_REQ_COUNTRY.*/set_var EASYRSA_REQ_COUNTRY  "RU"/' "$VARS_FILE"
sed -i 's/^#*set_var EASYRSA_REQ_PROVINCE.*/set_var EASYRSA_REQ_PROVINCE  "Saint-Petersburg"/' "$VARS_FILE"
sed -i 's/^#*set_var EASYRSA_REQ_CITY.*/set_var EASYRSA_REQ_CITY  "Saint-Petersburg"/' "$VARS_FILE"
sed -i 's/^#*set_var EASYRSA_REQ_CITY.*/set_var EASYRSA_REQ_CITY  "Saint-Petersburg"/' "$VARS_FILE"
sed -i 's/^#*set_var EASYRSA_REQ_ORG.*/set_var EASYRSA_REQ_ORG  "Arina Zaikina"/' "$VARS_FILE"
sed -i 's/^#*set_var EASYRSA_REQ_EMAIL.*/set_var EASYRSA_REQ_EMAIL        "sav2405@gmail.com"/' "$VARS_FILE"
sed -i 's/^#*set_var EASYRSA_REQ_OU.*/set_var EASYRSA_REQ_OU  "IE"/' "$VARS_FILE"
sed -i 's/^#*set_var EASYRSA_ALGO.*/set_var EASYRSA_ALGO  ec/' "$VARS_FILE"
sed -i 's/^#*set_var EASYRSA_DIGEST.*/set_var EASYRSA_DIGEST  "sha512"/' "$VARS_FILE"


echo "Файл vars отредактирован."

# Переход в рабочую директорию
cd "$EASY_RSA_DIR" || exit 1

echo "Инициализация PKI"
./easyrsa --batch init-pki

echo "Создание корневого сертификата"
./easyrsa --batch build-ca nopass

echo "Удостоверяющий центр настроен."
