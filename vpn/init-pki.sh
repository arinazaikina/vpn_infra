#!/bin/bash

# Путь к Easy-RSA
EASY_RSA="/etc/easy-rsa"
mkdir -p $EASY_RSA
ln -sf /usr/share/easy-rsa/* $EASY_RSA
chmod 700 "$EASY_RSA"
chown -R "$SUDO_USER":"$SUDO_USER" "$EASY_RSA"

# Инициализация PKI, если она еще не была выполнена
if [ ! -d "$EASY_RSA/pki" ]; then
    cd $EASY_RSA || { echo "Ошибка: Не удалось перейти в директорию $EASY_RSA"; exit 1; }
    ./easyrsa init-pki
    echo "PKI инициализирована в $EASY_RSA"
else
    echo "PKI уже инициализирована."
fi
