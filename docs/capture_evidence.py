#!/usr/bin/env python3
"""Write minimal, sanitized Mini SOC lab evidence into the Vagrant shared folder."""
import json
import sys
from datetime import datetime
from pathlib import Path

role = sys.argv[1]
root = Path("/vagrant")
out = root / "evidence" / "2026-11-18"
out.mkdir(parents=True, exist_ok=True)

def read_jsonl(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            for line in f:
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    continue
    except FileNotFoundError:
        return

if role == "siem":
    wanted_ids = {"100100", "100101", "100102", "550"}
    wanted_sids = {"1000001", "1000002", "1000003", "1000004"}
    selected = []
    seen = set()
    for event in read_jsonl("/var/ossec/logs/alerts/alerts.json"):
        rule = event.get("rule", {})
        data = event.get("data", {})
        alert = data.get("alert", {}) if isinstance(data, dict) else {}
        rid = str(rule.get("id", ""))
        sid = str(alert.get("signature_id", ""))
        if rid not in wanted_ids:
            continue
        key = (rid, event.get("agent", {}).get("name"))
        if key in seen:
            continue
        seen.add(key)
        item = {
            "timestamp": event.get("timestamp"),
            "rule_id": rid,
            "description": rule.get("description"),
            "agent": event.get("agent", {}).get("name"),
        }
        source = data.get("srcip") or data.get("src_ip")
        if source:
            item["source_ip"] = source
        if sid:
            item["suricata_sid"] = sid
            item["signature"] = alert.get("signature")
        syscheck = event.get("syscheck") or {}
        if syscheck.get("path"):
            item["file"] = syscheck["path"]
        selected.append(item)
    (out / "wazuh-alerts.jsonl").write_text(
        "".join(json.dumps(x, ensure_ascii=False) + "\n" for x in selected),
        encoding="utf-8",
    )
elif role == "target":
    wanted_sids = {1000001, 1000002, 1000003, 1000004}
    selected = []
    seen = set()
    for event in read_jsonl("/var/log/suricata/eve.json"):
        alert = event.get("alert", {})
        sid = alert.get("signature_id")
        if event.get("event_type") != "alert" or sid not in wanted_sids:
            continue
        if sid in seen:
            continue
        seen.add(sid)
        http = event.get("http", {})
        item = {
            "timestamp": event.get("timestamp"),
            "sid": sid,
            "signature": alert.get("signature"),
            "source_ip": event.get("src_ip"),
            "destination_ip": event.get("dest_ip"),
            "destination_port": event.get("dest_port"),
        }
        if http:
            item["http_method"] = http.get("http_method")
            item["http_url"] = http.get("url")
            item["http_status"] = http.get("status")
        selected.append(item)
    (out / "suricata-alerts.jsonl").write_text(
        "".join(json.dumps(x, ensure_ascii=False) + "\n" for x in selected),
        encoding="utf-8",
    )
    log = Path("/var/ossec/logs/active-responses.log")
    current_lines = [
        line for line in log.read_text(encoding="utf-8", errors="replace").splitlines()
        if line.startswith("2026/11/18 ") and "tiendacr-docker-drop" in line
    ] if log.exists() else []
    (out / "active-response.txt").write_text("\n".join(current_lines) + "\n", encoding="utf-8")
else:
    raise SystemExit("role must be siem or target")

print(f"wrote {len(selected)} sanitized records to {out}")
