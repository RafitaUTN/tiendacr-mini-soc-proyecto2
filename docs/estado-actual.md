# Estado actual del Mini SOC TiendaCR

**Corte de validación:** 18 de noviembre de 2026, revalidación en vivo.  
**Entorno:** Vagrant/VirtualBox, red interna `tiendacr-lab` (`10.10.10.0/24`).

## Componentes verificados

| VM | IP privada | Componentes / estado |
|---|---|---|
| `attacker` | `10.10.10.30` | Kali Linux; Nmap, Hydra y curl disponibles. |
| `target` | `10.10.10.10` | Ubuntu Server 22.04.5; Docker/Juice Shop 17.2.0; Suricata 6.0.4; Wazuh Agent 001 activo; UFW y filtro Docker activos. |
| `siem` | `10.10.10.20` | Ubuntu Server 24.04.3; Wazuh Manager, Indexer, Dashboard y Filebeat activos; agente 001 `Active`. |

## Pruebas completadas

- Escaneo Nmap de TCP 22 y 3000 detectado por Suricata (SID 1000001/1000002).
- Cinco conexiones SSH con usuario ficticio; alerta Wazuh 100101 tras eventos 5710. Hydra verificó que el objetivo no ofrece autenticación por contraseña.
- Solicitud SQLi de prueba: Suricata SID 1000003 y Wazuh 100100; respuesta de aplicación HTTP 500, sin evidencia de extracción de datos.
- Active Response añadió una regla DROP de Kali a Juice Shop por 180 segundos; el intento siguiente expiró y, al vencer el temporizador, el sitio volvió a HTTP 200.
- Solicitud traversal registrada como SID 1000004; HTTP 200, sin evidencia de lectura de `/etc/passwd`.
- Modificación de `/opt/tiendacr/fim-test/project-check.txt` detectada por Wazuh Syscheck, regla 550.
- Revalidación desde Kali: Nmap en 22/3000; Hydra con una credencial ficticia confirmó que password auth no se ofrece; cinco intentos SSH provocaron 100101; SQLi provocó 100100 y bloqueo por 180 s; tras el timeout volvió HTTP 200. Traversal provocó 100102 y respondió HTTP 200 sin probar lectura.
- Revalidación de FIM: escritura de un marcador benigno en el archivo de control generó nuevamente Wazuh 550 en el Manager.
- Suricata valida las reglas locales; `vagrant validate` y sintaxis de los scripts Bash verificadas.

La evidencia JSONL y las notas mínimas están en
[`../evidence/2026-11-18`](../evidence/2026-11-18/). No contienen credenciales
ni registros completos de autenticación.

## Controles activos

- UFW: denegar entrada por defecto en ambas VM. En `target` la política routed
  también es `deny`; en `siem` el reenvío aparece como `disabled (routed)` y no
  se usa como router.
- SSH: `PermitRootLogin no`, `PubkeyAuthentication yes`,
  `PasswordAuthentication no` en SIEM y objetivo.
- Aplicación: publicación solo en `10.10.10.10:3000`; la cadena `DOCKER-USER`
  restringe el acceso al segmento autorizado.
- SIEM: Indexer limitado a localhost; Dashboard HTTPS restringido a Kali.
- Active Response: regla 100100, agente 001, alcance limitado a conexiones
  nuevas de la IP de origen al puerto de Juice Shop, timeout 180 s.

## Límites del resultado

- Juice Shop se conserva intencionalmente vulnerable para el laboratorio. La
  detección y contención no parchean el código; el riesgo residual de SQLi se
  mantiene alto en la red de pruebas.
- El módulo Wazuh de vulnerabilidades está habilitado; el feed terminó su
  actualización y el Manager creó índices de inventario/vulnerabilidades para
  el propio SIEM. El agente objetivo está activo y Syscollector ejecutó una
  evaluación, pero no se confirmó un índice de vulnerabilidades específico del
  agente objetivo. Revisar el agente 001 en Dashboard antes de afirmar CVE
  detectados en ese host.
- El estudiante indicó que realiza el proyecto solo. El curso describe el
  trabajo en parejas; la aceptación de modalidad individual debe confirmarse
  con el profesor. No se inventan aportes ni coevaluación.
- La demostración oral aún debe ser realizada por el estudiante. El informe
  tiene 20 páginas y DOCX/PDF están en el repositorio público con historial
  limpio.
- Revisión detallada contra cada punto del enunciado: `VALIDACION_FINAL.md`.
