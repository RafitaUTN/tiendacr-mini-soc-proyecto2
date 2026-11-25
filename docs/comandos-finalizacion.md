# Operación y demostración del Mini SOC

Comandos desde PowerShell en la raíz del repositorio. Ejecutar pruebas solo en
`tiendacr-lab`; iniciar y provisionar una máquina a la vez por la memoria del
host.

## 1. Arranque y estado

```powershell
vagrant validate
vagrant status
vagrant up siem
vagrant up target
vagrant up attacker
```

Para visualizar TiendaCR y el Dashboard en el navegador del host, usar los
túneles SSH locales y comandos de demostración de
[`../COMPROBACION_EN_VIVO.txt`](../COMPROBACION_EN_VIVO.txt). Los túneles
escuchan solo en `127.0.0.1` del host y no publican los servicios a la LAN.

## 2. Verificar salud

```powershell
vagrant ssh siem -c "sudo systemctl is-active wazuh-manager wazuh-indexer wazuh-dashboard filebeat"
vagrant ssh siem -c "sudo /var/ossec/bin/agent_control -lc"
vagrant ssh target -c "sudo systemctl is-active docker suricata wazuh-agent tiendacr-docker-filter.service tiendacr-waf.service"
vagrant ssh target -c "sudo docker ps --format '{{.Names}} {{.Status}}'"
vagrant ssh attacker -c "curl -sS -o /dev/null -w 'HTTP=%{http_code}\n' http://10.10.10.10:3000/"
```

## 3. Demostración de 10 minutos

1. Mostrar topología y las reglas de firewall; verificar agente `001 Active`.
2. Desde Kali escanear solo los puertos declarados:

   ```bash
   nmap -Pn -sT -p 22,3000 10.10.10.10
   ```

3. Ejecutar cinco conexiones SSH con un usuario ficticio y autenticación por
   llave (`BatchMode`) para demostrar el rechazo y correlación 100101. No
   habilitar contraseñas ni usar cuentas reales.
4. Enviar una única solicitud SQLi de laboratorio y mostrar WAF HTTP 403,
   SID 1000003, Wazuh 100100 y Active Response:

   ```bash
   curl -sS --max-time 8 -o /dev/null -w 'HTTP=%{http_code}\n' \
     'http://10.10.10.10:3000/rest/products/search?q=%27%20OR%201=1--'
   ```

5. Mostrar que Kali no alcanza temporalmente el servicio durante 180 segundos;
   esperar el timeout, repetir la SQLi para ver el 403 persistente del WAF y
   confirmar HTTP 200 en la página normal. No quitar manualmente la regla.
6. Mostrar el evento FIM 550 de la ruta `/opt/tiendacr/fim-test` y explicar el
   riesgo residual de mantener Juice Shop como aplicación intencionalmente
   vulnerable.

## 4. Revisar alertas y evidencias

```powershell
vagrant ssh siem -c "sudo tail -n 100 /var/ossec/logs/alerts/alerts.json"
vagrant ssh target -c "sudo grep -E '1000001|1000002|1000003|1000004' /var/log/suricata/fast.log | tail"
```

Los extractos guardados y sanitizados están en
[`../evidence/2026-11-18`](../evidence/2026-11-18/). Para regenerar los dos
JSONL filtrados desde las VM, ejecutar:

```powershell
vagrant ssh target -c "sudo python3 /vagrant/docs/capture_evidence.py target"
vagrant ssh siem -c "sudo python3 /vagrant/docs/capture_evidence.py siem"
```

## 5. Apagado y contingencia

Al terminar, `vagrant halt` para liberar RAM. Si una VM pierde conectividad,
usar `vagrant status` y revisar UFW/interfaz antes de cambiar reglas. Los
scripts de aplicación de hardening respaldan configuraciones previas bajo
`/root/tiendacr-backups` en las VM.
