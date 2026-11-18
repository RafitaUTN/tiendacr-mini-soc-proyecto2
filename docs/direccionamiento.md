# Direccionamiento y reglas de firewall

## Red del laboratorio

| VM | Hostname | IP privada | Rol |
|---|---|---|---|
| `attacker` | `kali-linux-atacante` | `10.10.10.30/24` | Ataques controlados |
| `target` | `ubuntu-servidor-objetivo` | `10.10.10.10/24` | WAF, Juice Shop en loopback, Suricata y Wazuh Agent |
| `siem` | `ubuntu-servidor-siem` | `10.10.10.20/24` | Wazuh central |

`tiendacr-lab` es una red interna de VirtualBox. Las interfaces NAT se usan para
descargas y SSH local de Vagrant; no se usa bridging. La detección de interfaz
en los scripts se basa en rutas, no en nombres fijados.

## Reglas aplicadas

| Destino | Puerto / protocolo | Interfaz y origen permitido | Motivo | Riesgo mitigado |
|---|---|---|---|---|
| Objetivo | 22/TCP | NAT desde gateway Vagrant; privada desde `10.10.10.30` | Administración por llave y soporte del lab | Fuerza bruta/acceso remoto no autorizado |
| Objetivo | 3000/TCP | Privada desde `10.10.10.30` | Reverse proxy WAF hacia Juice Shop; patrones de SQLi/traversal/XSS bloqueados | Exposición de aplicación vulnerable |
| Objetivo | 3001/TCP | Solo loopback (`127.0.0.1`) | Upstream de Juice Shop, no accesible desde Kali ni otra VM | Acceso directo que evada el WAF |
| SIEM | 22/TCP | NAT desde gateway Vagrant; privada desde `10.10.10.30` | Administración por llave | Acceso administrativo no autorizado |
| SIEM | 443/TCP | Privada desde `10.10.10.30` | Dashboard HTTPS | Exposición del panel de monitoreo |
| SIEM | 1514/TCP y UDP | Privada desde `10.10.10.10` | Comunicación del agente Wazuh | Ingesta de telemetría desde fuentes arbitrarias |
| SIEM | 1515/TCP | Privada desde `10.10.10.10` | Registro de agentes según configuración del lab | Registro no autorizado de agentes |
| SIEM | 9200/TCP | Solo loopback (`127.0.0.1`) | Indexer interno | Acceso directo a índices |

UFW aplica `deny incoming` y `allow outgoing` en ambas VM. En `target`, UFW
también tiene `deny routed`; en `siem`, el reenvío aparece como
`disabled (routed)` y la máquina no actúa como router. El upstream Docker queda
ligado a loopback y el WAF escucha solo en la IP privada autorizada. Active
Response añade temporalmente un DROP en INPUT limitado a Kali, la interfaz del
laboratorio y TCP/3000; no bloquea SSH ni otros destinos. Las políticas siguen
el mínimo privilegio y denegación por defecto.

El acceso NAT de Vagrant es para administrar las VM desde el host local, no es
una regla de acceso desde Internet. Las IP `10.0.2.2` y la interfaz NAT son
específicas de la red de virtualización. El resultado observado se documenta en
[`estado-actual.md`](estado-actual.md); las reglas se pueden consultar con
`vagrant ssh target -c "sudo ufw status numbered"` y
`vagrant ssh siem -c "sudo ufw status numbered"`.
