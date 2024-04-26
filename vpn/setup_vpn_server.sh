#!/bin/bash

source /usr/bin/load_config.sh

/usr/bin/generate_vpn_keys.sh server

# Генерация TLS ключа для дополнительной защиты
if ! openvpn --genkey secret ta.key; then
    echo "Ошибка генерации TLS ключа"
    exit 1
fi
sudo cp ta.key /etc/openvpn/server/

# Получение ca.crt
if ! scp -i /home/"${CA_USER}"/.ssh/id_rsa_vpn_server "${CA_USER}"@"${CA_IP}":"${CA_DIR}"/pki/ca.crt /etc/openvpn/server/; then
   echo "Ошибка получения ca.crt"
   exit 1
fi

# Конфигурация сервера OpenVPN
sudo bash -c 'cat <<EOF > /etc/openvpn/server/server.conf
port 1194
proto udp
dev tun
ca ca.crt
cert server.crt
key server.key
dh none
tls-crypt ta.key
cipher AES-256-GCM
auth SHA256
server 10.8.0.0 255.255.255.0
keepalive 10 120
persist-key
persist-tun
status /var/log/openvpn/openvpn-status.log
verb 3
user nobody
group nogroup
push "redirect-gateway def1 bypass-dhcp"
ifconfig-pool-persist /var/log/openvpn/ipp.txt
explicit-exit-notify 1
EOF'

echo "Конфигурация сервера OpenVPN создана в /etc/openvpn/server/server.conf."
sudo chmod 600 /etc/openvpn/server/{server.key,ca.crt,server.crt,ta.key}

# Включение IP-проброса
if ! sudo grep -q '^net.ipv4.ip_forward = 1$' /etc/sysctl.conf; then
    sudo sh -c 'echo "net.ipv4.ip_forward = 1" >> /etc/sysctl.conf'
fi
sudo sysctl -p

# Запуск и включение OpenVPN
sudo systemctl start openvpn-server@server.service
sudo systemctl enable openvpn-server@server.service

echo "Настройка VPN-сервера завершена"
