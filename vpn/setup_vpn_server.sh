#!/bin/bash

# Проверка и создание директории конфигурации OpenVPN, если необходимо
sudo mkdir -p /etc/openvpn/server/

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

echo "Настройка VPN-сервера завершена."
