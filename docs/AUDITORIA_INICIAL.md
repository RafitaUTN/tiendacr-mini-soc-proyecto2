# Auditoría inicial — Mini SOC TiendaCR

**Fecha de corte:** 18 de noviembre de 2026  
**Alcance:** revisión documental y técnica de solo lectura del repositorio, Vagrant, las tres VM en ejecución y servicios visibles. No se ejecutaron ataques ni se modificó configuración.  
**Fuentes:** enunciado Proyecto 2 (PDF del usuario), informe compartido Google Docs y archivos del repositorio.

## Resumen ejecutivo

El laboratorio está desplegado y parcialmente operativo: las tres VM están encendidas; Wazuh Manager, Indexer y Dashboard están activos; el agente 001 aparece `Active`; el contenedor Juice Shop está arriba en `10.10.10.10:3000`; Suricata 6.0.4 está activo y existen logs EVE y auth. El script de respuesta automática está presente en la VM SIEM.

No está listo para entrega. Filebeat está `inactive`, UFW reporta `inactive` tanto en el host objetivo como requisito documentado de la plataforma (ver observación al final: la consulta se hizo en el objetivo), y la configuración SSH efectiva declara `PermitRootLogin without-password`, no el valor inequívoco `no` que exige el enunciado. El `Vagrantfile` no crea la regla de Suricata SQLi `%27` descrita en el contexto previo: tanto la regla desplegada por provisioning como `suricata/rules/tiendacr.rules` contienen solo dos reglas, y Wazuh `100100` correlaciona fallos SSH, no la alerta SQLi. El script Active Response no forma parte del provisioning versionado.

El informe compartido contiene una fase de investigación sustancial (comparativa de cuatro herramientas, responsabilidad compartida, activos, amenazas y 12 riesgos); sin embargo, las secciones de fase 2 son encabezados sin resultados. Las puntuaciones CVSS del documento se presentan expresamente como estimaciones preliminares basadas en supuestos y no identifican vulnerabilidades reales/CVE confirmados, mientras el enunciado pide vulnerabilidades reales del proyecto. El documento consultado no pudo exportarse ni verificarse visualmente como PDF final.

## Porcentaje de cumplimiento sustentado

Se usa un conteo conservador de 40 controles atómicos extraídos del enunciado (enunciados 2.1–2.8, entregables y seguridad). `Cumplido` requiere evidencia directamente observada en el repositorio, documento o ejecución de solo lectura; `Parcial` indica solo una parte del control o documentación sin validación funcional; `Pendiente` carece de evidencia suficiente. Para el porcentaje, solo cuenta `Cumplido`: **10/40 = 25% confirmado**. Otros 13 están parciales y 17 pendientes. Es un indicador de evidencia confirmada, no una calificación, ni implica que lo parcial no esté implementado. Las operaciones de ataque, remediación, demo y coevaluación no se repitieron ni se dan por cumplidas por el contexto histórico.

## Matriz de cumplimiento

