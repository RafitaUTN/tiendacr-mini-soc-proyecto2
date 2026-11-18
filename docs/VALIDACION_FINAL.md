# Validación final contra el enunciado — 18 de noviembre de 2026

Alcance: comprobaciones realizadas desde el host y Kali dentro de la red privada
Vagrant `tiendacr-lab` (`10.10.10.0/24`). No se escanearon redes externas ni se
usaron usuarios o contraseñas reales. La validación prueba controles observables;
no implica que un software vulnerable haya sido corregido si no hay evidencia de
un parche.

## Estado del laboratorio

| Máquina | Resultado comprobado |
|---|---|
| Kali `10.10.10.30` | `nmap`, `hydra` y `curl` disponibles; interfaz privada `eth1`. |
| Target `10.10.10.10` | Ubuntu 22.04.5, Docker/Juice Shop 17.2.0, Suricata 6.0.4, Wazuh Agent 001, UFW y filtro Docker activos. Contenedor `tiendacr-juice-shop-nuevo` en ejecución. |
| SIEM `10.10.10.20` | Ubuntu 24.04.3; Manager, Indexer, Dashboard y Filebeat activos; agente 001 `Active`. Dashboard responde HTTP 302 hacia login. |
| Integraciones | Filebeat `test output`: TLS verificado, handshake y conexión con `https://127.0.0.1:9200` satisfactorios. `wazuh-analysisd -t` correcto. |
| Reglas IDS | `suricata -T`: cuatro reglas cargadas, cero errores. |
| Vagrant | `vagrant validate` satisfactorio; attacker, target y SIEM en estado `running`. |

## Criterios del enunciado

| Criterio | Resultado de comprobación | Estado |
|---|---|---|
| Fase 1: comparar ≥4 herramientas; incluir proveedor cloud y ≥2 abiertas | El informe compara AWS GuardDuty, Wazuh, Suricata y CrowdSec. | Cumple documentalmente |
| Fase 1: ≥6 fuentes, ≥2 bibliografía del curso y ≥2 oficiales; APA | El informe contiene 10 referencias; incluye Dotson y Guijarro et al. del material citado por el enunciado, además de documentación oficial. | Cumple documentalmente |
| Responsabilidad compartida | Se usa AWS como proveedor de referencia para el laboratorio local. | Cumple documentalmente |
| Riesgos, ≥10 filas, CVSS/OWASP, tratamientos y matriz residual | Informe con inventario y 12 riesgos; incluye tres estimaciones asociadas a categorías OWASP y reevaluación. | Cumple documentalmente; las puntuaciones son estimaciones del proyecto |
| Tres máquinas y aplicación vulnerable en contenedor | Las tres VM corren; contenedor Juice Shop está `Up`. | Cumple |
| Firewall deny-by-default y reglas por IP; SSH por llaves | UFW activo en target y SIEM. Target: `deny incoming`, `deny routed`; SSH efectivo `PermitRootLogin no`, `PubkeyAuthentication yes`, `PasswordAuthentication no`. SIEM: `deny incoming`; routed `disabled` porque no enruta. | Cumple; revisar reglas NAT Vagrant descritas en evidencia |
| Agente: autenticación, FIM y vulnerabilidades | Wazuh Agent 001 activo; cinco fallos SSH dispararon 5710/100101; cambio en `/opt/tiendacr/fim-test/project-check.txt` disparó regla 550. Syscollector corre en agente 001. | Parcial: no aparece inventario/índice de vulnerabilidades del target en Indexer |
| Suricata integrado con SIEM | SQLi y traversal dispararon SID 1000003/1000004, Wazuh 100100/100102 y registros EVE con HTTP y URI. | Cumple para las firmas probadas |
| Cuatro ataques, regla, tiempo y MITRE | Desde Kali se ejecutaron reconocimiento, intentos SSH ficticios/Hydra, SQLi y traversal. Las reglas y eventos constan abajo; MITRE se consigna en el informe. | Cumple como ejercicios de detección; traversal no confirmó lectura de archivo |
| Cuarto ataque de integridad | Wazuh 550 detectó escritura al archivo de prueba. Se modificó administrativamente el archivo local del objetivo para validar FIM. | Parcial: no fue una intrusión remota originada desde Kali |
| Reglas propias ≥2 Suricata y ≥1 Wazuh | Cuatro SIDs locales (1000001–1000004) y tres reglas Wazuh locales (100100–100102) cargadas y observadas. | Cumple |
| Respuesta automática | SQLi disparó 100100; `DOCKER-USER` insertó DROP de `10.10.10.30` a `172.18.0.2:3000`. Curl expiró durante el bloqueo; luego el temporizador retiró la regla y el sitio volvió a HTTP 200. | Cumple detección/contención temporal |
| Remediación y repetición de ataques 2 y 3 | SSH por contraseña está deshabilitado y el ataque simulado se rechazó. La repetición SQLi detectó y bloqueó temporalmente. | Parcial: el código de Juice Shop sigue vulnerable; tras expirar el bloqueo no hay parche persistente probado |
| Plan IR de seis etapas, roles y objetivos de tiempo | Incluido en el informe: preparación, detección, contención, erradicación, recuperación y lecciones aprendidas. | Cumple documentalmente; la erradicación del código no se ejecutó |
| Informe 15–20 páginas, PDF y repositorio | PDF del informe con 20 páginas; DOCX y PDF en repositorio público con historial limpio y evidencia filtrada. | Cumple |
| Nombre del PDF según plantilla | Archivo público con nombre descriptivo; el enunciado pide `P1_Apellido1_Apellido2.pdf`. No se inventó un segundo apellido ni se cambió P2 por P1 sin aclaración del profesor. | Parcial; confirmar la convención para entrega individual |
| Demostración 10 min + 5 min de preguntas | No puede acreditarse con pruebas de laboratorio. | Pendiente del estudiante |
| Coevaluación y modalidad individual | No se inventaron integrante o formulario. El enunciado señala parejas; la aceptación del trabajo individual requiere confirmación del profesor. | Pendiente del curso |

