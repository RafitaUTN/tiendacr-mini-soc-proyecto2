# Cierre de correcciones — Mini SOC TiendaCR

La intervención técnica y las pruebas locales fueron autorizadas por Rafael y
se completaron el 18 de noviembre de 2026. La tabla resume lo realizado y lo
que aún debe revisar personalmente el estudiante antes de entregar.

| Área | Resultado comprobado | Estado / siguiente paso |
|---|---|---|
| Vagrant y tres VM | `vagrant validate`; las VMs `attacker`, `target` y `siem` están en ejecución. | Terminado localmente. |
| Telemetría | Manager, Indexer, Dashboard y Filebeat activos; agente 001 Active. Las alertas de pruebas llegan a Wazuh. | Terminado localmente. |
| Cuenta Manager→Indexer | Cuenta técnica dedicada y rol de alcance limitado a índices `wazuh-states-*`; contraseña aleatoria guardada en el keystore de Wazuh. | Provisioning reproducible en `provisioning/siem/`. |
| Firewall y SSH | Reglas por interfaz/origen y SSH con llave; sin root ni autenticación por contraseña. | Revisar con `docs/direccionamiento.md` al volver a provisionar. |
| Suricata y Wazuh | Cuatro firmas Suricata y reglas Wazuh 100100/100101/100102 con validaciones sintácticas. | Terminado localmente. |
| Active Response | SQLi de prueba activó el bloqueo acotado durante 180 s; se retiró al vencer y HTTP volvió a 200. | Terminado localmente. |
| Pruebas y evidencias | Reconocimiento, SSH, SQLi, traversal y FIM registrados en archivos sanitizados. | Terminado localmente; demo oral pendiente. |
| Vulnerabilidades | Feed finalizó la actualización y el Manager creó índices de estado locales. | Confirmar en Dashboard la vista del agente 001 y guardar captura; aún no se atribuyen CVE al objetivo sin esa verificación. |
| Informe | DOCX final de 20 páginas con resultados, latencias, ATT&CK, riesgos y anexo de evidencias; PDF renderizado para revisión. | Revisar personalmente datos y estilo antes de entregar. |
| Repositorio público | Publicación autorizada por el estudiante; se creará con historial limpio y solo archivos seleccionados del Proyecto 2. | En publicación. |
| Individual / coevaluación | No se inventaron contribuciones de otra persona. | Confirmar con el profesor que acepta modalidad individual; completar la defensa y los formularios que correspondan. |

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
