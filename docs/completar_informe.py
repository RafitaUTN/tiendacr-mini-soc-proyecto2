from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "Informe tecnico" / "Informe de investigacion .docx"
DOC = ROOT / "Informe tecnico" / "Informe de investigacion - Proyecto 2 final.docx"
doc = Document(SOURCE)
refs = []
ref_mode = False
stub_headings = {
    "Implementación de las máquinas virtuales.",
    "Configuración de Wazuh y Suricata.",
    "Pruebas de los cuatro ataques.",
    "Reglas de detección personalizadas.",
    "Respuesta automática.",
    "Plan de respuesta a incidentes.",
    "Remediación y comparación antes/después.",
    "Reevaluación de riesgos.",
    "Conclusiones y recomendaciones.",
}
for p in list(doc.paragraphs):
    text = p.text.strip()
    if text.lower().startswith("referencias bibliográficas"):
        ref_mode = True
        p._element.getparent().remove(p._element)
        continue
    if ref_mode:
        if text:
            refs.append(text)
        p._element.getparent().remove(p._element)
        continue
    if not text:
        p._element.getparent().remove(p._element)
        continue
    if text in stub_headings:
        p._element.getparent().remove(p._element)
        continue
    if text.startswith("Integrantes:"):
        p.text = "Integrante: Rafael Antonio Diaz (proyecto individual)"
    if text.startswith("Fecha:"):
        p.text = "Fecha: 18-11-2026"
    heading_levels = {
        "Introducción": 1,
        "1.1. Comparación de herramientas": 2,
        "1.2. Modelo de responsabilidad compartida": 2,
        "1.3. Análisis de riesgos": 2,
        "Método de valoración": 3,
        "Inventario de activos": 3,
        "Amenazas y vulnerabilidades principales": 3,
        "Matriz inicial de riesgos": 3,
        "Valoración CVSS de tres escenarios OWASP": 3,
        "Plan de tratamiento": 3,
        "Arquitectura del Mini SOC.": 1,
    }
    if text in heading_levels:
        p.style = f"Heading {heading_levels[text]}"

# The assignment instance is individual. Correct inherited team assignments in
# the phase-one treatment matrix without altering the risk analysis itself.
for t in doc.tables:
    for row in t.rows:
        for cell in row.cells:
            if "Responsable: ambos." in cell.text:
                cell.text = cell.text.replace("Responsable: ambos.", "Responsable: estudiante.")
            if "Responsable: ambos" in cell.text:
                cell.text = cell.text.replace("Responsable: ambos", "Responsable: estudiante")

for section in doc.sections:
    section.top_margin = Inches(.72)
    section.bottom_margin = Inches(.72)
    section.left_margin = Inches(.78)
    section.right_margin = Inches(.78)
for style_name in ("Normal",):
    style = doc.styles[style_name]
    style.font.name = "Aptos"
    style.font.size = Pt(10.5)
    style.paragraph_format.space_after = Pt(3)
for style_name in ("Heading 1", "Heading 2", "Heading 3"):
    style = doc.styles[style_name]
    style.font.name = "Aptos Display"
    style.font.color.rgb = None
doc.styles["Heading 1"].font.size = Pt(16)
doc.styles["Heading 2"].font.size = Pt(12)
doc.styles["Heading 3"].font.size = Pt(10.5)

def heading(text, level=1):
    doc.add_heading(text, level=level)

def para(text, style=None):
    return doc.add_paragraph(text, style=style)

def table(headers, rows, widths=None):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = True
    for i, value in enumerate(headers):
        cell = t.rows[0].cells[i]
        cell.text = str(value)
        for run in cell.paragraphs[0].runs:
            run.bold = True
            run.font.size = Pt(8)
        shade = OxmlElement("w:shd")
        shade.set(qn("w:fill"), "D9EAF7")
        cell._tc.get_or_add_tcPr().append(shade)
    for row in rows:
        cells = t.add_row().cells
        for i, value in enumerate(row):
            cells[i].text = str(value)
            cells[i].vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            for p in cells[i].paragraphs:
                p.paragraph_format.space_after = Pt(1)
                for run in p.runs:
                    run.font.size = Pt(8.5)
    return t

