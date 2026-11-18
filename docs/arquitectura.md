# Arquitectura del Mini SOC TiendaCR

El laboratorio separa el atacante, el servidor objetivo y el SIEM en máquinas
virtuales independientes. La red de ataques es una red interna de VirtualBox;
NAT se conserva únicamente para descargar actualizaciones y paquetes.

```text
                           NAT (actualizaciones)
                              |       |       |
                    +---------+-------+-------+---------+
                    |         red interna tiendacr-lab  |
                    |          10.10.10.0/24            |
                    +-----------+-----------+-----------+
                                |           |
             +------------------+           +------------------+
             |                                         |
   Kali-Linux-Atacante                         Ubuntu-Servidor-Objetivo
   10.10.10.30                                 10.10.10.10
   Nmap y pruebas                              Juice Shop
                                                Suricata + Wazuh Agent
                                                        |
                                                        | eventos
                                                        v
                                                  Ubuntu-Servidor-SIEM
                                                  10.10.10.20
                                                  Wazuh Manager
                                                  Indexer + Dashboard
```

El dashboard y los servicios de administración se limitarán a la red privada.
No se utilizará una interfaz puenteada ni se publicará Juice Shop en el
anfitrión.