| ID | Requisito | Estado | Evidencia / brecha |
|---|---|---|---|
| 01 | Atacante Kali propio | Cumplido | VM `attacker` running; Vagrantfile define Kali y red privada. |
| 02 | Objetivo Ubuntu LTS y app en contenedor | Cumplido | VM `target` running; `docker ps` muestra Juice Shop arriba y bound a 10.10.10.10:3000. |
| 03 | SIEM separado | Cumplido | VM `siem` running; servicios core activos. |
| 04 | Red local aislada del laboratorio | Parcial | Vagrant declara Internal Network `tiendacr-lab`, IPs estáticas y SSH host-only; exposición efectiva de todos los adaptadores/reglas no se auditó. |
| 05 | Firewall deny-by-default en servidores | Pendiente | En objetivo `ufw status verbose` devuelve `Status: inactive`; no hay prueba de política equivalente en SIEM. |
| 06 | Solo puertos mínimos y restringidos a IPs del equipo | Parcial | Juice Shop está enlazado a IP privada; listeners SIEM 443/1514/1515 en `0.0.0.0`; filtrado no demostrado. |
| 07 | SSH por llave, sin contraseña y sin root directo | Parcial | Objetivo reporta `PasswordAuthentication no`, `PubkeyAuthentication yes`; `PermitRootLogin without-password` no acredita `no`. SIEM pendiente. |
| 08 | Tabla de firewall con razón y riesgo | Parcial | `docs/direccionamiento.md` lista puertos y origen genérico; no contiene reglas aplicadas/resultado por cada una. |
| 09 | Cuatro herramientas comparadas | Cumplido | Informe compara Wazuh, Suricata, CrowdSec y GuardDuty. |
| 10 | Seis fuentes, incluidas bibliografía del curso y documentación oficial | Parcial | Hay referencias y documentación oficial; la verificación completa del número/tipo APA y bibliografía del curso queda pendiente. |
| 11 | Modelo de responsabilidad compartida | Cumplido | Informe incluye AWS como proveedor de referencia y tabla de responsabilidades para laboratorio. |
| 12 | Inventario C/I/D, amenazas y al menos 10 riesgos | Cumplido | Informe presenta activos, amenazas y 12 riesgos. |
| 13 | Tres CVSS de vulnerabilidades reales usadas | Parcial | Tres vectores y categorías OWASP presentes, pero son estimaciones hipotéticas y no se vinculan a vulnerabilidades reales confirmadas/CVE. |
| 14 | Plan de tratamiento con responsables y controles | Cumplido | Tabla R01–R12, estrategia, responsable y control propuesto. |
| 15 | Reevaluación del riesgo residual tras controles | Pendiente | El informe lo deja para Fase 2; no hay resultados residuales medidos. |
| 16 | Wazuh Manager activo | Cumplido | `systemctl is-active` devolvió `active`. |
| 17 | Indexer y Dashboard activos | Cumplido | Ambos devolvieron `active`; Indexer escucha en loopback:9200, Dashboard en 443. |
| 18 | Filebeat funcional en pipeline configurado | Pendiente | `systemctl is-active filebeat` devolvió `inactive`; no se diagnosticó causa ni entrega. |
| 19 | Agente objetivo conectado | Cumplido | `agent_control -lc`: agente 001 del objetivo `Active`. |
| 20 | Logs de autenticación y Suricata configurados | Parcial | Provisioning configura ambos log sources y existen `/var/log/auth.log` y `eve.json`; entrega al manager/indexer no demostrada. |
| 21 | FIM y vulnerabilidades Wazuh validados | Pendiente | No hay evidencia de validación funcional/documentación disponible. |
| 22 | Suricata integrado y alertas visibles en el panel | Parcial | Servicio y EVE presentes; no se comprobó ingesta/visualización. |
| 23 | Cuatro ataques requeridos ejecutados con evidencia | Pendiente | El informe tiene el título “Pruebas de los cuatro ataques” sin desarrollo. No se repitieron ataques. |
| 24 | Ataques documentados con regla, tiempo, MITRE y logs | Pendiente | Sin tabla ni mediciones actuales. |
| 25 | Dos reglas Suricata propias probadas | Parcial | Dos reglas de conexión TCP/SSH existen en archivo y provisioning; prueba funcional y alertas no verificadas. |
| 26 | Regla Wazuh propia probada | Parcial | Regla 100100 (5 fallos SSH/120 s) existe; carga y disparo no comprobados. |
| 27 | Detección SQLi `%27` mencionada en contexto | Pendiente | No aparece en reglas locales ni provisioning actual; Wazuh 100100 no la correlaciona. |
| 28 | Active Response automático demostrado | Parcial | Script está presente en SIEM; definición/enganche manager y ejecución no inspeccionados; evidencia histórica en contexto no se repitió. |
| 29 | Expiración, recuperación y falsos positivos documentados | Pendiente | No están desarrollados en informe actual. |
| 30 | Plan de respuesta a incidentes con fases/roles/tiempos | Pendiente | En informe solo aparece encabezado. |
| 31 | Remediar y repetir ataques 2 y 3 | Pendiente | Sin plan aplicado ni comparación documentada. |
| 32 | Informe de 15–20 páginas completo y exportado a PDF | Pendiente | El informe compartido deja apartados centrales vacíos; PDF final no verificado. |
| 33 | Evidencias auténticas y trazables | Pendiente | No se encontró directorio de evidencias en archivos del proyecto. |
| 34 | Repositorio GitHub público/reproducible | Parcial | Hay Vagrantfile/configs/README, pero `git remote -v` no muestra remoto y la mayor parte del proyecto está sin seguimiento. |
| 35 | Historial representa aportes de ambos | Pendiente | Solo hay un commit (`Inicio la parte practica`) y ningún remote observado; aportes no demostrados. |
| 36 | Sin secretos en archivos e historial | Pendiente | `.gitignore` excluye algunos formatos; no se realizó un escaneo del historial/archivos y hay archivos DOCX sin seguimiento. |
| 37 | Guion de demo 10+5 y contingencia | Pendiente | No encontrado en informe ni archivos. |
| 38 | Coevaluación individual | Pendiente | No hay evidencia; depende de formulario externo. |
| 39 | Uso de IA declarado en informe | Pendiente | No aparece declaración en el contenido consultado. |
| 40 | Pruebas delimitadas al laboratorio propio | Parcial | El alcance ético está en documentación; pruebas concretas y su evidencia no se revisaron. |

## Hallazgos técnicos prioritarios

