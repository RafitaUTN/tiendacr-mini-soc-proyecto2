#!/usr/bin/env bash
set -euo pipefail

hostname="$1"

hostnamectl set-hostname "$hostname"

install -d -m 0755 /opt/tiendacr /etc/hosts.d

case "$hostname" in
  kali-linux-atacante) lab_ip="10.10.10.30" ;;
  ubuntu-servidor-objetivo) lab_ip="10.10.10.10" ;;
  ubuntu-servidor-siem) lab_ip="10.10.10.20" ;;
  *) echo "Hostname no reconocido: $hostname" >&2; exit 1 ;;
esac

default_iface="$(ip route show default | awk 'NR == 1 {print $5}')"
lab_iface=""
for iface in $(ip -o link show | awk -F': ' '$2 != "lo" {print $2}'); do
  if [ "$iface" != "$default_iface" ]; then
    lab_iface="$iface"
    break
  fi
done
if [ -z "$lab_iface" ]; then
  echo "No se encontró la interfaz de laboratorio para $hostname" >&2
  exit 1
fi

ip addr del "$lab_ip/24" dev "$default_iface" 2>/dev/null || true
ip link set "$lab_iface" up
ip addr replace "$lab_ip/24" dev "$lab_iface"

cat > /etc/systemd/system/tiendacr-private-network.service <<EOF
[Unit]
Description=Configure TiendaCR private laboratory network
After=network-pre.target
Before=network.target

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/sbin/ip link set $lab_iface up
ExecStart=/sbin/ip addr replace $lab_ip/24 dev $lab_iface

[Install]
WantedBy=multi-user.target
EOF
systemctl daemon-reload
systemctl enable tiendacr-private-network.service
systemctl start tiendacr-private-network.service

cat > /etc/hosts.d/tiendacr-lab <<'EOF'
10.10.10.10 ubuntu-servidor-objetivo
10.10.10.20 ubuntu-servidor-siem
10.10.10.30 kali-linux-atacante
EOF

if ! grep -q 'tiendacr-lab' /etc/hosts; then
  cat /etc/hosts.d/tiendacr-lab >> /etc/hosts
fi

apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
  ca-certificates curl jq ufw
