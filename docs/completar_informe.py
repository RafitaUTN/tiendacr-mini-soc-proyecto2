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
    style.font.size = Pt(11)
    style.paragraph_format.space_after = Pt(5)
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
para("La validación observó el escaneo de puertos en Suricata; cinco conexiones SSH con un usuario ficticio generaron la regla personalizada Wazuh 100101; una solicitud de prueba SQLi generó Suricata SID 1000003 y Wazuh 100100. Esa alerta ejecutó Active Response y bloqueó únicamente el flujo de Kali hacia el contenedor durante 180 segundos; al expirar se retiró y Kali recuperó HTTP 200. El intento de traversal generó SID 1000004 en EVE JSON. Una modificación inocua de project-check.txt produjo la alerta FIM 550.")
para("Se configuraron UFW con denegación por defecto, reglas restringidas por interfaz/origen y SSH por llaves sin acceso de root. La aplicación deliberadamente vulnerable se conserva para la demostración; los controles de aislamiento y respuesta reducen exposición, pero no eliminan la vulnerabilidad de código. El riesgo residual de SQLi permanece alto dentro del segmento autorizado hasta reemplazar o parchear la aplicación.")

heading("2. Implementación de las máquinas virtuales", 1)
para("El despliegue se define con Vagrant y scripts versionados en provisioning. La red privada tiendacr-lab utiliza el segmento 10.10.10.0/24. Cada VM también dispone de NAT para actualizaciones, pero las reglas de firewall diferencian la interfaz NAT de la interfaz interna; la aplicación no se publica en un adaptador puente.")
table(["Máquina", "Sistema y rol", "Dirección privada", "Componentes y estado observado"], [
    ["attacker", "Kali Linux; pruebas autorizadas", "10.10.10.30", "Nmap, Hydra y curl disponibles; interfaz interna eth1."],
    ["target", "Ubuntu Server 22.04.5; aplicación y sensores", "10.10.10.10", "Docker/Juice Shop 17.2.0, Suricata 6.0.4, Wazuh Agent 001 activo, UFW activo."],
    ["siem", "Ubuntu Server 24.04.3; monitoreo central", "10.10.10.20", "Wazuh Manager, Indexer, Dashboard y Filebeat activos; agente 001 Active."],
])
para("Las versiones del sistema operativo observadas no son idénticas: el objetivo corresponde a Ubuntu 22.04.5 LTS y el SIEM a Ubuntu 24.04.3 LTS. La configuración base de los scripts debe mantener esta distinción. En la recuperación se corrigió la detección de interfaces: las interfaces privadas reales no coincidían con nombres fijados previamente en un script, lo que podía interrumpir el acceso administrativo. Las reglas actuales se generan identificando la ruta por defecto y la ruta 10.10.10.0/24.")
heading("2.1 Servicios y flujo de telemetría", 2)
para("Suricata escucha en la interfaz privada del objetivo y produce /var/log/suricata/eve.json. El agente Wazuh lee eventos EVE y autenticación; el Manager decodifica/correlaciona eventos y guarda alertas. Filebeat envía las alertas al Indexer, que alimenta Dashboard por HTTPS. La validación comprobó servicios activos, salida TLS de Filebeat y alertas de prueba en alerts.json del Manager. En Kali, Dashboard respondió con redirección a la pantalla de inicio de sesión (HTTP 302), sin exponer credenciales.")
heading("2.2 Control de acceso y tráfico", 1)
para("Los firewall locales sustituyen al grupo de seguridad en este laboratorio. UFW aplica denegación entrante y salida permitida; en el objetivo el tráfico enrutado también se deniega, mientras el SIEM tiene el reenvío desactivado. El servicio web está disponible solo en la interfaz privada desde Kali; las reglas Docker de DOCKER-USER permiten los flujos necesarios y descartan otras fuentes hacia el puerto del contenedor. El Indexer permanece enlazado a loopback. UFW conserva el acceso Vagrant por el adaptador NAT para administración local del hipervisor.")
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
para("Wazuh Syscheck observa /opt/tiendacr/fim-test en tiempo real, comprueba atributos y genera diferencias. La modificación de project-check.txt generó la alerta 550 ‘Integrity checksum changed’ en el Manager. La detección de vulnerabilidades está activa, el feed terminó de actualizar y el IndexerConnector creó índices de estado para el SIEM. Syscollector ejecutó una evaluación en el agente 001, pero no se confirmó un índice con vulnerabilidades del objetivo; esa vista debe revisarse en Dashboard antes de afirmar CVE detectados en ese host.")
heading("3. Pruebas de ataques controlados", 1)
para("Todas las pruebas siguientes se dirigieron desde 10.10.10.30 al objetivo propio 10.10.10.10. La latencia se midió desde el comando hasta el evento local y la alerta del Manager; los tiempos son aproximados por granularidad de los relojes virtuales y la consulta de logs.")
table(["N.º / prueba", "Comando o actividad", "Detección y evidencia", "Tiempo observado", "MITRE ATT&CK / resultado"], [
    ["1. Reconocimiento", "nmap -Pn -sT -p 22,3000 10.10.10.10", "Suricata SID 1000001 en 3000 y SID 1000002 en SYN a 22; fast.log/EVE. Puertos: ambos open.", "< 1 s local; alerta disponible en logs en segundos.", "T1046 Network Service Discovery. Detectado; escaneo limitado a dos puertos."],
    ["2. Fuerza bruta simulada", "Cinco conexiones SSH de usuario inexistente soc_test_nonexistent con BatchMode y autenticación publickey; Hydra confirmó que no se ofrece password auth.", "Wazuh 5710 repetida y regla propia 100101 (cinco en 120 s), con IP origen 10.10.10.30. No se intentaron contraseñas reales.", "Alerta 100101 observada aproximadamente 1–2 s después de completar el grupo de conexiones.", "T1110.001 Password Guessing. Acceso rechazado; la política de llaves se mantuvo."],
    ["3. Inyección SQL de prueba", "GET /rest/products/search?q=%27%20OR%201=1--", "Suricata SID 1000003; Wazuh 100100; EVE registra HTTP 500. La respuesta de la aplicación fue error, no extracción de datos.", "Aproximadamente 1 s entre alerta IDS y regla del Manager.", "T1190 Exploit Public-Facing Application. Firma detectada; no se afirma extracción exitosa."],
    ["4. Traversal de prueba", "GET con --path-as-is /..%2f..%2fetc%2fpasswd", "Suricata SID 1000004 en EVE con URI, origen y respuesta HTTP 200. No se obtuvo ni documentó contenido de archivos del host.", "Evento local registrado al completar la solicitud.", "T1190. Detectado por IDS; no se acredita lectura del archivo del sistema."],
    ["5. Integridad (actividad adicional)", "Crear y modificar /opt/tiendacr/fim-test/project-check.txt, sin datos sensibles.", "Wazuh Syscheck produjo regla 550 ‘Integrity checksum changed’ desde agente 001.", "Evento recibido en Manager en menos de un minuto desde la modificación final.", "T1565.001 Stored Data Manipulation, aplicado a modificación de archivo de prueba."],
])
para("El evento de traversal figura en EVE aunque la respuesta del servidor fue 200; la firma señala una ruta sospechosa, no prueba por sí misma que se haya leído /etc/passwd. De igual manera, el 500 de SQLi indica error de la aplicación y no permite concluir que los datos se extrajeron. Estas distinciones evitan atribuir resultados no observados.")
heading("3.1 Respuesta automática", 2)
para("El Manager vincula la regla 100100 con el comando tiendacr-docker-drop.py en el agente del objetivo y un timeout de 180 segundos. El script valida que el origen pertenezca al segmento del laboratorio, protege las direcciones reservadas y aplica una regla acotada en DOCKER-USER para impedir conexiones nuevas de esa IP hacia el contenedor 172.18.0.2:3000. No bloquea SSH ni otros destinos. En la prueba SQLi, el log del agente registró ‘Bloqueo agregado: 10.10.10.30 hacia 172.18.0.2:3000’; una solicitud posterior desde Kali expiró por timeout, mientras la cadena mantuvo las reglas generales para otros orígenes.")
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
para("La operación probada cubrió detección y contención automatizada. La erradicación de la vulnerabilidad de código no se declara completada: la app es deliberadamente vulnerable y permanece dentro del entorno docente. En un sistema real, aislar no sustituye parchear o retirar el componente vulnerable.")
heading("5. Remediación y comparación antes/después", 1)
table(["Riesgo/ataque", "Antes", "Control aplicado", "Después y limitación"], [
    ["R03 SSH", "No había demostración reciente de detección funcional.", "Desactivar password auth y root remoto; permitir llaves. Regla 100101 para cinco eventos 5710/120 s.", "Hydra no pudo usar contraseñas; cinco conexiones a usuario ficticio generaron 100101. Reduce acceso por contraseña y mejora detección; no elimina todo intento de enumeración."],
    ["R01 SQLi", "Aplicación Juice Shop deliberadamente vulnerable y expuesta al segmento interno.", "UFW/Docker restringen acceso a Kali; Suricata detecta %27; Wazuh correlaciona y Active Response bloquea IP→contenedor por 180 s.", "La prueba disparó 100100 y el bloqueo negó la siguiente conexión. La vulnerabilidad de aplicación permanece; no se presenta como parche de código."],
    ["R02 traversal", "Sin alerta documentada anteriormente.", "Regla Suricata SID 1000004 y Wazuh 100102; servicio dentro del segmento y fuente limitada.", "EVE registró la solicitud; respuesta 200. No se verificó acceso a archivo. Para remediar código, se requiere parche/validación de rutas o reemplazo del objetivo."],
    ["R07 integridad", "FIM no verificado inicialmente.", "Ruta de laboratorio agregada a Syscheck en tiempo real.", "Configuración activa. Completar la comparación al confirmar el evento de cambio y su regla en alertas del Manager."],
])
para("La comparación demuestra prevención de acceso por contraseña y contención temporal de la prueba SQLi, pero no corrige el código vulnerable de Juice Shop. Para el escenario docente se acepta temporalmente ese riesgo con aislamiento, mínimo privilegio, monitoreo y respuesta. Para producción el riesgo no sería aceptable: se debe retirar Juice Shop y desplegar una aplicación corregida antes de recibir tráfico real.")
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
para("La topología de tres máquinas funciona en la red interna y el flujo de telemetría Wazuh/Suricata produjo alertas observables. Las reglas personalizadas distinguen reconocimiento, SSH, SQLi y traversal. El bloqueo automático de SQLi restringió correctamente la acción al flujo del atacante hacia el contenedor y, al vencer a los 180 segundos, recuperó el acceso HTTP 200. La prueba FIM alertó la modificación del archivo de control. La prueba de SSH confirmó que el acceso por contraseña está deshabilitado.")
para("El trabajo no demuestra que la inyección haya extraído datos ni que traversal haya leído archivos. La app vulnerable se conserva como blanco de laboratorio, por lo que su riesgo residual sigue siendo alto en el segmento. El feed del módulo de vulnerabilidades y los índices del SIEM se verificaron; falta confirmar en Dashboard el inventario de vulnerabilidades asociado al agente 001 antes de afirmar CVE en el objetivo.")
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
