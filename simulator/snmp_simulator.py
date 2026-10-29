#!/usr/bin/env python3
"""
NetPulse Synthetic Network Telemetry Simulator
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Generates realistic Prometheus metrics on port 9100 to simulate
enterprise Cisco switches, trunk bandwidth, and ICMP latency without physical hardware.

Author: Rood Kerry Lucien
"""

from __future__ import annotations
import time
import math
import random
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = 9100

class MetricsHandler(BaseHTTPRequestHandler):
    start_time = time.time()
    rx_counter = 100000000
    tx_counter = 85000000

    def do_GET(self):
        if self.path == "/metrics" or self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/plain; version=0.0.4; charset=utf-8")
            self.end_headers()
            
            elapsed = time.time() - self.start_time
            sine_wave = (math.sin(elapsed / 15.0) + 1.0) / 2.0  # 0.0 to 1.0

            # Simulate increasing byte counters (bandwidth)
            MetricsHandler.rx_counter += int(2500000 * (0.8 + sine_wave * 0.5))
            MetricsHandler.tx_counter += int(1800000 * (0.7 + sine_wave * 0.4))

            # Simulate metrics
            cpu_val = round(22.0 + sine_wave * 18.0 + random.uniform(-2, 2), 1)
            mem_val = round(42.0 + random.uniform(-1, 1), 1)
            latency_core = round(0.008 + sine_wave * 0.004 + random.uniform(0, 0.002), 4)
            latency_wan = round(0.024 + sine_wave * 0.012 + random.uniform(0, 0.005), 4)

            payload = f"""# HELP probe_success Whether the probe was successful
# TYPE probe_success gauge
probe_success{{instance="192.168.10.1"}} 1
probe_success{{instance="192.168.10.11"}} 1
probe_success{{instance="192.168.10.12"}} 1
probe_success{{instance="192.168.1.1"}} 1
probe_success{{instance="192.168.20.5"}} 1
probe_success{{instance="8.8.8.8"}} 1

# HELP probe_duration_seconds Round-trip latency in seconds
# TYPE probe_duration_seconds gauge
probe_duration_seconds{{instance="192.168.10.1"}} {latency_core}
probe_duration_seconds{{instance="192.168.10.11"}} {latency_core + 0.002}
probe_duration_seconds{{instance="192.168.1.1"}} {latency_wan}
probe_duration_seconds{{instance="8.8.8.8"}} {latency_wan + 0.015}

# HELP ifHCInOctets Total bytes received on interface
# TYPE ifHCInOctets counter
ifHCInOctets{{instance="192.168.10.1",ifDescr="GigabitEthernet0/1-Trunk"}} {MetricsHandler.rx_counter}
ifHCInOctets{{instance="192.168.10.11",ifDescr="GigabitEthernet0/24-Uplink"}} {int(MetricsHandler.rx_counter * 0.6)}

# HELP ifHCOutOctets Total bytes sent on interface
# TYPE ifHCOutOctets counter
ifHCOutOctets{{instance="192.168.10.1",ifDescr="GigabitEthernet0/1-Trunk"}} {MetricsHandler.tx_counter}
ifHCOutOctets{{instance="192.168.10.11",ifDescr="GigabitEthernet0/24-Uplink"}} {int(MetricsHandler.tx_counter * 0.6)}

# HELP ifOperStatus Current interface operational status (1=up, 2=down)
# TYPE ifOperStatus gauge
ifOperStatus{{instance="192.168.10.1",ifDescr="GigabitEthernet0/1-Trunk",ifAlias="Core Trunk"}} 1
ifOperStatus{{instance="192.168.10.11",ifDescr="GigabitEthernet0/24-Uplink",ifAlias="Floor 1 Trunk"}} 1

# HELP ciscoCpuUsage5Min 5-minute CPU usage percentage
# TYPE ciscoCpuUsage5Min gauge
ciscoCpuUsage5Min{{instance="192.168.10.1"}} {cpu_val}
ciscoCpuUsage5Min{{instance="192.168.1.1"}} {cpu_val + 6.0}

# HELP ciscoMemUsage Memory usage percentage
# TYPE ciscoMemUsage gauge
ciscoMemUsage{{instance="192.168.10.1"}} {mem_val}
ciscoMemUsage{{instance="192.168.1.1"}} {mem_val + 8.0}
"""
            self.wfile.write(payload.encode("utf-8"))
        else:
            self.send_error(404, "Endpoint not found. Use /metrics")

    def log_message(self, format, *args):
        pass  # Quiet logging

def main():
    server = HTTPServer(("0.0.0.0", PORT), MetricsHandler)
    print(f"[*] NetPulse Telemetry Simulator active on http://0.0.0.0:{PORT}/metrics")
    print("[*] Generating continuous synthetic network telemetry (Ctrl+C to stop)...")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[!] Simulator stopped.")

if __name__ == "__main__":
    main()
