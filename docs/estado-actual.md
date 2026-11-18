# Estado actual del Mini SOC TiendaCR

**Corte de validación:** 18 de noviembre de 2026, revalidación en vivo.  
**Entorno:** Vagrant/VirtualBox, red interna `tiendacr-lab` (`10.10.10.0/24`).

## Componentes verificados

| VM | IP privada | Componentes / estado |
|---|---|---|
| `attacker` | `10.10.10.30` | Kali Linux; Nmap, Hydra y curl disponibles. |
| `target` | `10.10.10.10` | Ubuntu Server 22.04.5; WAF HTTP en 3000; Juice Shop 17.2.0 solo en loopback:3001; Suricata 6.0.4; Wazuh Agent 001; UFW activo. |
| `siem` | `10.10.10.20` | Ubuntu Server 24.04.3; Wazuh Manager, Indexer, Dashboard y Filebeat activos; agente 001 `Active`. |

## Pruebas completadas

- Escaneo Nmap de TCP 22 y 3000 detectado por Suricata (SID 1000001/1000002).
- Cinco conexiones SSH con usuario ficticio; alerta Wazuh 100101 tras eventos 5710. Hydra verificó que el objetivo no ofrece autenticación por contraseña.
- SQLi antes del WAF: HTTP 500 sin extracción probada; Suricata SID 1000003/Wazuh 100100.
- WAF persistente: el mismo SQLi posterior devolvió HTTP 403; luego del timeout de 180 s se repitió y siguió en 403; la página normal conservó HTTP 200.
- Active Response bloqueó Kali en INPUT hacia `10.10.10.10:3000`, limitó el alcance y eliminó la regla al vencer los 180 s.
- Traversal después del WAF devolvió HTTP 403; Suricata SID 1000004 y Wazuh 100102. No se confirmó lectura de `/etc/passwd`.
- FIM desde Kali: tras acceso simulado por una llave temporal revocable, se modificó solo `project-check.txt`; Wazuh 550 alertó y la llave se retiró.
- Revalidación SSH desde Kali: Hydra confirmó que no se ofrece autenticación por contraseña; cinco fallos de usuario ficticio generaron 100101.
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
- Aplicación: WAF disponible solo en `10.10.10.10:3000` desde Kali; upstream
  Juice Shop enlazado a `127.0.0.1:3001`, no publicado al segmento.
- SIEM: Indexer limitado a localhost; Dashboard HTTPS restringido a Kali.
- Active Response: regla 100100, agente 001, alcance limitado a conexiones
  entrantes de la IP de origen a `10.10.10.10:3000` por la interfaz privada,
  timeout 180 s. El WAF persistente sigue protegiendo el upstream tras expirar.

## Límites del resultado

- Juice Shop se conserva intencionalmente vulnerable para el laboratorio. La
  detección y contención no parchean el código; el riesgo residual de SQLi se
  mantiene alto en la red de pruebas.
- El módulo Wazuh de vulnerabilidades está habilitado; el feed terminó su
  actualización. La consulta autenticada de solo lectura al índice global
  confirmó para `agent.id=001` 629 paquetes y 2578 registros de vulnerabilidad.
  Una muestra corresponde a CVE-2026-99282 del kernel de Ubuntu y figura bajo
  evaluación, sin CVSS asignado por Wazuh; revisar prioridad y estado en
  Dashboard antes de decidir remediación.
- El estudiante indicó que realiza el proyecto solo. El curso describe el
  trabajo en parejas; la aceptación de modalidad individual debe confirmarse
  con el profesor. No se inventan aportes ni coevaluación.
- La demostración oral aún debe ser realizada por el estudiante. El informe
  tiene 20 páginas y DOCX/PDF están en el repositorio público con historial
  limpio.
- Revisión detallada contra cada punto del enunciado: `VALIDACION_FINAL.md`.
