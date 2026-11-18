#!/usr/bin/env bash
set -euo pipefail

backup_dir=/root/tiendacr-backups
install -d -m 0700 "$backup_dir"
for path in /etc/suricata/rules/suricata.rules /etc/ssh/sshd_config.d/99-tiendacr-security.conf /etc/ssh/sshd_config.d/00-tiendacr-security.conf /var/ossec/etc/ossec.conf; do
  if [ -e "$path" ]; then
    name="$(basename "$path")"
    if [ ! -e "$backup_dir/$name.before-project-hardening" ]; then
      cp -a "$path" "$backup_dir/$name.before-project-hardening"
    fi
  fi
done

install -d -m 0755 /opt/tiendacr/juice-shop
install -m 0644 /vagrant/docker/juice-shop/docker-compose.yml \
  /opt/tiendacr/juice-shop/docker-compose.yml
bash /vagrant/provisioning/target/deploy-waf.sh

install -d -m 0755 /etc/suricata/rules
install -m 0644 /vagrant/suricata/rules/tiendacr.rules \
  /etc/suricata/rules/suricata.rules
suricata_iface="$(ip route show 10.10.10.0/24 | awk 'NR == 1 {for (i = 1; i <= NF; i++) if ($i == "dev") {print $(i + 1); exit}}')"
suricata -T -c /etc/suricata/suricata.yaml -i "$suricata_iface"
systemctl restart suricata

install -o root -g wazuh -m 0750 \
  /vagrant/provisioning/target/tiendacr-docker-drop.py \
  /var/ossec/active-response/bin/tiendacr-docker-drop.py

python3 - <<'PY'
from pathlib import Path

path = Path("/var/ossec/etc/ossec.conf")
text = path.read_text()
entry = '    <directories check_all="yes" report_changes="yes" realtime="yes">/opt/tiendacr/fim-test</directories>'
lines = [line for line in text.splitlines() if "/opt/tiendacr/fim-test</directories>" not in line]
text = "\n".join(lines) + "\n"
marker = "  </syscheck>"
text = text.replace(marker, f"{entry}\n{marker}", 1)
path.write_text(text)
PY
install -d -o root -g wazuh -m 0750 /opt/tiendacr/fim-test

bash /vagrant/provisioning/common/ssh-hardening.sh
bash /vagrant/provisioning/target/firewall.sh
systemctl restart tiendacr-docker-filter.service
systemctl restart wazuh-agent
