#!/usr/bin/env bash
set -euo pipefail

ufw default deny incoming
ufw default allow outgoing
ufw default deny routed

nat_iface="$(ip route show default | awk 'NR == 1 {print $5}')"
lab_iface="$(ip route show 10.10.10.0/24 | awk 'NR == 1 {for (i = 1; i <= NF; i++) if ($i == "dev") {print $(i + 1); exit}}')"
[ -n "$nat_iface" ] && [ -n "$lab_iface" ]

ensure_rule() {
  local status_fragment="$1"
  shift
  if ! ufw status | grep -Fq -- "$status_fragment"; then
    ufw "$@"
  fi
}

# Vagrant administration through the NAT port-forward and the authorized lab.
ensure_rule "22/tcp on $nat_iface" allow in on "$nat_iface" from 10.0.2.2 to any port 22 proto tcp
ensure_rule "22/tcp on $lab_iface" allow in on "$lab_iface" from 10.10.10.30 to any port 22 proto tcp
# Only the objective may send Wazuh agent traffic.
ensure_rule "1514/tcp on $lab_iface" allow in on "$lab_iface" from 10.10.10.10 to 10.10.10.20 port 1514 proto tcp
ensure_rule "1514/udp on $lab_iface" allow in on "$lab_iface" from 10.10.10.10 to 10.10.10.20 port 1514 proto udp
ensure_rule "1515/tcp on $lab_iface" allow in on "$lab_iface" from 10.10.10.10 to 10.10.10.20 port 1515 proto tcp
# The dashboard is exposed only to Kali and Vagrant's local tunnel endpoint.
ensure_rule "443/tcp on $lab_iface" allow in on "$lab_iface" from 10.10.10.30 to 10.10.10.20 port 443 proto tcp
ensure_rule "443/tcp on $nat_iface" allow in on "$nat_iface" from 10.0.2.2 to any port 443 proto tcp

if [ "$nat_iface" != enp0s3 ]; then
  ufw --force delete allow in on enp0s3 from 10.0.2.2 to any port 22 proto tcp >/dev/null || true
  ufw --force delete allow in on enp0s3 from 10.0.2.2 to any port 443 proto tcp >/dev/null || true
fi
if [ "$lab_iface" != enp0s8 ]; then
  ufw --force delete allow in on enp0s8 from 10.10.10.30 to any port 22 proto tcp >/dev/null || true
  ufw --force delete allow in on enp0s8 from 10.10.10.10 to 10.10.10.20 port 1514 proto tcp >/dev/null || true
  ufw --force delete allow in on enp0s8 from 10.10.10.10 to 10.10.10.20 port 1514 proto udp >/dev/null || true
  ufw --force delete allow in on enp0s8 from 10.10.10.10 to 10.10.10.20 port 1515 proto tcp >/dev/null || true
  ufw --force delete allow in on enp0s8 from 10.10.10.30 to 10.10.10.20 port 443 proto tcp >/dev/null || true
fi

ufw --force enable
