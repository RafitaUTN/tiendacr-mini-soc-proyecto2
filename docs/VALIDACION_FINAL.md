# Validación final contra el enunciado — actualización 25 de noviembre de 2026

El inventario de ataques y evidencias detallado abajo fue medido el 18 de
noviembre. El 25 de noviembre se revalidaron desde el host el estado de las
tres VM, servicios, agente, reglas Suricata, configuración Wazuh y acceso web
local: Vagrant validó; las tres VM estaban `running`; el agente 001 estaba
`Active`; Suricata cargó cuatro reglas sin errores; `wazuh-analysisd -t` y
`filebeat test output` finalizaron correctamente; Juice Shop respondió HTTP 200.
Además, el túnel local al Dashboard respondió HTTP 302 y el de Juice Shop HTTP
200. El PDF final tiene 19 páginas.
Las salidas resumidas de esta revalidación se guardan en
[`../evidence/2026-11-25/E09-revalidacion-host.txt`](../evidence/2026-11-25/E09-revalidacion-host.txt).
El 25-11 también se corrigió un timeout intermitente de `/app/wz-home`: una
actualización inicial del feed de vulnerabilidades elevó temporalmente las
respuestas de la API por encima del límite de 20 s. Se configuró el límite del
Dashboard en 60 s y se reinició solo ese servicio. Después, la API regresó a
menos de 1.1 s en las consultas probadas; el login fue HTTP 200, una sesión
autenticada cargó `/app/wz-home` con HTTP 200 y las cuatro unidades siguieron
activas. Ver evidencia E10.

Alcance: comprobaciones realizadas desde el host y Kali dentro de la red privada
Vagrant `tiendacr-lab` (`10.10.10.0/24`). No se escanearon redes externas ni se
usaron usuarios o contraseñas reales. La validación prueba controles observables;
no implica que un software vulnerable haya sido corregido si no hay evidencia de
un parche.

## Estado del laboratorio

| Máquina | Resultado comprobado |
|---|---|
| Kali `10.10.10.30` | `nmap`, `hydra` y `curl` disponibles; interfaz privada `eth1`. |
| Target `10.10.10.10` | Ubuntu 22.04.5, WAF `tiendacr-waf.service` activo en 3000, Juice Shop 17.2.0 por Docker solo en `127.0.0.1:3001`, Suricata 6.0.4, Wazuh Agent 001 y UFW activos. Contenedor `tiendacr-juice-shop-nuevo` en ejecución. |
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
| Agente: autenticación, FIM y vulnerabilidades | Wazuh Agent 001 activo; cinco fallos SSH dispararon 5710/100101; cambio remoto simulado desde Kali en `/opt/tiendacr/fim-test/project-check.txt` disparó regla 550. Query al índice global: 629 paquetes y 2578 vulnerabilidades para `agent.id=001`. | Cumple; algunos registros quedan bajo evaluación y deben priorizarse |
| Suricata integrado con SIEM | SQLi y traversal dispararon SID 1000003/1000004, Wazuh 100100/100102 y registros EVE con HTTP y URI. | Cumple para las firmas probadas |
| Cuatro ataques, regla, tiempo y MITRE | Desde Kali se ejecutaron reconocimiento, intentos SSH ficticios/Hydra, SQLi y traversal. Las reglas y eventos constan abajo; MITRE se consigna en el informe. | Cumple como ejercicios de detección; traversal no confirmó lectura de archivo |
| Cuarto ataque de integridad | Desde Kali se autenticó con una llave temporal autorizada para simular una cuenta comprometida; la escritura a `project-check.txt` produjo Wazuh 550. La llave se revocó y borró al terminar. | Cumple como ataque post-acceso simulado, sin tocar datos reales ni archivos de sistema |
| Reglas propias ≥2 Suricata y ≥1 Wazuh | Cuatro SIDs locales (1000001–1000004) y tres reglas Wazuh locales (100100–100102) cargadas y observadas. | Cumple |
| WAF / remediación web | Juice Shop escucha en `127.0.0.1:3001`; el proxy filtra el puerto lab 3000. El mismo SQLi que antes devolvía 500 ahora retorna 403 aun después de expirar Active Response; traversal devuelve 403; la página normal conserva HTTP 200. | Cumple para patrones de prueba; el WAF de firmas no corrige el código y puede evadirse con variantes |
| Respuesta automática | SQLi disparó 100100; Active Response insertó DROP en INPUT para `10.10.10.30`→`10.10.10.10:3000` por 180 s. Curl expiró; la regla se retiró sola. Después, el WAF siguió rechazando el mismo payload. | Cumple |
| Remediación y repetición de ataques 2 y 3 | SSH por contraseña rechazado y 100101 activo. El mismo payload SQLi, repetido tras el timeout, obtuvo 403 persistente mientras HTTP normal obtuvo 200. | Cumple como control compensatorio del laboratorio; Juice Shop subyacente continúa vulnerable a variantes no probadas |
| Plan IR de seis etapas, roles y objetivos de tiempo | Incluido en el informe: preparación, detección, contención, erradicación, recuperación y lecciones aprendidas. | Cumple documentalmente; la erradicación del código no se ejecutó |
| Informe 15–20 páginas, PDF y repositorio | PDF del informe con 19 páginas; DOCX y PDF en repositorio público con historial limpio y evidencia filtrada. | Cumple |
| Nombre del PDF según plantilla | Archivo público con nombre descriptivo; el enunciado pide `P1_Apellido1_Apellido2.pdf`. No se inventó un segundo apellido ni se cambió P2 por P1 sin aclaración del profesor. | Parcial; confirmar la convención para entrega individual |
| Demostración 10 min + 5 min de preguntas | No puede acreditarse con pruebas de laboratorio. | Pendiente del estudiante |
| Coevaluación y modalidad individual | No se inventaron integrante o formulario. El enunciado señala parejas; la aceptación del trabajo individual requiere confirmación del profesor. | Pendiente del curso |

