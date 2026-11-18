#!/usr/bin/env python3
"""Read Wazuh Indexer package/vulnerability counts for agents 000 and 001."""
import json
import ssl
import urllib.error
import urllib.request

BASE = "https://127.0.0.1:9200"
CERT = "/etc/wazuh-indexer/certs/admin.pem"
KEY = "/etc/wazuh-indexer/certs/admin-key.pem"
context = ssl.create_default_context(cafile="/etc/wazuh-indexer/certs/root-ca.pem")
context.load_cert_chain(CERT, KEY)

for index in ("wazuh-states-inventory-packages-*", "wazuh-states-vulnerabilities-*"):
    for agent_id in ("000", "001"):
        body = json.dumps({"query": {"term": {"agent.id": agent_id}}}).encode()
        request = urllib.request.Request(
            f"{BASE}/{index}/_count",
            data=body,
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(request, context=context, timeout=15) as response:
                result = json.load(response)
            print(f"{index} agent={agent_id} count={result['count']}")
        except urllib.error.HTTPError as error:
            print(f"{index} agent={agent_id} HTTP={error.code} {error.read().decode(errors='replace')}")

body = json.dumps({"size": 1, "query": {"term": {"agent.id": "001"}}}).encode()
request = urllib.request.Request(
    f"{BASE}/wazuh-states-vulnerabilities-*/_search",
    data=body,
    headers={"Content-Type": "application/json"},
)
with urllib.request.urlopen(request, context=context, timeout=15) as response:
    hits = json.load(response)["hits"]["hits"]
if hits:
    source = hits[0]["_source"]
    print("Sample vulnerability document:")
    print(json.dumps(source, indent=2))
