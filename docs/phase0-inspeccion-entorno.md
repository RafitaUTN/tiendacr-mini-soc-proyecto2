# Fase 0: inspección del entorno

**Proyecto:** Mini SOC TiendaCR  
**Fecha de inspección:** 10 de noviembre de 2026  
**Estado:** verificado; pendiente de autorización para modificar la infraestructura

## 1. Estado del entorno

| Componente | Resultado |
|---|---|
| Sistema anfitrión | Windows 11 Pro 64 bits, versión 10.0.26200 |
| Procesador | Intel Core i5-12450H, 8 núcleos y 12 procesadores lógicos |
| Memoria física | 15.71 GiB; aproximadamente 4.20 GiB libres durante la inspección |
| Disco C: | 475.81 GiB, 63.09 GiB libres |
| Disco D: | 260.67 GiB, 210.86 GiB libres |
| VirtualBox | 7.2.2r170484 |
| Vagrant | 2.4.9 |
| Virtualización | Hay un hipervisor activo; VirtualBox informa paginación anidada disponible |
| Internet | HTTPS hacia `releases.hashicorp.com` respondió `200 OK` |
| Docker, WSL y SSH | Disponibles en el anfitrión |

La inspección fue de solo lectura. No se iniciaron, detuvieron, eliminaron ni
reconfiguraron máquinas virtuales o redes.

## 2. Recursos existentes y problemas encontrados

### Máquinas virtuales registradas

- `GNS3 VM`: Ubuntu 64 bits, 2 GiB RAM, 1 CPU, estado `aborted`, interfaces
  host-only y NAT.
- `Taller-5-IDS`: Ubuntu 64 bits, 2 GiB RAM, 2 CPU, estado `poweroff`, una
  interfaz NAT.
- No hay máquinas del Mini SOC TiendaCR registradas.
- Ninguna de las máquinas registradas tiene snapshots.

### Redes

- Adaptador host-only de VirtualBox activo: `192.168.56.1/24`, DHCP
  deshabilitado.
- Red interna existente: `intnet`.
- No se encontró una red NAT Network configurada.
- La red del Mini SOC debe crearse de forma independiente para no alterar el
  laboratorio existente.

### Software e imágenes

- Hay cajas Vagrant para Ubuntu 24.04, Debian Bookworm y Ubuntu Jammy. Para
  compatibilidad con el arranque SSH observado en este entorno, se utilizará
  Ubuntu Jammy 22.04 LTS para objetivo y SIEM.
- No se encontró una caja o ISO de Kali Linux.
- No existe un `Vagrantfile` en el repositorio actual; hay un proyecto Vagrant
  independiente en `C:\Users\rafad\Music\Taller_5_seguridad`.
- El Extension Pack de VirtualBox reporta versión `7.2.14`, diferente de la
  versión instalada de VirtualBox (`7.2.2`). Debe alinearse antes de depender
  de funciones del paquete de extensión.

## 3. Requisitos faltantes

1. Imagen o caja Vagrant de Kali Linux compatible con VirtualBox.
2. Tres definiciones Vagrant separadas para atacante, objetivo y SIEM.
3. Imagen base Ubuntu Server LTS para objetivo y SIEM; puede reutilizarse una
   caja Ubuntu existente después de validar compatibilidad.
4. Red privada aislada y direccionamiento estático del laboratorio.
5. Espacio adicional para las imágenes y discos virtuales; se recomienda usar
   el disco D:.
6. Alineación de las versiones de VirtualBox y Extension Pack.

## 4. Distribución propuesta de recursos

La máquina tiene 16 GiB nominales, pero durante la inspección solo había
aproximadamente 4.20 GiB libres. Antes de iniciar las tres máquinas será
necesario cerrar aplicaciones no esenciales y verificar nuevamente la memoria
disponible.

### Perfil inicial conservador

| Máquina | CPU | RAM | Disco dinámico | Función |
|---|---:|---:|---:|---|
| Kali atacante | 2 vCPU | 2 GiB | 25 GiB | Ataques controlados |
| Ubuntu objetivo | 2 vCPU | 2 GiB | 30 GiB | Juice Shop, Suricata y agente |
| Ubuntu SIEM | 4 vCPU | 4 GiB | 60 GiB | Wazuh manager, indexer y dashboard |
| **Total** | **8 vCPU** | **8 GiB** | **115 GiB** | |

Este perfil deja aproximadamente 7.7 GiB para Windows en una situación ideal,
pero es ajustado si el sistema anfitrión continúa con solo 4.20 GiB libres.
El SIEM debe iniciarse y verificarse antes de arrancar las otras máquinas.
Si Wazuh requiere más memoria o el anfitrión muestra presión de memoria, la
alternativa es ejecutar las pruebas por etapas: SIEM + objetivo, y luego
incorporar Kali.

El almacenamiento propuesto cabe en el espacio libre del disco D:. Los discos
serán dinámicos para evitar reservar todo el espacio de inmediato.

Wazuh recomienda 8 GiB para una instalación de 1–25 agentes. Por la memoria
disponible del anfitrión, el SIEM se configuró inicialmente con 4 GiB. Esta es
una desviación documentada: si el indexador o dashboard no se mantienen
estables, la alternativa es ampliar la RAM del anfitrión o ejecutar el SIEM
por separado durante las demostraciones.

## 5. Diseño de red propuesto

Se usarán dos interfaces por máquina:

1. NAT únicamente para actualizaciones y descarga de paquetes.
2. Red interna aislada `tiendacr-lab` para todo el tráfico de pruebas.

| Máquina | Hostname | IP privada | Interfaces permitidas |
|---|---|---|---|
| Kali atacante | `kali-linux-atacante` | `10.10.10.30/24` | NAT + red interna |
| Ubuntu servidor objetivo | `ubuntu-servidor-objetivo` | `10.10.10.10/24` | NAT + red interna |
| Ubuntu servidor SIEM | `ubuntu-servidor-siem` | `10.10.10.20/24` | NAT + red interna |

El objetivo recibirá ataques únicamente desde `10.10.10.30`. El agente
enviará eventos al SIEM en `10.10.10.20`. El dashboard se expondrá solo en la
red interna y no se usará una interfaz puenteada. Los puertos concretos se
documentarán y restringirán mediante firewall en la Fase 1.

## 6. Plan de implementación

1. Autorizar el paso de inspección a implementación.
2. Alinear VirtualBox y Extension Pack, sin tocar las máquinas existentes.
3. Obtener y validar las imágenes necesarias.
4. Crear el `Vagrantfile` y la estructura del Mini SOC en este repositorio.
5. Levantar y verificar primero la red y las tres máquinas.
6. Aplicar firewall y endurecimiento SSH.
7. Instalar Juice Shop, Suricata y Wazuh.
8. Ejecutar ataques exclusivamente contra `10.10.10.10`.
9. Validar alertas, regla personalizada, respuesta automática y evidencias.
10. Documentar resultados y reevaluar los riesgos.

## 7. Evidencias que deben conservarse

- Salida de versiones de Windows, VirtualBox y Vagrant.
- Inventario de máquinas, redes y estados previo a los cambios.
- Pruebas de conectividad entre las tres IP privadas.
- Configuración de recursos asignados.
- Capturas y registros de cada verificación posterior.

No se deben registrar contraseñas, tokens, claves privadas ni credenciales en
el repositorio.
