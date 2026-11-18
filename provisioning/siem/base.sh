#!/usr/bin/env bash
set -euo pipefail

apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
  openssh-server curl gnupg apt-transport-https

systemctl enable --now ssh

install -d -m 0755 \
  /etc/systemd/system/wazuh-indexer.service.d \
  /etc/systemd/system/wazuh-manager.service.d
cat > /etc/systemd/system/wazuh-indexer.service.d/timeout.conf <<'EOF'
[Service]
TimeoutStartSec=10min
TimeoutStopSec=10min
EOF
cat > /etc/systemd/system/wazuh-manager.service.d/timeout.conf <<'EOF'
[Service]
TimeoutStartSec=10min
TimeoutStopSec=10min
EOF
systemctl daemon-reload

if [ ! -x /var/ossec/bin/wazuh-control ]; then
  install -d -m 0755 /opt/tiendacr/wazuh
  cd /opt/tiendacr/wazuh
  curl -fsSLO https://packages.wazuh.com/4.14/wazuh-install.sh
  chmod 0755 wazuh-install.sh
  bash ./wazuh-install.sh -a
fi

if [ -f /vagrant/wazuh/manager/local_rules.xml ]; then
  install -o root -g wazuh -m 0640 /vagrant/wazuh/manager/local_rules.xml /var/ossec/etc/rules/local_rules.xml
fi

python3 - <<'PY'
from pathlib import Path

path = Path("/var/ossec/etc/ossec.conf")
text = path.read_text()
command = """  <command>
    <name>tiendacr-docker-drop</name>
    <executable>tiendacr-docker-drop.py</executable>
    <timeout_allowed>yes</timeout_allowed>
  </command>

"""
response = """  <active-response>
    <disabled>no</disabled>
    <command>tiendacr-docker-drop</command>
    <location>defined-agent</location>
    <agent_id>001</agent_id>
    <rules_id>100100</rules_id>
    <timeout>180</timeout>
  </active-response>

"""
if "<name>tiendacr-docker-drop</name>" not in text:
    text = text.replace("</ossec_config>", command + "</ossec_config>")
if "<command>tiendacr-docker-drop</command>" not in text:
    text = text.replace("</ossec_config>", response + "</ossec_config>")
path.write_text(text)
PY

filebeat_config="/etc/filebeat/filebeat.yml"
if [ -s "$filebeat_config" ]; then
  filebeat test config -e
fi

systemctl enable --now wazuh-manager wazuh-indexer wazuh-dashboard
bash /vagrant/provisioning/siem/apply-hardening.sh