## Pruebas de Kali y respuesta

- **Nmap:** `nmap -Pn -sT -sV -p 22,3000 --version-light 10.10.10.10` encontró TCP/22 y TCP/3000 abiertos. SSH identificó OpenSSH 8.9p1 Ubuntu. Suricata generó SID 1000001 para tráfico a 3000 y SID 1000002 para conexiones SYN a 22. Solo se sondearon esos dos puertos del target.
- **Hydra SSH:** un único intento con `laboratorio-inexistente` y la contraseña ficticia `DemoOnlyNotReal123`, un hilo. Resultado: `target ... does not support password authentication`. No se probó una lista ni credenciales reales.
- **Umbral SSH Wazuh:** cinco conexiones SSH con usuario inexistente desde Kali entre 21:11:46 y 21:11:47; el Manager emitió 100101 para el agente 001. Todos fueron rechazados por `publickey`.
- **SQLi de laboratorio:** una petición `GET /rest/products/search?q=%27%20OR%201=1--` respondió HTTP 500 en ~0,45 s; EVE registró SID 1000003 y Wazuh 100100. No hay evidencia de extracción de datos. Active Response impidió la petición posterior (timeout 3 s); después de esperar el timeout de 180 s, se retiró el DROP y Kali recuperó HTTP 200 en ~0,08 s.
- **Path traversal:** petición con `--path-as-is /..%2f..%2fetc%2fpasswd` respondió HTTP 200 en ~0,13 s. EVE registró SID 1000004 y Wazuh 100102. La firma evidencia la ruta sospechosa, no la lectura del archivo.
- **FIM:** modificación de marcador inocuo en `/opt/tiendacr/fim-test/project-check.txt` disparó regla 550 en el agente 001 y quedó en `alerts.json` del Manager.

## Pendientes que impiden afirmar “100% cumplido”

1. **Vulnerabilidades del agente objetivo:** el feed y el módulo del Manager arrancaron, pero `_cat/indices` solo mostró `wazuh-states-vulnerabilities-ubuntu-servidor-siem` (2578 documentos) y no un índice del objetivo. No atribuir CVE al target hasta confirmar agente 001 en Dashboard/Indexer.
2. **Remediación SQLi:** la aplicación deliberadamente vulnerable continúa respondiendo al endpoint; el control medido es detección más bloqueo temporal de 180 s. Se necesita parche/capa persistente y repetir el mismo payload después para demostrar que ya no llega a la aplicación, o documentar que el profesor acepta la contención temporal como tratamiento del laboratorio.
3. **Ataque de integridad desde Kali:** la alerta FIM se validó con modificación administrativa de un archivo benigno; no se obtuvo acceso remoto ni se alteraron archivos de sistema. Si el criterio exige origen Kali, falta diseñar una vía de prueba segura y autorizada que origine un cambio detectable.
4. **Entrega académica:** falta la demo oral, completar el formulario aplicable y confirmar con el profesor que acepta la modalidad individual. El repositorio es público; el estudiante debe entregar su enlace por la plataforma del curso.
