# Mini SOC TiendaCR — Proyecto 2

Laboratorio académico local con tres VM en VirtualBox/Vagrant, OWASP Juice Shop,
Suricata y Wazuh. Las pruebas se limitan a `10.10.10.0/24` y no se dirige
tráfico a redes o sistemas externos.

## Estado verificado — 18 de noviembre de 2026

- Kali atacante: `10.10.10.30`.
- Objetivo Ubuntu 22.04.5: `10.10.10.10`, Juice Shop 17.2.0 en Docker,
  Suricata 6.0.4 y Wazuh Agent 001 activo.
- SIEM Ubuntu 24.04.3: `10.10.10.20`, Wazuh Manager, Indexer, Dashboard y
  Filebeat activos.
- El Vagrantfile fija Ubuntu Jammy para el objetivo y Bento Ubuntu 24.04.3 para
  SIEM. SSH usa llaves, sin root remoto ni autenticación por contraseña.
- Reglas personalizadas Suricata: SID 1000001–1000004. Reglas Wazuh:
  100100 (SQLi), 100101 (umbral de intentos SSH) y 100102 (traversal).
- Evidencia real sanitizada en [`evidence/2026-11-18`](evidence/2026-11-18/).
- Informe final de 20 páginas: [`DOCX`](Informe%20tecnico/Informe%20de%20investigacion%20-%20Proyecto%202%20final.docx) y [`PDF`](Informe%20tecnico/Informe%20de%20investigacion%20-%20Proyecto%202%20final.pdf).
- Vulnerabilidades: feed/indexer activos; confirmar en Dashboard el inventario específico del agente objetivo antes de afirmar CVE detectados.

## Requisitos del equipo

- Windows 11, VirtualBox y Vagrant.
- Al menos 16 GiB de RAM recomendados; iniciar/provisionar una VM por vez.
- La VM SIEM usa 6 GiB y requiere varios minutos al iniciar.

## Operación básica

```powershell
vagrant validate
vagrant status
vagrant up siem
vagrant up target
vagrant up attacker
```

Verificar servicios y agente:

```powershell
vagrant ssh siem -c "sudo systemctl is-active wazuh-manager wazuh-indexer wazuh-dashboard filebeat"
vagrant ssh siem -c "sudo /var/ossec/bin/agent_control -lc"
vagrant ssh target -c "sudo systemctl is-active docker suricata wazuh-agent tiendacr-docker-filter.service"
vagrant ssh attacker -c "curl -sS -o /dev/null -w '%{http_code}\n' http://10.10.10.10:3000/"
```

Para el procedimiento de validación y demostración consulte
[`docs/comandos-finalizacion.md`](docs/comandos-finalizacion.md). La descripción
de controles y la matriz de puertos están en
[`docs/direccionamiento.md`](docs/direccionamiento.md).

## Informe y modalidad

El informe conserva la investigación inicial y añade resultados medidos. Está
disponible en el repositorio público [RafitaUTN/tiendacr-mini-soc-proyecto2](https://github.com/RafitaUTN/tiendacr-mini-soc-proyecto2). El estudiante indicó que trabaja solo; el
enunciado del curso plantea parejas, por lo que la modalidad individual debe
confirmarse con el profesor. No se atribuyen aportes ni coevaluaciones ficticias.
La demostración en vivo y la entrega mediante la plataforma del curso son
responsabilidad del estudiante.

## Seguridad y publicación

No versionar claves privadas, credenciales, tokens, archivos `.env`, discos de
VM ni logs completos. Las evidencias publicadas están reducidas y sanitizadas;
el repositorio se preparó con un historial limpio, separado del historial local
anterior. Las claves de Indexer se generan al provisionar y se guardan en el
keystore local de Wazuh; nunca se incluyen en este repositorio.
