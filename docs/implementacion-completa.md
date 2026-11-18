# Implementacion completa del Mini SOC TiendaCR

> Estado medido el 18-11-2026: las tres VMs activas; Manager, Indexer,
> Dashboard, Filebeat y agente 001 activos. El WAF bloqueó los payloads SQLi y
> traversal probados incluso tras expirar Active Response. Wazuh detectó SSH,
> ataques web y FIM desde Kali. Evidencia en `../evidence/2026-11-18/`.

## 1. Objetivo

El proyecto implementa un laboratorio Mini SOC para TiendaCR con tres maquinas
virtuales separadas:

- Kali Linux para pruebas autorizadas.
- Ubuntu Server como objetivo con OWASP Juice Shop y Suricata.
- Ubuntu Server como SIEM central con Wazuh.

La separacion evita mezclar el atacante, el servicio vulnerable y la
monitorizacion. Las pruebas deben ejecutarse solamente dentro de la red privada
del laboratorio.

## 2. Entorno del equipo anfitrion

- Sistema: Windows 11 Pro de 64 bits.
- CPU: Intel Core i5-12450H.
- Memoria fisica: aproximadamente 16 GiB.
- VirtualBox: 7.2.2.
- Vagrant: 2.4.9.
- Extension Pack detectado: 7.2.14; debe alinearse con la version de
  VirtualBox si se requieren funciones adicionales.
- Espacio disponible limitado en la unidad del sistema.

Debido a la memoria disponible, el SIEM usa 6 GiB y las maquinas deben
encenderse y aprovisionarse por etapas. Wazuh recomienda mas memoria para una
instalacion all-in-one de produccion; este laboratorio se mantiene como entorno
academico controlado.

## 3. Infraestructura implementada

La infraestructura declarativa esta en el [Vagrantfile](../Vagrantfile).

| Funcion | Nombre VirtualBox | Hostname | IP privada | SSH local |
|---|---|---|---|---|
| Atacante | `Kali-Linux-Atacante` | `kali-linux-atacante` | `10.10.10.30` | `2201` |
| Objetivo | `Ubuntu-Servidor-Objetivo` | `ubuntu-servidor-objetivo` | `10.10.10.10` | `2202` |
| SIEM | `Ubuntu-Servidor-SIEM` | `ubuntu-servidor-siem` | `10.10.10.20` | `2203` |

La red privada es la red interna de VirtualBox `tiendacr-lab`. Cada maquina
tambien conserva una interfaz NAT para actualizaciones, descargas y acceso SSH
de Vagrant. No se usa bridging y no se expone Juice Shop en la interfaz NAT.

## 4. Aprovisionamiento creado

### Archivos principales

- [Vagrantfile](../Vagrantfile): define cajas, nombres, IPs, puertos y recursos.
- [base.sh comun](../provisioning/common/base.sh): hostname, `/etc/hosts`, red
  privada, utilidades y UFW.
- [base.sh atacante](../provisioning/attacker/base.sh): Nmap, Curl, jq y SSH.
- [base.sh objetivo](../provisioning/target/base.sh): Docker, Juice Shop,
  WAF, Suricata y agente Wazuh.
- [base.sh SIEM](../provisioning/siem/base.sh): dependencias e instalacion
  oficial de Wazuh.
- [docker-compose de Juice Shop](../docker/juice-shop/docker-compose.yml):
  upstream de Juice Shop ligado a `127.0.0.1:3001` detrás del WAF.
- [WAF de laboratorio](../provisioning/target/tiendacr-waf.py): proxy en la IP
  privada del target; bloquea patrones probados de SQLi, traversal y XSS.
- [reglas Wazuh](../wazuh/manager/local_rules.xml): SQLi, traversal y umbral
  de cinco eventos SSH en 120 segundos.
- [reglas Suricata](../suricata/rules/tiendacr.rules): conexión de Juice Shop,
  SYN SSH, SQLi `%27` y traversal.

### Seguridad aplicada

- Juice Shop corre como usuario no privilegiado `65532`, con
  `no-new-privileges` y volumen nombrado para datos de laboratorio. La imagen
  reescribe archivos de arranque; el rootfs no es read-only.
- El puerto 3000 publica el WAF solo en `10.10.10.10`; el puerto upstream 3001
  escucha únicamente en loopback.
- La interfaz de captura de Suricata se determina por la ruta de
  `10.10.10.0/24`; no se asume que siempre se llame `eth0`.
