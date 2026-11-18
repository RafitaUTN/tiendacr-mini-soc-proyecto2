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

# SSH is reachable through Vagrant's host-only port forward and from Kali.
ensure_rule "22/tcp on $nat_iface" allow in on "$nat_iface" from 10.0.2.2 to any port 22 proto tcp
ensure_rule "22/tcp on $lab_iface" allow in on "$lab_iface" from 10.10.10.30 to any port 22 proto tcp
# WAF is available only to the authorized attacker VM; the app container
# listens only on loopback port 3001.
ensure_rule "3000/tcp on $lab_iface" allow in on "$lab_iface" from 10.10.10.30 to 10.10.10.10 port 3000 proto tcp

if [ "$nat_iface" != enp0s3 ]; then
  ufw --force delete allow in on enp0s3 from 10.0.2.2 to any port 22 proto tcp >/dev/null || true
fi
if [ "$lab_iface" != enp0s8 ]; then
  ufw --force delete allow in on enp0s8 from 10.10.10.30 to any port 22 proto tcp >/dev/null || true
  ufw --force delete allow in on enp0s8 from 10.10.10.30 to 10.10.10.10 port 3000 proto tcp >/dev/null || true
fi

ufw --force enable

install -d -m 0755 /usr/local/sbin
install -m 0750 /vagrant/provisioning/target/tiendacr-docker-filter.sh \
  /usr/local/sbin/tiendacr-docker-filter.sh
cat > /etc/systemd/system/tiendacr-docker-filter.service <<'EOF'
[Unit]
Description=Restrict TiendaCR Juice Shop Docker traffic to Kali
Requires=docker.service
After=docker.service
PartOf=docker.service

[Service]
Type=oneshot
ExecStart=/usr/local/sbin/tiendacr-docker-filter.sh
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF
systemctl daemon-reload
systemctl enable --now tiendacr-docker-filter.service