def bullet(text):
    para("• " + text)

def numbered(text):
    para(text)

# The source document already contains the complete first-phase analysis and tables.
para("Actualización de fase 2 y cierre técnico — 18 de noviembre de 2026", "Subtitle")
para("Autoría: el estudiante confirmó que realiza el proyecto individualmente y no tiene segundo integrante. El enunciado plantea trabajo en parejas; se deja constancia de la modalidad individual para que el estudiante la confirme con el profesor y no se atribuye trabajo a una persona inexistente.")
heading("Resumen ejecutivo", 1)
para("Se implementó y verificó un Mini SOC local de tres máquinas en VirtualBox y Vagrant: Kali (10.10.10.30), objetivo Ubuntu (10.10.10.10) y SIEM Ubuntu (10.10.10.20). El objetivo aloja OWASP Juice Shop 17.2.0, Suricata 6.0.4 y un agente Wazuh; el SIEM ejecuta Manager, Indexer, Dashboard y Filebeat. Las pruebas se limitaron a la red privada del laboratorio, con tráfico de baja intensidad y datos ficticios.")
para("La validación observó el escaneo de puertos en Suricata; cinco conexiones SSH con un usuario ficticio generaron la regla Wazuh 100101. Después de añadir un WAF de laboratorio persistente, la misma solicitud SQLi se rechazó con HTTP 403 y `X-TiendaCR-WAF: blocked`; Suricata SID 1000003 y Wazuh 100100 la registraron. Active Response bloqueó temporalmente a Kali durante 180 segundos; al expirar, el mismo payload siguió en HTTP 403 y la página normal volvió a HTTP 200. El traversal también recibió HTTP 403 y generó SID 1000004/Wazuh 100102. Desde Kali, una escritura simulada tras autenticación con llave temporal provocó FIM 550; la llave fue revocada y eliminada al terminar.")
para("Se configuraron UFW con denegación por defecto, reglas restringidas por interfaz/origen y SSH por llaves sin acceso de root. El WAF bloquea patrones probados de SQLi, traversal y XSS antes de llegar a Juice Shop, que se mantiene intencionalmente vulnerable para la demostración. Es una protección basada en firmas, no una corrección del código ni defensa contra toda variante; el riesgo residual de la aplicación sigue requiriendo cautela y aislamiento.")