## Pruebas de Kali y respuesta

- **Nmap:** `nmap -Pn -sT -sV -p 22,3000 --version-light 10.10.10.10` encontró TCP/22 y TCP/3000 abiertos. SSH identificó OpenSSH 8.9p1 Ubuntu. Suricata generó SID 1000001 para tráfico a 3000 y SID 1000002 para conexiones SYN a 22. Solo se sondearon esos dos puertos del target.
- **Hydra SSH:** un único intento con `laboratorio-inexistente` y la contraseña ficticia `DemoOnlyNotReal123`, un hilo. Resultado: `target ... does not support password authentication`. No se probó una lista ni credenciales reales.
- **Umbral SSH Wazuh:** cinco conexiones SSH con usuario inexistente desde Kali entre 21:11:46 y 21:11:47; el Manager emitió 100101 para el agente 001. Todos fueron rechazados por `publickey`.
- **SQLi de laboratorio:** antes del WAF, `GET /rest/products/search?q=%27%20OR%201=1--` dio HTTP 500 en ~0,45 s sin extracción demostrada. Después del WAF, el mismo payload dio HTTP 403 con `X-TiendaCR-WAF: blocked` en ~0,02 s; EVE registró SID 1000003 y Wazuh 100100. Active Response impidió tráfico de Kali por 180 s; una vez retirado el DROP, el mismo SQLi siguió en HTTP 403 y la página normal respondió HTTP 200.
- **Path traversal:** antes del WAF dio HTTP 200 sin lectura confirmada. Después, `--path-as-is /..%2f..%2fetc%2fpasswd` devolvió HTTP 403 en ~0,02 s; EVE registró SID 1000004 y Wazuh 100102. La firma señala la ruta sospechosa, no prueba por sí sola una lectura.
- **FIM desde Kali:** se añadió una llave ed25519 temporal y explícitamente comentada a `vagrant` para simular una cuenta comprometida; Kali modificó solo el archivo inocuo de prueba y el agente produjo regla 550. Se quitó la llave de `authorized_keys` y se borraron los archivos privado/público temporales.

## Pendientes que impiden afirmar “100% cumplido”

1. **Límite de remediación:** Juice Shop sigue siendo vulnerable a patrones no cubiertos por el WAF de laboratorio. El payload probado queda en 403 después del timeout, pero esto es un control compensatorio acotado, no un parche de código ni una defensa general.
2. **Nombre del PDF:** la plantilla prescribe `P1_Apellido1_Apellido2.pdf`; el PDF se mantiene con nombre descriptivo y no se inventó un segundo apellido. Confirmar formato por trabajo individual.
3. **Entrega académica:** falta la demo oral, completar el formulario aplicable y confirmar con el profesor que acepta la modalidad individual. El repositorio es público; el estudiante debe entregar su enlace por la plataforma del curso.
