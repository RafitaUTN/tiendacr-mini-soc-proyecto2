#!/usr/bin/env bash
set -euo pipefail

api=https://127.0.0.1:9200
cert=/etc/wazuh-indexer/certs/admin.pem
key=/etc/wazuh-indexer/certs/admin-key.pem
ca=/etc/wazuh-indexer/certs/root-ca.pem
user=tiendacr_manager_indexer
role=tiendacr_manager_indexer
work="$(mktemp -d /dev/shm/tiendacr-indexer-user.XXXXXX)"
chmod 0700 "$work"
trap 'rm -rf "$work"' EXIT
password="$(openssl rand -hex 32)"

cat > "$work/role.json" <<'JSON'
{"cluster_permissions":["cluster_monitor","cluster_manage_index_templates"],"index_permissions":[{"index_patterns":["wazuh-states-*"],"allowed_actions":["crud","create_index"]}]}
JSON
printf '{"password":"%s"}\n' "$password" > "$work/user.json"
chmod 0600 "$work/user.json"
cat > "$work/mapping.json" <<JSON
{"users":["$user"],"backend_roles":[],"hosts":[]}
JSON

curl -fsS --cacert "$ca" --cert "$cert" --key "$key" \
  -H 'Content-Type: application/json' -X PUT \
  --data-binary "@$work/role.json" \
  "$api/_plugins/_security/api/roles/$role" >/dev/null
curl -fsS --cacert "$ca" --cert "$cert" --key "$key" \
  -H 'Content-Type: application/json' -X PUT \
  --data-binary "@$work/user.json" \
  "$api/_plugins/_security/api/internalusers/$user" >/dev/null
curl -fsS --cacert "$ca" --cert "$cert" --key "$key" \
  -H 'Content-Type: application/json' -X PUT \
  --data-binary "@$work/mapping.json" \
  "$api/_plugins/_security/api/rolesmapping/$role" >/dev/null

printf '%s\n' "$user" | /var/ossec/bin/wazuh-keystore -f indexer -k username >/dev/null
printf '%s\n' "$password" | /var/ossec/bin/wazuh-keystore -f indexer -k password >/dev/null
printf 'dedicated_user_auth_http='
curl -sS --cacert "$ca" --user "$user:$password" -o /dev/null \
  -w '%{http_code}\n' "$api/_plugins/_security/api/account"
unset password
echo 'Dedicated indexer user configured; password retained only in manager keystore.'