heading("2. Implementación de las máquinas virtuales", 1)
para("El despliegue se define con Vagrant y scripts versionados en provisioning. La red privada tiendacr-lab utiliza el segmento 10.10.10.0/24. Cada VM también dispone de NAT para actualizaciones, pero las reglas de firewall diferencian la interfaz NAT de la interfaz interna; la aplicación no se publica en un adaptador puente.")
table(["Máquina", "Sistema y rol", "Dirección privada", "Componentes y estado observado"], [
    ["attacker", "Kali Linux; pruebas autorizadas", "10.10.10.30", "Nmap, Hydra y curl disponibles; interfaz interna eth1."],
    ["target", "Ubuntu Server 22.04.5; aplicación, WAF y sensores", "10.10.10.10", "WAF HTTP en 3000; Juice Shop 17.2.0 en Docker loopback:3001; Suricata 6.0.4; Wazuh Agent 001 y UFW activos."],
    ["siem", "Ubuntu Server 24.04.3; monitoreo central", "10.10.10.20", "Wazuh Manager, Indexer, Dashboard y Filebeat activos; agente 001 Active."],
])
para("Las versiones del sistema operativo observadas no son idénticas: el objetivo corresponde a Ubuntu 22.04.5 LTS y el SIEM a Ubuntu 24.04.3 LTS. La configuración base de los scripts debe mantener esta distinción. En la recuperación se corrigió la detección de interfaces: las interfaces privadas reales no coincidían con nombres fijados previamente en un script, lo que podía interrumpir el acceso administrativo. Las reglas actuales se generan identificando la ruta por defecto y la ruta 10.10.10.0/24.")
heading("2.1 Servicios y flujo de telemetría", 2)
para("Suricata escucha en la interfaz privada del objetivo y produce /var/log/suricata/eve.json. El agente Wazuh lee eventos EVE y autenticación; el Manager decodifica/correlaciona eventos y guarda alertas. Filebeat envía las alertas al Indexer, que alimenta Dashboard por HTTPS. La validación comprobó servicios activos, salida TLS de Filebeat y alertas de prueba en alerts.json del Manager. En Kali, Dashboard respondió con redirección a la pantalla de inicio de sesión (HTTP 302), sin exponer credenciales.")
heading("2.2 Control de acceso y tráfico", 1)
para("Los firewall locales sustituyen al grupo de seguridad en este laboratorio. UFW aplica denegación entrante y salida permitida; en el objetivo el tráfico enrutado también se deniega, mientras el SIEM tiene el reenvío desactivado. El puerto HTTP 3000 de la interfaz privada acepta solo a Kali y termina en un WAF local de firmas; Juice Shop escucha únicamente en 127.0.0.1:3001 detrás del proxy. El contenedor usa el usuario no privilegiado 65532 y no-new-privileges. El Indexer permanece enlazado a loopback. UFW conserva el acceso Vagrant por el adaptador NAT para administración local del hipervisor.")
table(["Host", "Puerto/protocolo", "Interfaz y origen permitido", "Justificación y riesgo mitigado"], [
    ["target", "22/TCP", "NAT desde gateway Vagrant; red interna desde 10.10.10.30", "Administración por llave; reduce acceso no autorizado."],
    ["target", "3000/TCP", "Red interna desde 10.10.10.30", "Demostración controlada de Juice Shop; limita exposición de la app vulnerable."],
    ["siem", "22/TCP", "NAT Vagrant; red interna desde 10.10.10.30", "Administración por llave."],
    ["siem", "443/TCP", "Red interna desde 10.10.10.30", "Acceso de demostración al Dashboard desde Kali."],
    ["siem", "1514/TCP,UDP", "Red interna desde 10.10.10.10", "Canal cifrado y eventos del agente."],
    ["siem", "1515/TCP", "Red interna desde 10.10.10.10", "Registro/inscripción del agente según la topología del laboratorio."],
])
para("Los puertos de API 55000 y de Indexer 9200 no se abren hacia el segmento; 9200 escucha en localhost. La política SSH efectiva en ambos servidores es PermitRootLogin no, PubkeyAuthentication yes y PasswordAuthentication no. En Kali se comprobó conectividad únicamente a los puertos publicados del objetivo; no se ejecutaron pruebas contra otras redes.")
heading("2.3 Reglas propias y monitoreo", 1)
para("El archivo tiendacr.rules define cuatro firmas: conexión TCP a Juice Shop (SID 1000001), SYN hacia SSH (1000002), comilla codificada %27 en URI HTTP hacia el servicio (1000003) y traversal con ..%2f (1000004). La sintaxis se validó mediante suricata -T y las reglas se comprobaron con tráfico real de laboratorio. EVE JSON registró dirección, puerto, firma y solicitud HTTP. El Manager contiene reglas locales 100100 (SQLi), 100101 (umbral de cinco eventos SSH 5710 desde la misma IP en 120 segundos) y 100102 (traversal), con mapeos MITRE.")
para("Wazuh Syscheck observa /opt/tiendacr/fim-test en tiempo real, comprueba atributos y genera diferencias. La escritura remota simulada desde Kali en project-check.txt generó la alerta 550 ‘Integrity checksum changed’ en el Manager; la llave de prueba se revocó después. La consulta autenticada de solo lectura al índice global confirmó para el agente 001 (ubuntu-servidor-objetivo) 629 paquetes y 2578 registros de vulnerabilidades. Una muestra corresponde a linux-image-5.15.0-203-generic y CVE-2026-99282; Wazuh la marca under evaluation, sin puntuación CVSS asignada. La prioridad y el estado de cada hallazgo deben revisarse en Dashboard antes de decidir tratamiento.")
heading("3. Pruebas de ataques controlados", 1)
para("Todas las pruebas siguientes se dirigieron desde 10.10.10.30 al objetivo propio 10.10.10.10. La latencia se midió desde el comando hasta el evento local y la alerta del Manager; los tiempos son aproximados por granularidad de los relojes virtuales y la consulta de logs.")
table(["N.º / prueba", "Comando o actividad", "Detección y evidencia", "Tiempo observado", "MITRE ATT&CK / resultado"], [
    ["1. Reconocimiento", "nmap -Pn -sT -p 22,3000 10.10.10.10", "Suricata SID 1000001 en 3000 y SID 1000002 en SYN a 22; fast.log/EVE. Puertos: ambos open.", "< 1 s local; alerta disponible en logs en segundos.", "T1046 Network Service Discovery. Detectado; escaneo limitado a dos puertos."],
    ["2. Fuerza bruta simulada", "Cinco conexiones SSH de usuario inexistente soc_test_nonexistent con BatchMode y autenticación publickey; Hydra confirmó que no se ofrece password auth.", "Wazuh 5710 repetida y regla propia 100101 (cinco en 120 s), con IP origen 10.10.10.30. No se intentaron contraseñas reales.", "Alerta 100101 observada aproximadamente 1–2 s después de completar el grupo de conexiones.", "T1110.001 Password Guessing. Acceso rechazado; la política de llaves se mantuvo."],
    ["3. Inyección SQL de prueba", "GET /rest/products/search?q=%27%20OR%201=1-- desde Kali, antes y después del WAF.", "Antes del WAF: HTTP 500 sin extracción. Después: WAF HTTP 403 persistente; Suricata 1000003 y Wazuh 100100. Active Response añadió DROP INPUT por 180 s; tras vencer el mismo payload volvió a 403.", "403 del WAF en 0.02 s; Manager observó la alerta al instante.", "T1190 Exploit Public-Facing Application. Payload de prueba bloqueado; el código de Juice Shop sigue vulnerable a variantes."],
    ["4. Traversal de prueba", "GET con --path-as-is /..%2f..%2fetc%2fpasswd desde Kali.", "Antes del WAF: HTTP 200 sin lectura probada. Después: WAF HTTP 403 con X-TiendaCR-WAF: blocked; Suricata 1000004 y Wazuh 100102.", "403 del WAF en 0.02 s; alerta Manager en el segundo de la solicitud.", "T1190. Detectado y bloqueado; no se acredita lectura de archivo."],
    ["5. Integridad tras acceso simulado", "Desde Kali, SSH por llave temporal autorizada; modificar solo project-check.txt bajo /opt/tiendacr/fim-test.", "Wazuh Syscheck produjo regla 550 en agente 001. Se revocó la clave temporal al terminar.", "Alerta Manager recibida en segundos desde la escritura.", "T1565.001 Stored Data Manipulation, aplicado a archivo de prueba benigno."],
])
para("Antes del WAF, traversal devolvió HTTP 200, pero no se documentó contenido de /etc/passwd; la firma no prueba lectura por sí sola. Después de activar el WAF, el mismo patrón devolvió 403 y no alcanzó Juice Shop. El HTTP 500 inicial de SQLi tampoco probó extracción de datos; el WAF persistente bloqueó el payload medido tras expirar Active Response.")
heading("3.1 Respuesta automática", 2)
para("El Manager vincula la regla 100100 con el comando tiendacr-docker-drop.py en el agente objetivo y un timeout de 180 segundos. El script valida que el origen pertenezca al segmento, protege direcciones reservadas y agrega un DROP en INPUT limitado a la interfaz privada, IP de Kali y destino 10.10.10.10:3000. No bloquea SSH ni otros destinos. Tras la alerta SQLi, la solicitud posterior de Kali expiró; al vencer los 180 segundos, la regla desapareció automáticamente y el WAF siguió devolviendo 403 al mismo payload mientras la página normal devolvía HTTP 200.")
para("Riesgo de la respuesta automática: una firma puede activarse por un falso positivo o una prueba autorizada y suspender el acceso legítimo del equipo durante tres minutos. El alcance por IP/servicio y el vencimiento automático limitan el impacto; el procedimiento de operación prevé revisar el evento, confirmar el origen y esperar la expiración, sin borrar manualmente evidencia ni desbloquear durante la medición.")
heading("4. Plan de respuesta a incidentes aplicado a SQLi", 1)
table(["Fase", "Acción", "Responsable", "Objetivo de tiempo"], [
    ["Preparación", "Mantener inventario, reglas respaldadas, alcance/IP autorizados, contactos del equipo y recuperación del servicio.", "Operador de infraestructura y analista SOC", "Antes de prueba; revisión de 5 min."],
    ["Detección", "Correlacionar SID 1000003, regla Wazuh 100100, origen, destino, hora y estado HTTP. Preservar EVE/alerts.json.", "Analista SOC", "Triage ≤ 5 min."],
    ["Contención", "Aplicar bloqueo temporal de IP origen hacia el servicio; verificar regla y evento de Active Response.", "Operador SOC automatizado; verificación del analista", "≤ 1 min desde regla."],
    ["Erradicación", "En producción, parchear la consulta vulnerable o reemplazar la aplicación; en este laboratorio, conservar Juice Shop aislado y eliminar cualquier artefacto de la prueba si existiera.", "Administrador de aplicación", "≤ 1 h para decidir; corrección en ventana acordada."],
    ["Recuperación", "Dejar expirar bloqueo, comprobar retorno HTTP 200 de la página base, agente activo, servicios SIEM y logs sin interrupción.", "Operador de infraestructura", "≤ 5 min después de expiración."],
    ["Lecciones aprendidas", "Revisar tiempos, falso positivo, regla aplicada, riesgo residual y actualización de runbook/riesgos.", "Estudiante responsable", "≤ 24 h de la prueba."],
])
para("La operación probada cubrió detección, contención automatizada y bloqueo persistente de los patrones SQLi/traversal usados en la prueba. No se erradicó la vulnerabilidad del código: Juice Shop permanece deliberadamente vulnerable dentro del entorno docente y la regla WAF puede ser evadida por variantes no probadas. En producción se debe parchear o retirar el componente vulnerable.")
heading("5. Remediación y comparación antes/después", 1)
table(["Riesgo/ataque", "Antes", "Control aplicado", "Después y limitación"], [
    ["R03 SSH", "No había demostración reciente de detección funcional.", "Desactivar password auth y root remoto; permitir llaves. Regla 100101 para cinco eventos 5710/120 s.", "Hydra no pudo usar contraseñas; cinco conexiones a usuario ficticio generaron 100101. Reduce acceso por contraseña y mejora detección; no elimina todo intento de enumeración."],
    ["R01 SQLi", "Juice Shop deliberadamente vulnerable; el payload de prueba llegó al endpoint y respondió HTTP 500.", "WAF de laboratorio en 3000 bloquea el patrón probado; Suricata detecta %27, Wazuh correlaciona y Active Response bloquea temporalmente INPUT por 180 s.", "Después del timeout, el mismo payload persistió en HTTP 403 mientras la página base devolvió 200. El código sigue vulnerable a variantes; no se presenta como parche de aplicación."],
    ["R02 traversal", "No había respuesta de bloqueo documentada; el patrón devolvió HTTP 200 sin lectura de archivo probada.", "WAF de laboratorio bloquea segmentos ..; Suricata SID 1000004 y Wazuh 100102 correlacionan el evento.", "El patrón repetido devuelve HTTP 403; no se confirma lectura. Variantes pueden evadir esta firma; en producción parchear o retirar la app."],
    ["R07 integridad", "FIM no verificado inicialmente.", "Syscheck observa la ruta de control en tiempo real.", "Acceso remoto simulado desde Kali modificó solo el archivo benigno y produjo regla 550 en Manager; se revocó la llave temporal."],
])
para("La comparación demuestra rechazo SSH, bloqueo persistente de los payloads SQLi/traversal probados y Active Response temporal. No corrige el código vulnerable de Juice Shop ni pretende cubrir todas las variantes; en el escenario docente se conserva el riesgo residual con aislamiento, WAF, monitoreo y respuesta. Para producción el riesgo no sería aceptable: retirar Juice Shop y desplegar una aplicación corregida antes de recibir tráfico real.")
heading("6. Reevaluación de riesgos", 1)
para("Se usa la misma escala P × I (1–5) y los mismos rangos definidos en fase 1. Las puntuaciones residuales son juicio contextual del equipo tras observar los controles; no son mediciones estadísticas ni garantizan ausencia de explotación.")
table(["ID", "Escenario", "Inicial", "Residual", "Justificación basada en evidencia"], [
    ["R01", "SQLi en Juice Shop", "4×5=20 Crítico", "3×5=15 Alto", "Aislamiento, firma y bloqueo limitan ventana/exposición, pero el código vulnerable permanece."],
    ["R02", "XSS / explotación web", "4×4=16 Alto", "3×4=12 Alto", "Segmento y firewall reducen alcance; no se ejecutó XSS ni se parcheó la app."],
    ["R03", "Fuerza bruta SSH", "4×4=16 Alto", "2×4=8 Moderado", "PasswordAuthentication no, llaves, regla por umbral y logs verificados."],
    ["R04", "Escaneo de servicios", "4×3=12 Alto", "2×3=6 Moderado", "Deny-by-default y solo servicios mínimos por origen; escaneo detectado."],
    ["R05", "Acceso SSH no autorizado", "3×5=15 Alto", "2×5=10 Alto", "Root y contraseña deshabilitados; quedan riesgos de llave comprometida o acceso Vagrant desde host local."],
    ["R06", "Compromiso del SIEM", "3×5=15 Alto", "2×5=10 Alto", "Firewall limita Dashboard/puertos; servicios activos. Riesgo de credenciales y gestión local persiste."],
    ["R07", "Alteración de logs/archivos", "3×4=12 Alto", "2×4=8 Moderado", "Regla 550 observada al modificar un archivo inocuo; mejora detección, aunque falta retención inmutable externa."],
    ["R08", "Firewall permisivo", "3×5=15 Alto", "2×5=10 Alto", "Reglas dinámicas y validación de puertos reducen exposición; NAT Vagrant sigue habilitado para administración."],
    ["R09", "Secretos en repositorio", "3×5=15 Alto", "1×5=5 Moderado", "Se revisaron los archivos e historial que se publicarán; claves y credenciales se excluyen y quedan ignoradas."],
    ["R10", "Contenedor privilegiado", "3×5=15 Alto", "2×5=10 Alto", "Se conserva contenedor separado y puerto ligado a IP privada; revisar capacidades/permisos en cada reconstrucción."],
    ["R11", "Ataques fuera de alcance", "2×5=10 Alto", "1×5=5 Moderado", "Pruebas acotadas a IP privada del target; la regla Active Response protege otros destinos."],
    ["R12", "SOC sin recursos/alertas perdidas", "4×3=12 Alto", "2×3=6 Moderado", "Pipeline activo y alertas observadas; SIEM consume recursos considerables y requiere verificar disco durante la demo."],
])

