#!/usr/bin/env bash
set -euo pipefail

apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
  docker.io docker-compose suricata openssh-server

systemctl enable --now docker
systemctl enable --now ssh

install -d -m 0755 /opt/tiendacr/juice-shop
cp /vagrant/docker/juice-shop/docker-compose.yml /opt/tiendacr/juice-shop/docker-compose.yml
docker-compose -f /opt/tiendacr/juice-shop/docker-compose.yml up -d

suricata_iface="$(ip route show 10.10.10.0/24 | awk 'NR == 1 {for (i = 1; i <= NF; i++) if ($i == "dev") {print $(i + 1); exit}}')"
if [ -z "$suricata_iface" ]; then
  suricata_iface="$(ip -o link show | awk -F': ' '$2 != "lo" {print $2; exit}')"
fi
install -d -m 0755 /etc/suricata/rules
install -m 0644 /vagrant/suricata/rules/tiendacr.rules /etc/suricata/rules/suricata.rules
install -d -m 0755 /etc/systemd/system/suricata.service.d
cat > /etc/systemd/system/suricata.service.d/override.conf <<EOF
[Service]
Type=simple
ExecStart=
ExecStart=/usr/bin/suricata -c /etc/suricata/suricata.yaml -i $suricata_iface
Restart=on-failure
EOF
systemctl daemon-reload
suricata -T -c /etc/suricata/suricata.yaml -i "$suricata_iface"
systemctl enable --now suricata

if ! dpkg-query -W -f='${Status}' wazuh-agent 2>/dev/null | grep -q 'install ok installed'; then
  install -d -m 0755 /usr/share/keyrings
  if [ ! -s /usr/share/keyrings/wazuh.gpg ]; then
    curl -fsSL https://packages.wazuh.com/key/GPG-KEY-WAZUH \
      | gpg --batch --yes --dearmor -o /usr/share/keyrings/wazuh.gpg
  fi
  chmod 0644 /usr/share/keyrings/wazuh.gpg
  echo "deb [signed-by=/usr/share/keyrings/wazuh.gpg] https://packages.wazuh.com/4.x/apt/ stable main" \
    > /etc/apt/sources.list.d/wazuh.list
  apt-get update
  WAZUH_MANAGER="10.10.10.20" \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends wazuh-agent
fi

python3 - <<'PY'
from pathlib import Path

path = Path("/var/ossec/etc/ossec.conf")
text = path.read_text()
entries = [
    "  <localfile><log_format>json</log_format><location>/var/log/suricata/eve.json</location></localfile>",
    "  <localfile><log_format>syslog</log_format><location>/var/log/auth.log</location></localfile>",
]
for entry in entries:
    if entry not in text:
        text = text.replace("</ossec_config>", f"{entry}\n</ossec_config>")
path.write_text(text)
PY

systemctl enable --now wazuh-agent
bash /vagrant/provisioning/target/apply-hardening.sh