- La unidad de Suricata usa `Type=simple` para evitar el timeout de la unidad
  heredada que esperaba un proceso bifurcado.
- La clave GPG de Wazuh se importa de forma idempotente y no interactiva.
- Las credenciales y certificados generados por Wazuh permanecen dentro de la
  VM del SIEM.

## 5. Servicios instalados

### Kali Linux

- Nmap.
- Curl.
- jq.
- OpenSSH.

### Ubuntu objetivo

- Docker Engine.
- Docker Compose.
- OWASP Juice Shop `bkimminich/juice-shop:v17.2.0`.
- WAF HTTP local `tiendacr-waf.service`.
- Suricata 6.0.4.
- OpenSSH.
- Wazuh Agent 4.14.10.
- Recoleccion de `/var/log/auth.log`.
- Recoleccion JSON de `/var/log/suricata/eve.json`.

### Ubuntu SIEM

- Wazuh Indexer 4.14.10.
- Wazuh Manager 4.14.10.
- Wazuh Dashboard 4.14.10.
- Filebeat 7.10.2.
- HTTPS en el puerto 443.
- Recepcion de agentes en los puertos 1514 y 1515.

## 6. Problemas encontrados y soluciones

### Kali no aparecia en VirtualBox

La caja `kalilinux/rolling` estaba descargada, pero la VM todavia no habia sido
creada. Se creo la VM y se asigno el nombre `Kali-Linux-Atacante`.

### Caja Ubuntu objetivo no arrancaba correctamente

La caja Ubuntu 24.04 de Bento presento problemas persistentes de SSH. Se cambio
el objetivo a `ubuntu/jammy64`, que permitio completar el arranque y el
aprovisionamiento.

### IP privada asignada a la interfaz equivocada

La deteccion inicial podia seleccionar la interfaz NAT. Se corrigio el script
para buscar la interfaz asociada a la ruta de `10.10.10.0/24`.

### Suricata fallaba con `eth0`

La unidad predeterminada usaba `--af-packet` y una interfaz que no existia en
la VM. Se agrego un override de systemd que obtiene la interfaz real
(`enp0s8` en el objetivo), ejecuta Suricata en modo simple y valida la
configuracion antes de iniciarla.

### Suricata no tenia reglas

Se agregaron dos reglas locales y se crea
`/etc/suricata/rules/suricata.rules` durante el aprovisionamiento. La advertencia
de regla SYN-only para trafico de retorno es esperada y no impide cargar la
configuracion.

### El instalador Wazuh se detenia por tiempo

El Indexer y el Manager tardaron varios minutos en iniciar. Se agregaron
timeouts de systemd de hasta diez minutos para ambos servicios. La instalacion
quedo inicialmente parcial, por lo que el Dashboard se instalo y configuro
posteriormente sin sobrescribir Indexer ni Manager.

### El SIEM dejo de aceptar SSH

La combinacion de Manager, Indexer y las tres VMs produjo presion de memoria.
Se reinicio la VM del SIEM de forma controlada y los servicios persistieron.
Se debe evitar iniciar tareas pesadas en paralelo.

### Registro duplicado del agente

El agente se instala y alcanza el puerto 1514, pero el Manager puede rechazarlo
si conserva la inscripcion anterior con el nombre
`ubuntu-servidor-objetivo`. La limpieza y el nuevo registro estan documentados
en [comandos-finalizacion.md](comandos-finalizacion.md).

## 7. Estado de validación

La validación funcional actual y los límites se detallan en
[`VALIDACION_FINAL.md`](VALIDACION_FINAL.md). El agente 001 aparece `Active`;
Manager, Indexer, Dashboard y Filebeat están activos. Suricata detectó
reconocimiento, SQLi y traversal; Wazuh correlacionó SSH, FIM y vulnerabilidades
del objetivo. El WAF rechazó de forma persistente los patrones de prueba; el
bloqueo automático temporal también expiró correctamente. Juice Shop conserva
su vulnerabilidad intencional y el WAF por firmas no sustituye parchear el
código ni garantiza bloquear variantes.

## 8. Procedimiento operativo

La secuencia vigente de arranque, salud, pruebas, demo y apagado está en
[`comandos-finalizacion.md`](comandos-finalizacion.md). Las evidencias filtradas
y sanitizadas están en `../evidence/2026-11-18/`. No guardar contraseñas,
claves privadas, certificados o tokens en Git.

