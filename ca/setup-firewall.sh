#!/bin/bash

# Определение директории для бэкапов
BACKUP_DIR="/root/iptables_backups"
mkdir -p "${BACKUP_DIR}"

# Создание бэкапа текущих правил iptables
BACKUP_FILE="iptables-$(date +%Y-%m-%d_%H-%M-%S).bak"
iptables-save > "${BACKUP_DIR}/${BACKUP_FILE}"
echo "Текущие правила iptables сохранены в ${BACKUP_DIR}/${BACKUP_FILE}"

# Очистка текущих правил
iptables -F
iptables -t nat -F
iptables -t mangle -F
iptables -X

# Политика по умолчанию: отбрасывать все входящие и перенаправленные соединения, разрешить исходящие
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT

# Разрешение локального трафика и установленных соединений
iptables -A INPUT -i lo -j ACCEPT
iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT


# Считывание IP-адресов из файла конфигурации
source /etc/myvpn/ip_addresses.conf
IFS=',' read -r -a VPN_IPS <<< "$VPN_IPS"

# Разрешение SSH для локального IP и списка VPN IP
iptables -A INPUT -p tcp --dport 22 -s "$LOCAL_IP" -j ACCEPT
for IP in "${VPN_IPS[@]}"; do
    iptables -A INPUT -p tcp --dport 22 -s "$IP" -j ACCEPT
done

# Сохранение изменённых правил iptables
iptables-save > /etc/iptables/rules.v4

echo "Новые правила iptables применены и сохранены."