1. **Control de acceso sin aplicar:** UFW está inactivo en el objetivo; no puede afirmarse cumplimiento de denegación por defecto.
2. **Filebeat detenido:** Manager/Indexer/Dashboard están arriba, pero la cadena de alertas no se considera funcional mientras no se diagnostique y pruebe envío.
3. **Configuración distinta de la descripción previa:** target actualmente usa contenedor `tiendacr-juice-shop-nuevo`; `Vagrantfile` y docs discrepan en versión base Ubuntu (Jammy frente a 24.04.3 citada en el contexto) y en nombres/versiones de servicios. La versión efectiva del SO no se recogió en este turno.
4. **Reglas no alineadas:** solo SID 1000001/1000002 están en `suricata/rules/tiendacr.rules` y en provisioning. Falta regla SQLi 1000003; no asumir la regla 100100 activa hasta probarla.
5. **Active Response no reproducible desde el repositorio:** script vive en la VM, no está en provisioning/config versionado observado; asociación del manager, permisos, allowlist y temporizador requieren auditoría específica.
6. **Superficie SIEM:** Manager escucha 1514 y 1515 en todas las interfaces; Dashboard 443 también. Indexer 9200 está enlazado a loopback. El firewall inactivo incrementa exposición del servicio en interfaces presentes, aunque la red Vagrant/VirtualBox no se presume expuesta a Internet sin verificarlo.
7. **Historial/entrega:** sin remoto Git, solo un archivo base seguido por Git y gran cantidad de archivos no seguidos; falta inspección de secretos e integración de ambos autores.
8. **Informe no representa el estado actual:** arquitectura dice Ubuntu 24.04.3; `Vagrantfile` selecciona `ubuntu/jammy64`. El informe identifica al menos un integrante, aunque el enunciado solicita ambos nombres.

## Riesgos antes de cambiar infraestructura

- Cambiar firewall puede cortar SSH, agente Wazuh, acceso de demo o el tráfico de Suricata.
- Activar/reiniciar Filebeat u otros servicios podría alterar el estado actual de alertas; primero hay que leer logs/configuración sin divulgar credenciales.
- Rehacer registro del agente puede eliminar/reemplazar IDs o claves existentes.
- Instalar o alterar reglas/Active Response puede causar falsos positivos o bloquear tráfico legítimo.
- Ejecutar reprovisioning puede sobrescribir configuración y reiniciar servicios; queda fuera de esta auditoría.
- La asignación de RAM del SIEM es 6 GiB de los 15.71 GiB del host según inspección previa; acciones concurrentes pueden degradar el laboratorio.

## Informe: faltantes sustantivos

Desarrollar con resultados medidos: implementación y versiones efectivas; control de acceso y reglas justificadas; arquitectura final y recursos; configuración/validación Wazuh, FIM, detección de vulnerabilidades y Suricata; cuatro ataques con comando, tiempo, evidencia, regla y MITRE; pruebas antes/después de SSH y explotación web; Active Response incluyendo expiración y falso positivo; plan de respuesta por fases, roles y objetivos de tiempo; reevaluación del riesgo residual; conclusiones/recomendaciones; referencias APA revisadas; anexos y declaración de IA. Ajustar portada para incluir los dos integrantes.

## Evidencias faltantes

No se encontraron capturas, logs exportados ni tabla central de evidencias en la carpeta. Conseguir, una vez validados: estado Vagrant/recursos; firewall efectivo; SSH seguro; agente Active; Filebeat/pipeline e indexación; FIM y vulnerabilidades; reglas Suricata/Wazuh cargadas y detecciones; ataques 1–4 y tiempos; bloqueo/expiración/recuperación; comparación antes/después y riesgos residuales. Usar identificadores E01–E15 del prompt maestro solo cuando exista evidencia auténtica.

## Estructura de carpetas recomendada

```text
docs/
  AUDITORIA_INICIAL.md
  PLAN_DE_CORRECCION.md
  MATRIZ_VALIDACION.md
  BITACORA_CAMBIOS.md
  checklist-entrega.md
evidence/
  README.md                 # índice/metadatos; no logs sensibles
  screenshots/              # capturas revisadas y redactadas
  logs/                     # extractos mínimos, sin secretos
docs/report/                # fuente DOCX/PDF final, si se acuerda versionarla
```

No se creó una carpeta vacía de evidencias. Antes de publicar, revisar secretos en el working tree y el historial completo.

## Decisiones que requieren autorización antes de fase técnica

- Aplicar y validar reglas UFW/firewall, SSH o ajustes de exposición de servicios.
- Activar, reparar o reiniciar Filebeat/servicios Wazuh.
- Cambiar registros del agente, reglas o respuesta automática.
- Ejecutar los cuatro ataques controlados y repetir ataques tras remediación.
- Crear evidencias que impliquen reiniciar servicios o modificar configuración.
- Publicar, hacer commit/push, vincular remoto o compartir el repositorio.
- Editar el informe compartido: usar copia/version de revisión, conservar el original.

## Limitaciones de esta auditoría

La lectura del Google Doc fue de solo lectura. El estado técnico observado corresponde a una sola captura temporal, no a pruebas de persistencia tras reinicio. No se comprobó acceso al Dashboard con credenciales, visibilidad de alertas, ingesta completa, estado de los firewalls del SIEM/atacante, reglas activas del manager, wiring de Active Response ni integridad/escaneo de vulnerabilidades. El cálculo 27.5% refleja únicamente controles confirmados bajo el criterio descrito.

