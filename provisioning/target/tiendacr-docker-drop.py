#!/usr/bin/env python3

import sys
import json
import ipaddress
import subprocess
import tempfile
import os
from datetime import datetime
from pathlib import Path

LOG_FILE = Path("/var/ossec/logs/active-responses.log")
IPTABLES = "/usr/sbin/iptables"

# Configuracion exclusiva del laboratorio
LAB_NETWORK = ipaddress.ip_network("10.10.10.0/24")
SIEM_IP = ipaddress.ip_address("10.10.10.20")
TARGET_IP = ipaddress.ip_address("10.10.10.10")
GATEWAY_IP = ipaddress.ip_address("10.10.10.1")
WEB_PORT = "3000"

RULE_ID = "100100"
SURICATA_SID = "1000003"
COMMENT = "tiendacr-wazuh-sql100100"
STATE_DIR = Path("/var/ossec/var/tiendacr-active-response")


def log(message):
    timestamp = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    with LOG_FILE.open("a") as f:
        f.write(f"{timestamp} tiendacr-docker-drop: {message}\n")


def validate_ip(value):
    try:
        ip = ipaddress.ip_address(value)
    except (ValueError, TypeError):
        raise ValueError("IP de origen invalida")

    if ip.version != 4:
        raise ValueError("Solo se permiten direcciones IPv4")

    if ip not in LAB_NETWORK:
        raise ValueError("IP fuera de la red autorizada del laboratorio")

    if ip in (SIEM_IP, TARGET_IP, GATEWAY_IP):
        raise ValueError("IP protegida: SIEM o servidor objetivo")

    if (ip.is_loopback or ip.is_multicast or ip.is_unspecified
            or ip.is_link_local or ip.is_reserved):
        raise ValueError("Direccion IP no permitida")

    if ip in (LAB_NETWORK.network_address, LAB_NETWORK.broadcast_address):
        raise ValueError("Direccion de red o broadcast no permitida")

    return str(ip)


def get_alert_data(message):
    alert = message.get("parameters", {}).get("alert", {})

    rule_id = str(alert.get("rule", {}).get("id", ""))
    data = alert.get("data", {})

    signature_id = str(data.get("alert", {}).get("signature_id", ""))

    if rule_id != RULE_ID:
        raise ValueError("La alerta no corresponde a la regla 100100")

    if signature_id != SURICATA_SID:
        raise ValueError("El SID de Suricata no es el esperado")

    source_ip = validate_ip(data.get("src_ip"))

    return source_ip


def send_check_keys(source_ip):
    control_message = {
        "version": 1,
        "origin": {
            "name": "tiendacr-docker-drop.py",
            "module": "active-response"
        },
        "command": "check_keys",
        "parameters": {
            "keys": [source_ip]
        }
    }

    sys.stdout.write(json.dumps(control_message) + "\n")
    sys.stdout.flush()

    response_line = sys.stdin.readline()

    if not response_line:
        raise RuntimeError("No se recibio respuesta de wazuh-execd")

    response = json.loads(response_line)

    if response.get("command") != "continue":
        return False

    return True


def get_lab_interface():
    result = subprocess.run(
        ["/usr/sbin/ip", "route", "show", "10.10.10.0/24"],
        capture_output=True,
        text=True,
        timeout=5,
        check=True,
    )
    fields = result.stdout.split()
    if "dev" not in fields:
        raise RuntimeError("No se encontro la interfaz de la red de laboratorio")
    return fields[fields.index("dev") + 1]


def state_file(source_ip):
    return STATE_DIR / f"{source_ip.replace('.', '_')}.json"


def iptables_action(action, source_ip):
    STATE_DIR.mkdir(mode=0o750, parents=True, exist_ok=True)
    state_path = state_file(source_ip)

    if action == "-I":
        lab_interface = get_lab_interface()

        rule_args = [
            "-i", lab_interface,
            "-s", source_ip,
            "-d", str(TARGET_IP),
            "-p", "tcp",
            "--dport", WEB_PORT,
            "-m", "comment",
            "--comment", COMMENT,
            "-j", "DROP"
        ]

        check = subprocess.run(
            [IPTABLES, "-w", "5", "-C", "INPUT"] + rule_args,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        if check.returncode == 0:
            log(f"Regla preexistente para {source_ip}; no se reclama")
            return

        if state_path.exists():
            raise RuntimeError(
                f"Ya existe un estado para {source_ip}; "
                "se requiere revision manual"
            )

        state = {
            "source_ip": source_ip,
            "target_ip": str(TARGET_IP),
            "interface": lab_interface,
            "comment": COMMENT
        }

        fd, temporary_name = tempfile.mkstemp(
            prefix=f".{source_ip.replace('.', '_')}.",
            suffix=".tmp",
            dir=str(STATE_DIR)
        )
        temporary_path = Path(temporary_name)

        try:
            with os.fdopen(fd, "w") as state_file_handle:
                json.dump(state, state_file_handle)
                state_file_handle.flush()
                os.fsync(state_file_handle.fileno())

            temporary_path.replace(state_path)

            try:
                subprocess.run(
                    [IPTABLES, "-w", "5", "-I", "INPUT", "1"]
                    + rule_args,
                    check=True,
                    capture_output=True,
                    text=True
                )
            except Exception:
                state_path.unlink(missing_ok=True)
                raise

        finally:
            temporary_path.unlink(missing_ok=True)

        log(
            f"Bloqueo agregado: {source_ip} "
            f"hacia {TARGET_IP}:{WEB_PORT}"
        )

    elif action == "-D":
        if not state_path.exists():
            log(f"No existe estado de bloqueo para {source_ip}")
            return

        state = json.loads(state_path.read_text())

        if (state.get("source_ip") != source_ip
                or state.get("comment") != COMMENT):
            raise ValueError("El estado guardado no coincide")

        target_ip = str(ipaddress.ip_address(state["target_ip"]))

        if ipaddress.ip_address(target_ip) != TARGET_IP:
            raise ValueError("IP guardada no corresponde al servidor objetivo")
        lab_interface = get_lab_interface()
        if state.get("interface") != lab_interface:
            raise ValueError("La interfaz guardada no coincide con la red de laboratorio")

        rule_args = [
            "-i", lab_interface,
            "-s", source_ip,
            "-d", target_ip,
            "-p", "tcp",
            "--dport", WEB_PORT,
            "-m", "comment",
            "--comment", COMMENT,
            "-j", "DROP"
        ]

        check = subprocess.run(
            [IPTABLES, "-w", "5", "-C", "INPUT"] + rule_args,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        if check.returncode == 0:
            subprocess.run(
                [IPTABLES, "-w", "5", "-D", "INPUT"] + rule_args,
                check=True,
                capture_output=True,
                text=True
            )
            log(f"Bloqueo retirado: {source_ip}")
        else:
            log(f"La regla ya no existia para {source_ip}")

        state_path.unlink(missing_ok=True)

    else:
        raise ValueError(f"Accion iptables no permitida: {action}")


def main():
    line = sys.stdin.readline()

    if not line:
        raise ValueError("No se recibio mensaje JSON")

    message = json.loads(line)
    command = message.get("command")

    if command not in ("add", "delete"):
        raise ValueError(f"Comando no permitido: {command}")

    source_ip = get_alert_data(message)

    if command == "add":
        if not send_check_keys(source_ip):
            log(f"Respuesta cancelada por deduplicacion: {source_ip}")
            return

        iptables_action("-I", source_ip)

    elif command == "delete":
        iptables_action("-D", source_ip)


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        log(f"ERROR: {type(error).__name__}: {error}")
        sys.exit(1)
