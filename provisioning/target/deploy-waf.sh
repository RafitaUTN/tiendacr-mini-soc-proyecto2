#!/usr/bin/env bash
set -euo pipefail

compose=/opt/tiendacr/juice-shop/docker-compose.yml
install -d -m 0755 /opt/tiendacr/juice-shop
install -m 0644 /vagrant/docker/juice-shop/docker-compose.yml "$compose"
docker-compose -f "$compose" config >/dev/null
# Compose v1 can fail when old containers retain incompatible metadata. Replace
# only this service's containers; its named lab-data volume remains intact.
old_containers="$(docker ps -aq --filter label=com.docker.compose.service=juice-shop)"
if [ -n "$old_containers" ]; then
  # shellcheck disable=SC2086
  docker rm -f $old_containers >/dev/null
fi
docker-compose -f "$compose" up -d

install -o root -g root -m 0644 /vagrant/provisioning/target/tiendacr-waf.py \
  /opt/tiendacr/tiendacr-waf.py
cat >/etc/systemd/system/tiendacr-waf.service <<'EOF'
[Unit]
Description=TiendaCR lab web application firewall reverse proxy
After=docker.service network-online.target
Requires=docker.service

[Service]
Type=simple
ExecStart=/usr/bin/python3 /opt/tiendacr/tiendacr-waf.py
Restart=on-failure
RestartSec=2
User=root
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/log

[Install]
WantedBy=multi-user.target
EOF
systemctl daemon-reload
systemctl enable tiendacr-waf.service
systemctl restart tiendacr-waf.service
for attempt in $(seq 1 60); do
  if curl -fsS --max-time 2 -o /dev/null http://10.10.10.10:3000/ >/dev/null 2>&1; then
    exit 0
  fi
  sleep 1
done
echo "WAF no respondio a la prueba local" >&2
exit 1
