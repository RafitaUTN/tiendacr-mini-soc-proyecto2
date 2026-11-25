#!/usr/bin/env bash
set -euo pipefail

backup_dir=/root/tiendacr-backups
install -d -m 0700 "$backup_dir"
for path in /var/ossec/etc/ossec.conf /var/ossec/etc/rules/local_rules.xml /etc/ssh/sshd_config.d/99-tiendacr-security.conf /etc/ssh/sshd_config.d/00-tiendacr-security.conf; do
  if [ -e "$path" ]; then
    name="$(basename "$path")"
    if [ ! -e "$backup_dir/$name.before-project-hardening" ]; then
      cp -a "$path" "$backup_dir/$name.before-project-hardening"
    fi
  fi
done

install -o root -g wazuh -m 0640 /vagrant/wazuh/manager/local_rules.xml \
  /var/ossec/etc/rules/local_rules.xml

# Use the verified CA and a dedicated least-privilege Indexer user. The
# generated password is retained only in the Wazuh manager keystore.
test -s /etc/filebeat/certs/root-ca.pem
install -d -o root -g wazuh -m 0750 /var/ossec/etc/certs
install -o root -g wazuh -m 0640 /etc/filebeat/certs/root-ca.pem \
  /var/ossec/etc/certs/root-ca.pem
bash /vagrant/provisioning/siem/configure-manager-indexer-user.sh

python3 - <<'PY'
from pathlib import Path

path = Path("/var/ossec/etc/ossec.conf")
text = path.read_text()
text = text.replace("/etc/filebeat/certs/root-ca.pem", "/var/ossec/etc/certs/root-ca.pem")
text = text.replace("      <certificate>/etc/filebeat/certs/wazuh-server.pem</certificate>\n", "")
text = text.replace("      <key>/etc/filebeat/certs/wazuh-server-key.pem</key>\n", "")
text = text.replace("      <certificate>/var/ossec/etc/certs/wazuh-server.pem</certificate>\n", "")
text = text.replace("      <key>/var/ossec/etc/certs/wazuh-server-key.pem</key>\n", "")
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

# The local SIEM VM shares limited host resources with the target and attacker.
# Give Wazuh Dashboard API requests 60 seconds during startup/feed evaluation;
# the default 20 seconds can expire while the Manager is busy correlating data.
dashboard_config=/usr/share/wazuh-dashboard/data/wazuh/config/wazuh.yml
if [ -f "$dashboard_config" ]; then
  if [ ! -e "$backup_dir/wazuh-dashboard-wazuh.yml.before-api-timeout" ]; then
    cp -a "$dashboard_config" "$backup_dir/wazuh-dashboard-wazuh.yml.before-api-timeout"
  fi
  python3 - <<'PY'
from pathlib import Path
import re

path = Path("/usr/share/wazuh-dashboard/data/wazuh/config/wazuh.yml")
text = path.read_text()
if re.search(r"(?m)^\s*timeout:\s*\d+\s*$", text):
    text = re.sub(r"(?m)^\s*timeout:\s*\d+\s*$", "timeout: 60000", text, count=1)
elif re.search(r"(?m)^#\s*timeout:\s*\d+\s*$", text):
    text = re.sub(r"(?m)^#\s*timeout:\s*\d+\s*$", "timeout: 60000", text, count=1)
else:
    text = "timeout: 60000\n" + text
path.write_text(text)
PY
fi

/var/ossec/bin/wazuh-analysisd -t
systemctl restart wazuh-manager
systemctl enable --now wazuh-indexer wazuh-dashboard
systemctl restart wazuh-dashboard

if [ -s /etc/filebeat/filebeat.yml ]; then
  filebeat test config -e
  filebeat test output -e
  systemctl enable --now filebeat
fi

bash /vagrant/provisioning/common/ssh-hardening.sh
bash /vagrant/provisioning/siem/firewall.sh