heading("7. Conclusiones y recomendaciones", 1)
para("La topología de tres máquinas funciona en la red interna y el flujo de telemetría Wazuh/Suricata produjo alertas observables. Las reglas personalizadas distinguen reconocimiento, SSH, SQLi y traversal. El WAF bloqueó persistentemente los patrones SQLi/traversal probados; Active Response añadió además un bloqueo INPUT temporal de 180 segundos y lo retiró al vencer, manteniendo HTTP 200 para la página normal. Una modificación simulada desde Kali disparó la alerta FIM 550. La prueba SSH confirmó que el acceso por contraseña está deshabilitado.")
para("El trabajo no demuestra que la inyección haya extraído datos ni que traversal haya leído archivos. La app vulnerable se conserva como blanco de laboratorio, por lo que su riesgo residual sigue siendo alto en el segmento. Wazuh indexó 629 paquetes y 2578 registros de vulnerabilidades para el agente 001; la muestra CVE-2026-99282 está bajo evaluación sin CVSS asignado, y los hallazgos requieren priorización en Dashboard.")
for x in [
    "El repositorio público contiene un historial limpio del Proyecto 2; se excluyeron las claves privadas, credenciales, tokens, discos de VM y archivos de contexto personal.",
    "Mantener las máquinas apagadas fuera de la demostración para liberar memoria y reducir superficie activa.",
    "En producción, reemplazar Juice Shop por software corregido; no considerar una firma IDS o un bloqueo temporal como parche.",
    "Durante la demo, mostrar panel/alerta y Active Response, esperar o explicar el timeout de 180 s y confirmar la recuperación del servicio.",
    "Confirmar con el profesor que acepta la modalidad individual; no inventar integrantes, commits ni coevaluación. Verificar las fuentes bibliográficas del curso requeridas.",
]: bullet(x)
heading("8. Declaración de uso de herramientas de IA", 1)
para("Se utilizó un asistente de IA para apoyar auditoría de configuración, redacción y organización del informe, revisión de comandos y preparación de evidencias. El estudiante debe comprobar cada afirmación, explicar las reglas y resultados en la defensa y ajustar esta declaración para describir su uso real. La IA no sustituye la autoría ni la comprensión técnica.")
heading("Referencias bibliográficas", 1)
for reference in refs:
    para(reference)
