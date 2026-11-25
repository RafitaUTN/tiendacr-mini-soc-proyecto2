# Cierre de correcciones — Mini SOC TiendaCR

La intervención técnica y las pruebas locales fueron autorizadas por Rafael y
se completaron el 18 de noviembre de 2026. La tabla resume lo realizado y lo
que aún debe revisar personalmente el estudiante antes de entregar.

| Área | Resultado comprobado | Estado / siguiente paso |
|---|---|---|
| Vagrant y tres VM | `vagrant validate`; las VMs `attacker`, `target` y `siem` están en ejecución. | Terminado localmente. |
| Telemetría | Manager, Indexer, Dashboard y Filebeat activos; agente 001 Active. Filebeat prueba TLS/conexión; alertas de ataques llegan a Manager y al Indexer. | Terminado para logs/alertas. |
| Cuenta Manager→Indexer | Cuenta técnica dedicada y rol de alcance limitado a índices `wazuh-states-*`; contraseña aleatoria guardada en el keystore de Wazuh. | Provisioning reproducible en `provisioning/siem/`. |
| Firewall y SSH | Reglas por interfaz/origen y SSH con llave; sin root ni autenticación por contraseña. | Revisar con `docs/direccionamiento.md` al volver a provisionar. |
| Suricata y Wazuh | Cuatro firmas Suricata y reglas Wazuh 100100/100101/100102 con validaciones sintácticas. | Terminado localmente. |
| Active Response | SQLi de prueba activó el bloqueo acotado durante 180 s; se retiró al vencer y HTTP volvió a 200. | Terminado localmente. |
| Pruebas y evidencias | Reconocimiento, SSH, SQLi, traversal y FIM desde Kali revalidados; evidencias E07/E08 actualizadas. | Pruebas técnicas terminadas; demo oral pendiente. |
| Vulnerabilidades | Consulta autenticada del índice global: 629 paquetes y 2578 registros vinculados a `agent.id=001`; muestra de CVE-2026-99282 del kernel bajo evaluación. | Inventario del agente comprobado; priorizar CVE/estado en Dashboard. |
| Remediación | SSH por contraseña rechaza; WAF devuelve 403 al SQLi/traversal probados incluso después del timeout de Active Response; HTTP normal sigue en 200. | Control compensatorio validado. Juice Shop permanece vulnerable a variantes y requiere aislamiento; no se afirma parche de código. |
| FIM desde Kali | Llave temporal autorizada simuló acceso comprometido; modificación benigna disparó Wazuh 550; la llave se revocó y borró. | Cumple como escenario de integridad post-acceso simulado. |
| Informe | DOCX/PDF final de 19 páginas; fuentes, latencias, ATT&CK, riesgos y anexos. Publicado junto a matriz requisito por requisito. | Revisado; revisar antes de entrega académica. |
| Repositorio público | [RafitaUTN/tiendacr-mini-soc-proyecto2](https://github.com/RafitaUTN/tiendacr-mini-soc-proyecto2), público, historial limpio con un commit del Proyecto 2; archivos seleccionados y evidencia sanitizada. | Publicado y verificado. |
| Individual / coevaluación | No se inventaron contribuciones de otra persona. | Pendiente: confirmar modalidad individual, ejecutar defensa oral y completar los formularios aplicables. |

## Revalidación local

```powershell
vagrant validate
vagrant status
vagrant ssh siem -c "sudo systemctl is-active wazuh-manager wazuh-indexer wazuh-dashboard filebeat"
vagrant ssh siem -c "sudo /var/ossec/bin/agent_control -lc"
vagrant ssh target -c "sudo suricata -T -c /etc/suricata/suricata.yaml -v"
```

La práctica se limita a la red aislada `10.10.10.0/24`. La demostración debe
repetirse solo en ese entorno, conforme a `docs/comandos-finalizacion.md`.
