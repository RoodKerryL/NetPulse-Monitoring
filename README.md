# 🌐 NetPulse — Enterprise Network Telemetry & Observability Stack

[![Docker Compose](https://img.shields.io/badge/Orchestration-Docker%20Compose-2496ED.svg?logo=docker&logoColor=white)](https://www.docker.com/)
[![Prometheus](https://img.shields.io/badge/Telemetry-Prometheus%20TSDB-E6522C.svg?logo=prometheus&logoColor=white)](https://prometheus.io/)
[![Grafana](https://img.shields.io/badge/Visualization-Grafana%2010-F46800.svg?logo=grafana&logoColor=white)](https://grafana.com/)
[![SNMP Protocol](https://img.shields.io/badge/Protocol-SNMP%20v2c%20%2F%20v3-0284c7.svg)](https://en.wikipedia.org/wiki/Simple_Network_Management_Protocol)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)
[![Author](https://img.shields.io/badge/Author-Rood%20Kerry%20Lucien-0ea5e9.svg)](https://github.com/RoodKerryL)

> **NetPulse** is a containerized, production-grade network telemetry and infrastructure observability stack. Designed for network engineers and IT operations, it provides real-time traffic analysis, automated threshold-based alerting (NOC Discord/Slack webhooks), and high-density Grafana dashboards for multi-vendor switches, routers, and WAN links.

---

## 🎯 The Engineering Challenge

In enterprise network management:
1. **Blind Spots in Traffic Spikes:** Without continuous timeseries telemetry, transient network congestion, packet drops, and duplex mismatches go unnoticed until users complain.
2. **Slow Mean Time to Resolution (MTTR):** Network technicians lack centralized dashboards correlating interface saturation with switch CPU and round-trip ICMP latency.
3. **Complex Setup:** Traditional enterprise NMS solutions (SolarWinds, PRTG) are monolithic, license-heavy, or non-reproducible.

**NetPulse** solves this with an Infrastructure-as-Code containerized stack that boots with a single command: **`docker compose up -d`**.

---

## 🏗️ Architecture & Telemetry Pipeline

```text
    +-------------------------------------------------------------+
    |                    Managed Network Fleet                    |
    |  - Core Switches (Cisco Catalyst 3850 / 9300)               |
    |  - Distribution & Access Switches (VLAN Trunks)             |
    |  - WAN Edge Routers (BGP / OSPF / IPsec Gateways)           |
    +---------------+-----------------------------+---------------+
                    | (SNMP Queries)              | (ICMP Probes)
                    v                             v
        +-----------------------+     +-----------------------+
        |     SNMP Exporter     |     |   Blackbox Exporter   |
        |      Port :9116       |     |      Port :9115       |
        +-----------+-----------+     +-----------+-----------+
                    |                             |
                    +--------------+--------------+
                                   |
                                   v (Scrape every 15s)
                    +-----------------------------+
                    |    Prometheus TSDB Engine   |
                    |         Port :9090          |
                    +--------------+--------------+
                                   |
                 +-----------------+-----------------+
                 |                                   |
                 v (Threshold Alerts)                v (Data Source Query)
    +-------------------------+         +-------------------------+
    |      Alertmanager       |         |    Grafana Dashboards   |
    |       Port :9093        |         |       Port :3000        |
    +------------+------------+         +------------+------------+
                 |                                   |
                 v (Webhooks)                        v
    +-------------------------+         +-------------------------+
    | Discord / Slack / Teams |         | NOC Dark-Mode Dashboard |
    |      Instant Alert      |         |  (Real-Time Analytics)  |
    +-------------------------+         +-------------------------+
```

---

## ✨ Key Capabilities

- 📊 **64-Bit High-Capacity Counters:** Gathers `ifHCInOctets` and `ifHCOutOctets` via SNMP to calculate exact bandwidth utilization on Gigabit and 10-Gigabit links without 32-bit counter roll-over bugs.
- ⏱️ **Sub-Second Latency Tracking:** Uses the Blackbox Exporter to track ICMP echo round-trip times (RTT) across internal gateways and external targets (e.g., `8.8.8.8`, `1.1.1.1`).
- 🔔 **Proactive NOC Alerting:** Pre-configured alert rules for:
  - `NetworkDeviceDown` (ICMP probe failure > 1 min)
  - `CriticalInterfaceDown` (Trunk/uplink link flapping)
  - `HighInterfaceBandwidthUtilization` (> 85% link capacity)
  - `HighSwitchCpuUtilization` (> 85% CPU for 5 min)
- 🚀 **Zero-Configuration Provisioning:** Grafana automatically registers Prometheus and mounts the complete **Network Overview Dashboard** on startup.
- 🧪 **Built-in Python Telemetry Simulator:** Includes a standalone Python script generating dynamic metrics on port `:9100` for live demonstrations and testing without physical hardware.

---

## 📋 Monitored OIDs & MIBs

| Metric Name | SNMP OID | MIB Source | Purpose |
| :--- | :--- | :--- | :--- |
| `sysUpTime` | `1.3.6.1.2.1.1.3` | RFC1213-MIB | Device uptime tracking and reboot detection |
| `ifOperStatus` | `1.3.6.1.2.1.2.2.1.8` | IF-MIB | Link state (1=UP, 2=DOWN, 3=TESTING) |
| `ifHCInOctets` | `1.3.6.1.2.1.31.1.1.1.6` | IF-MIB | 64-bit Inbound Octets (converted to bps) |
| `ifHCOutOctets` | `1.3.6.1.2.1.31.1.1.1.10` | IF-MIB | 64-bit Outbound Octets (converted to bps) |
| `ifHighSpeed` | `1.3.6.1.2.1.31.1.1.1.15` | IF-MIB | Port speed in Mbps (1000, 10000) |
| `probe_duration` | `N/A (ICMP)` | Blackbox | Network ping round-trip latency & jitter |
| `ciscoCpuUsage` | `1.3.6.1.4.1.9.9.109...` | CISCO-PROCESS-MIB | Cisco 5-minute CPU load average |

---

## 🚀 Quick Start Guide

### 1. Clone the Repository
```bash
git clone https://github.com/RoodKerryL/NetPulse-Monitoring.git
cd NetPulse-Monitoring
```

### 2. Launch the Entire Stack
```bash
docker compose up -d
```

### 3. Access Web Interfaces
- **Grafana (Dashboards):** [http://localhost:3000](http://localhost:3000) *(User: `admin` / Password: `admin`)*
- **Prometheus (Metrics & Targets):** [http://localhost:9090](http://localhost:9090)
- **Alertmanager (Alerts):** [http://localhost:9093](http://localhost:9093)

---

## 🧪 Simulation Mode (Testing Without Hardware)

If running in a lab or testing on a laptop without physical Cisco switches:
```bash
python simulator/snmp_simulator.py
```
This spawns a lightweight metrics server on `http://localhost:9100/metrics` providing dynamic traffic curves and latency metrics to populate the Grafana dashboard in real time!

---

## 👨‍💻 Author

**Rood Kerry Lucien**  
*Systems & Network Engineer | IT Infrastructure Specialist | Web Developer*  
- **Portfolio:** [roodkerryl.github.io](https://roodkerryl.github.io)  
- **LinkedIn:** [linkedin.com/in/jean-rood-kerry-l](https://www.linkedin.com/in/jean-rood-kerry-l/)  
- **GitHub:** [@RoodKerryL](https://github.com/RoodKerryL)

---

## 📄 License
This project is open-source under the [MIT License](LICENSE).