heading("Anexo A. Evidencias técnicas", 1)
para("El repositorio local conserva una bitácora con comandos y resultados sanitizados bajo evidence/2026-11-18/. Los resultados se identifican por VM, hora del sistema, dirección privada y regla. Los logs completos de autenticación no se anexan; solo extractos mínimos necesarios, sin identificadores de claves ni credenciales.")
evidence_table = table(["Evidencia", "Resultado que sustenta"], [
    ["E01-suricata-scan.txt", "SID 1000001/1000002 y puertos observados durante Nmap."],
    ["E02-ssh-bruteforce.jsonl", "Regla Wazuh 5710 y alerta agregada 100101 para fuente 10.10.10.30."],
    ["E03-sqli-ar.txt", "SID 1000003, regla 100100, evento de bloqueo y conexión temporalmente denegada."],
    ["E04-path-traversal.jsonl", "SID 1000004 en EVE; estado HTTP observado, sin alegar lectura del archivo."],
    ["E05-fim.jsonl", "Regla 550 de Syscheck por modificación del archivo de prueba en la ruta vigilada."],
    ["E06-servicios-firewall.txt", "UFW, reglas y servicios."],
    ["E07-revalidacion-kali.txt", "Repetición inicial de ataques desde Kali y validación de servicio."],
    ["E08-waf-final-kali.txt", "SQLi/traversal 403; AR expiró; FIM 550 desde Kali."],
])
for row in evidence_table.rows:
    for cell in row.cells:
        for p in cell.paragraphs:
            p.paragraph_format.space_after = Pt(0)
            for run in p.runs:
                run.font.size = Pt(7.5)

# Footer page numbers.
for section in doc.sections:
    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = footer.add_run("Mini SOC TiendaCR  |  Página ")
    run.font.size = Pt(8)
    fld = OxmlElement("w:fldSimple")
    fld.set(qn("w:instr"), "PAGE")
    footer._p.append(fld)

# Tables read more cleanly with left-aligned cell text; full justification had
# stretched short words across narrow columns in the original phase-one tables.
for t in doc.tables:
    if t.rows:
        header = OxmlElement("w:tblHeader")
        header.set(qn("w:val"), "true")
        t.rows[0]._tr.get_or_add_trPr().append(header)
    for row in t.rows:
        for cell in row.cells:
            for p in cell.paragraphs:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                for run in p.runs:
                    if run.font.size is None or run.font.size.pt > 9:
                        run.font.size = Pt(9)

doc.save(DOC)
print(DOC)
