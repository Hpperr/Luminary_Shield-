#!/usr/bin/env python3
"""
LUMINARY SHIELD v1.0 - Ultimate Defense & Detection Framework
Advanced Security Defense - Real-time Monitoring - Zero Trust

Author: F1REW0LF
License: MIT
"""

import sys
import os
import re
import json
import time
import socket
import threading
import queue
import subprocess
import signal
import hashlib
import base64
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse

try:
    from scapy.all import *
    from scapy.layers.inet import IP, TCP, UDP, ICMP
    from scapy.layers.l2 import ARP, Ether
    from scapy.layers.dns import DNS, DNSQR, DNSRR
    from scapy.layers.http import HTTP, HTTPRequest
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

VERSION = "1.0.0"
AUTHOR = "F1REW0LF"
LICENSE = "MIT"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    GOLD = '\033[93m'
    NEON = '\033[96m'
    WHITE = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    MAGENTA = '\033[95m'
    ORANGE = '\033[38;5;208m'

def cprint(text, color=Colors.WHITE, bold=False):
    if bold:
        print(f"{Colors.BOLD}{color}{text}{Colors.WHITE}")
    else:
        print(f"{color}{text}{Colors.WHITE}")

def print_banner():
    banner = f"""
{Colors.CYAN}{Colors.BOLD}    ██╗     ██╗███╗   ███╗██╗███╗   ██╗ █████╗ ██████╗ ██╗   ██╗    ███████╗██╗  ██╗██╗███████╈╗██████╗ 
    ██║     ██║████╗ ████║██║████╗  ██║██╔══██╗██╔══██╗╚██╗ ██╔╝    ██╔════╝██║  ██║██║██╔════╝██╔══██╗
    ██║     ██║██╔████╔██║██║██╔██╗ ██║███████║██████╔╝ ╚████╔╝     ███████╗███████║██║███████╗██████╔╝
    ██║     ██║██║╚██╔╝██║██║██║╚██╗██║██╔══██║██╔══██╗  ╚██╔╝      ╚════██║██╔══██║██║╚════██║██╔══██╗
    ███████╗██║██║ ╚═╝ ██║██║██║ ╚████║██║  ██║██║  ██║   ██║       ███████║██║  ██║██║███████║██║  ██║
    ╚══════╝╚═╝╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝       ╚══════╝╚═╝  ╚═╝╚═╝╚══════╝╚═╝  ╚═╝
                                                   
{Colors.NEON}          ULTIMATE DEFENSE & DETECTION FRAMEWORK{Colors.WHITE}
{Colors.CYAN}    Advanced Security Defense - Real-time Monitoring{Colors.WHITE}
{Colors.YELLOW}    Version {VERSION} | Author: {AUTHOR} | {LICENSE}{Colors.WHITE}
    """
    print(banner)
    print("=" * 80)

# ==================== THREAT DATABASE ====================
class ThreatDatabase:
    """Database of known threats and signatures"""
    
    MALICIOUS_IPS = {
        '10.0.0.0/8': 'Internal Network',
        '172.16.0.0/12': 'Internal Network',
        '192.168.0.0/16': 'Internal Network',
        '127.0.0.0/8': 'Localhost',
        '0.0.0.0/8': 'Invalid',
        '169.254.0.0/16': 'Link-local',
        '224.0.0.0/4': 'Multicast',
        '240.0.0.0/4': 'Reserved',
        '255.255.255.255/32': 'Broadcast'
    }
    
    MALICIOUS_PORTS = {
        22: 'SSH - Brute Force',
        23: 'Telnet - Brute Force',
        25: 'SMTP - Spam',
        53: 'DNS - Amplification',
        80: 'HTTP - Web Attack',
        135: 'RPC - Exploit',
        139: 'NetBIOS - Exploit',
        445: 'SMB - Exploit',
        1433: 'MSSQL - Brute Force',
        3306: 'MySQL - Brute Force',
        3389: 'RDP - Brute Force',
        5432: 'PostgreSQL - Brute Force',
        6379: 'Redis - Exploit',
        8080: 'HTTP-Alt - Web Attack',
        8443: 'HTTPS-Alt - Web Attack'
    }
    
    MALICIOUS_PATTERNS = [
        # SQL Injection
        r'(\%27)|(\')|(\-\-)|(\%23)|(#)',
        r'((\%3D)|(=))[^\n]*((\%27)|(\')|(\-\-)|(\%3B)|(;))',
        # XSS
        r'((\%3C)|<)((\%2F)|/)*[a-z0-9\%]+((\%3E)|>)',
        r'<script.*?>.*?</script>',
        r'javascript:',
        # Command Injection
        r';.*?(\||\&|\;)',
        r'\|\|.*?(\||\&|\;)',
        r'`.*?`',
        # Path Traversal
        r'\.\./',
        r'\.\.\\',
        # File Inclusion
        r'php://',
        r'file://',
        r'http://.*?\.(php|txt|cfg|conf|ini)',
    ]
    
    MALICIOUS_USER_AGENTS = [
        'sqlmap', 'nmap', 'nikto', 'w3af', 'wpscan', 'dirb',
        'gobuster', 'ffuf', 'wfuzz', 'arachni', 'zap', 'burp',
        'python-requests', 'curl', 'wget', 'masscan', 'zmap'
    ]
    
    @classmethod
    def check_ip(cls, ip: str) -> Optional[str]:
        for subnet, desc in cls.MALICIOUS_IPS.items():
            if ip in ipaddress.ip_network(subnet):
                return desc
        return None
    
    @classmethod
    def check_port(cls, port: int) -> Optional[str]:
        return cls.MALICIOUS_PORTS.get(port)
    
    @classmethod
    def check_pattern(cls, data: str) -> Optional[str]:
        for pattern in cls.MALICIOUS_PATTERNS:
            if re.search(pattern, data, re.IGNORECASE):
                return "Malicious pattern detected"
        return None
    
    @classmethod
    def check_user_agent(cls, ua: str) -> bool:
        for malicious in cls.MALICIOUS_USER_AGENTS:
            if malicious.lower() in ua.lower():
                return True
        return False

# ==================== NETWORK MONITOR ====================
class NetworkMonitor:
    def __init__(self, interface: str = 'eth0'):
        self.interface = interface
        self.running = False
        self.stop_event = threading.Event()
        self.packets = []
        self.alerts = []
        self.stats = {'packets': 0, 'alerts': 0, 'threats': 0}
        self.lock = threading.Lock()
        self.db = ThreatDatabase()
    
    def start(self):
        cprint("[MONITOR] Starting network monitoring...", Colors.BLUE)
        
        if not SCAPY_AVAILABLE:
            cprint("[-] Scapy not available", Colors.RED)
            return
        
        self.running = True
        
        def packet_handler(pkt):
            if not self.running:
                return
            
            with self.lock:
                self.stats['packets'] += 1
            
            self._analyze_packet(pkt)
        
        try:
            sniff(iface=self.interface, prn=packet_handler, store=0,
                  stop_filter=lambda x: self.stop_event.is_set())
        except Exception as e:
            cprint(f"[-] Sniff error: {e}", Colors.RED)
    
    def _analyze_packet(self, pkt):
        try:
            # IP Layer
            if pkt.haslayer(IP):
                ip = pkt[IP]
                src = ip.src
                dst = ip.dst
                
                # Check for suspicious IPs
                if self.db.check_ip(src):
                    self._alert(f"Suspicious source IP: {src}", Colors.RED)
                
                # TCP Layer
                if pkt.haslayer(TCP):
                    tcp = pkt[TCP]
                    sport = tcp.sport
                    dport = tcp.dport
                    
                    # Check for suspicious ports
                    if self.db.check_port(sport):
                        self._alert(f"Suspicious source port: {sport}", Colors.RED)
                    if self.db.check_port(dport):
                        self._alert(f"Suspicious destination port: {dport}", Colors.RED)
                    
                    # SYN flood detection
                    if tcp.flags == 'S':
                        self._alert(f"SYN packet detected: {src} -> {dst}:{dport}", Colors.YELLOW)
                
                # UDP Layer
                if pkt.haslayer(UDP):
                    udp = pkt[UDP]
                    if udp.dport == 53:
                        self._alert(f"DNS query detected: {src} -> {dst}", Colors.DIM)
            
            # HTTP Layer
            if pkt.haslayer(HTTPRequest):
                http = pkt[HTTPRequest]
                host = http.Host.decode() if http.Host else 'unknown'
                path = http.Path.decode() if http.Path else '/'
                method = http.Method.decode() if http.Method else 'GET'
                
                # Check for malicious patterns
                if self.db.check_pattern(path):
                    self._alert(f"Malicious HTTP request: {method} {host}{path}", Colors.RED)
                
                # Check User-Agent
                if http.User_Agent:
                    ua = http.User_Agent.decode()
                    if self.db.check_user_agent(ua):
                        self._alert(f"Suspicious User-Agent: {ua}", Colors.YELLOW)
        
        except Exception as e:
            pass
    
    def _alert(self, message: str, color=Colors.RED):
        with self.lock:
            alert = {
                'timestamp': datetime.now().isoformat(),
                'message': message,
                'color': color
            }
            self.alerts.append(alert)
            self.stats['alerts'] += 1
            self.stats['threats'] += 1
        
        cprint(f"[!] {message}", color, bold=True)
    
    def get_stats(self) -> Dict:
        with self.lock:
            return self.stats.copy()
    
    def get_alerts(self) -> List[Dict]:
        with self.lock:
            return self.alerts.copy()
    
    def stop(self):
        cprint("[MONITOR] Stopping network monitoring...", Colors.YELLOW)
        self.running = False
        self.stop_event.set()
        cprint("[+] Monitoring stopped", Colors.GREEN)

# ==================== SYSTEM MONITOR ====================
class SystemMonitor:
    def __init__(self):
        self.running = False
        self.stop_event = threading.Event()
        self.alerts = []
        self.stats = {}
        self.lock = threading.Lock()
    
    def start(self):
        cprint("[SYSTEM] Starting system monitoring...", Colors.BLUE)
        self.running = True
        
        def monitor():
            while self.running and not self.stop_event.is_set():
                self._check_system()
                time.sleep(5)
        
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()
    
    def _check_system(self):
        if not PSUTIL_AVAILABLE:
            return
        
        try:
            # CPU
            cpu = psutil.cpu_percent(interval=0.1)
            if cpu > 80:
                self._alert(f"High CPU usage: {cpu}%", Colors.RED)
            
            # Memory
            mem = psutil.virtual_memory()
            if mem.percent > 80:
                self._alert(f"High memory usage: {mem.percent}%", Colors.RED)
            
            # Disk
            disk = psutil.disk_usage('/')
            if disk.percent > 80:
                self._alert(f"High disk usage: {disk.percent}%", Colors.RED)
            
            # Network connections
            connections = psutil.net_connections()
            established = len([c for c in connections if c.status == 'ESTABLISHED'])
            if established > 100:
                self._alert(f"Many established connections: {established}", Colors.YELLOW)
            
            # Running processes
            processes = len(psutil.pids())
            if processes > 500:
                self._alert(f"Many running processes: {processes}", Colors.YELLOW)
            
        except Exception as e:
            pass
    
    def _alert(self, message: str, color=Colors.RED):
        with self.lock:
            alert = {
                'timestamp': datetime.now().isoformat(),
                'message': message,
                'color': color
            }
            self.alerts.append(alert)
        
        cprint(f"[!] {message}", color, bold=True)
    
    def get_alerts(self) -> List[Dict]:
        with self.lock:
            return self.alerts.copy()
    
    def stop(self):
        cprint("[SYSTEM] Stopping system monitoring...", Colors.YELLOW)
        self.running = False
        self.stop_event.set()
        cprint("[+] System monitoring stopped", Colors.GREEN)

# ==================== WEB FIREWALL ====================
class WebFirewall:
    def __init__(self, port: int = 8080):
        self.port = port
        self.running = False
        self.server = None
        self.db = ThreatDatabase()
        self.blocked_ips = set()
        self.blocked_patterns = []
        self.stats = {'requests': 0, 'blocked': 0}
    
    def start(self):
        cprint("[FIREWALL] Starting web firewall on port {}...".format(self.port), Colors.BLUE)
        
        try:
            from flask import Flask, request, jsonify
            
            app = Flask(__name__)
            
            @app.before_request
            def before_request():
                self.stats['requests'] += 1
                
                # Check IP
                ip = request.remote_addr
                if ip in self.blocked_ips:
                    self._block_request(f"Blocked IP: {ip}")
                    return "Access Denied", 403
                
                # Check User-Agent
                ua = request.headers.get('User-Agent', '')
                if self.db.check_user_agent(ua):
                    self.blocked_ips.add(ip)
                    self._block_request(f"Suspicious User-Agent: {ua}")
                    return "Access Denied", 403
                
                # Check URL path
                path = request.path
                if self.db.check_pattern(path):
                    self.blocked_ips.add(ip)
                    self._block_request(f"Malicious path: {path}")
                    return "Access Denied", 403
                
                # Check query parameters
                for key, value in request.args.items():
                    if self.db.check_pattern(value):
                        self.blocked_ips.add(ip)
                        self._block_request(f"Malicious parameter: {key}={value}")
                        return "Access Denied", 403
            
            @app.route('/')
            def index():
                return """
                <h1>LUMINARY SHIELD - Web Firewall</h1>
                <p>Protected by advanced security system</p>
                """
            
            @app.route('/admin')
            def admin():
                ip = request.remote_addr
                if ip not in self.blocked_ips:
                    return """
                    <h1>Admin Panel</h1>
                    <p>Status: Active</p>
                    <p>Requests: {}</p>
                    <p>Blocked: {}</p>
                    """.format(self.stats['requests'], self.stats['blocked'])
                return "Access Denied", 403
            
            @app.route('/api/status')
            def status():
                return jsonify({
                    'status': 'active',
                    'requests': self.stats['requests'],
                    'blocked': self.stats['blocked'],
                    'blocked_ips': len(self.blocked_ips)
                })
            
            self.server = app
            self.running = True
            app.run(host='0.0.0.0', port=self.port, debug=False)
            
        except Exception as e:
            cprint(f"[-] Firewall start failed: {e}", Colors.RED)
    
    def _block_request(self, reason: str):
        self.stats['blocked'] += 1
        cprint(f"[FIREWALL] Blocked: {reason}", Colors.RED)
    
    def stop(self):
        cprint("[FIREWALL] Stopping web firewall...", Colors.YELLOW)
        self.running = False
        if self.server:
            self.server.do_teardown_appcontext()
        cprint("[+] Web firewall stopped", Colors.GREEN)

# ==================== INTRUSION DETECTION ====================
class IntrusionDetection:
    def __init__(self):
        self.db = ThreatDatabase()
        self.alerts = []
        self.stats = {'scans': 0, 'attacks': 0, 'alerts': 0}
        self.lock = threading.Lock()
    
    def analyze_log(self, log_file: str):
        cprint("[IDS] Analyzing log file: {}".format(log_file), Colors.BLUE)
        
        try:
            with open(log_file, 'r') as f:
                for line in f:
                    self._analyze_line(line)
        except Exception as e:
            cprint(f"[-] Log analysis failed: {e}", Colors.RED)
    
    def _analyze_line(self, line: str):
        # Check for attack patterns
        if self.db.check_pattern(line):
            self._alert(f"Attack pattern detected: {line[:100]}", Colors.RED)
        
        # Check for suspicious IPs
        ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        ips = re.findall(ip_pattern, line)
        for ip in ips:
            if self.db.check_ip(ip):
                self._alert(f"Suspicious IP: {ip}", Colors.RED)
        
        # Check for port scans
        port_pattern = r'port\s+(\d+)'
        ports = re.findall(port_pattern, line, re.IGNORECASE)
        for port in ports:
            if self.db.check_port(int(port)):
                self._alert(f"Suspicious port: {port}", Colors.YELLOW)
    
    def _alert(self, message: str, color=Colors.RED):
        with self.lock:
            alert = {
                'timestamp': datetime.now().isoformat(),
                'message': message,
                'color': color
            }
            self.alerts.append(alert)
            self.stats['alerts'] += 1
        
        cprint(f"[IDS] {message}", color, bold=True)
    
    def get_alerts(self) -> List[Dict]:
        with self.lock:
            return self.alerts.copy()

# ==================== MAIN FRAMEWORK ====================
class LuminaryShield:
    def __init__(self, interface: str = 'eth0'):
        self.interface = interface
        self.network_monitor = None
        self.system_monitor = None
        self.web_firewall = None
        self.ids = IntrusionDetection()
        self.running = True
        self.components = []
        
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        cprint("\n[!] Luminary Shield deactivating...", Colors.RED)
        self.running = False
        self.stop_all()
        sys.exit(0)
    
    def show_menu(self):
        print(f"""
{Colors.BLUE}{'='*60}{Colors.WHITE}
{Colors.BOLD}LUMINARY SHIELD - Defense Menu{Colors.WHITE}
{Colors.BLUE}{'='*60}{Colors.WHITE}
[1] Network Monitor (Packet Analysis)
[2] System Monitor (Performance)
[3] Web Firewall (HTTP Protection)
[4] Intrusion Detection System
[5] Show Alerts
[6] Show Stats
[7] Stop All
[8] Exit
""")
    
    def start_network_monitor(self):
        if self.network_monitor and self.network_monitor.running:
            cprint("[!] Network monitor already running", Colors.YELLOW)
            return
        
        self.network_monitor = NetworkMonitor(self.interface)
        thread = threading.Thread(target=self.network_monitor.start, daemon=True)
        thread.start()
        self.components.append(('Network Monitor', self.network_monitor))
        cprint("[+] Network monitor started", Colors.GREEN)
    
    def start_system_monitor(self):
        if self.system_monitor and self.system_monitor.running:
            cprint("[!] System monitor already running", Colors.YELLOW)
            return
        
        self.system_monitor = SystemMonitor()
        self.system_monitor.start()
        self.components.append(('System Monitor', self.system_monitor))
        cprint("[+] System monitor started", Colors.GREEN)
    
    def start_web_firewall(self):
        if self.web_firewall and self.web_firewall.running:
            cprint("[!] Web firewall already running", Colors.YELLOW)
            return
        
        port = input("[>] Port (8080): ").strip() or "8080"
        self.web_firewall = WebFirewall(int(port))
        thread = threading.Thread(target=self.web_firewall.start, daemon=True)
        thread.start()
        self.components.append(('Web Firewall', self.web_firewall))
        cprint("[+] Web firewall started on port {}".format(port), Colors.GREEN)
    
    def run_ids(self):
        log_file = input("[>] Log file path: ").strip()
        if os.path.exists(log_file):
            self.ids.analyze_log(log_file)
        else:
            cprint("[-] Log file not found", Colors.RED)
    
    def show_alerts(self):
        alerts = []
        if self.network_monitor:
            alerts.extend(self.network_monitor.get_alerts())
        if self.system_monitor:
            alerts.extend(self.system_monitor.get_alerts())
        alerts.extend(self.ids.get_alerts())
        
        if not alerts:
            cprint("[!] No alerts", Colors.YELLOW)
            return
        
        print("\n" + "="*60)
        cprint(" ALERTS", Colors.RED, bold=True)
        print("="*60)
        for alert in alerts[-20:]:
            print("[{}] {}".format(alert['timestamp'], alert['message']))
        print("="*60)
    
    def show_stats(self):
        print("\n" + "="*60)
        cprint(" STATISTICS", Colors.PURPLE, bold=True)
        print("="*60)
        
        if self.network_monitor:
            stats = self.network_monitor.get_stats()
            cprint("\n[Network Monitor]", Colors.CYAN)
            print(f"  Packets: {stats['packets']}")
            print(f"  Alerts: {stats['alerts']}")
            print(f"  Threats: {stats['threats']}")
        
        if self.system_monitor:
            cprint("\n[System Monitor]", Colors.CYAN)
            print(f"  Alerts: {len(self.system_monitor.get_alerts())}")
        
        if self.web_firewall:
            cprint("\n[Web Firewall]", Colors.CYAN)
            print(f"  Requests: {self.web_firewall.stats['requests']}")
            print(f"  Blocked: {self.web_firewall.stats['blocked']}")
        
        if self.ids:
            cprint("\n[Intrusion Detection]", Colors.CYAN)
            print(f"  Alerts: {self.ids.stats['alerts']}")
        
        print("="*60)
    
    def stop_all(self):
        cprint("[STOP] Stopping all components...", Colors.YELLOW)
        for name, component in self.components:
            try:
                component.stop()
                cprint("[+] {} stopped".format(name), Colors.GREEN)
            except:
                pass
        cprint("[+] All components stopped", Colors.GREEN)
    
    def run(self):
        print_banner()
        cprint("[*] LUMINARY SHIELD - Ultimate Defense Framework", Colors.CYAN)
        cprint("[*] Zero Trust - Real-time Protection", Colors.DIM)
        
        while self.running:
            self.show_menu()
            choice = input(f"{Colors.CYAN}[>] Select: {Colors.WHITE}").strip()
            
            if choice == '1':
                self.start_network_monitor()
            elif choice == '2':
                self.start_system_monitor()
            elif choice == '3':
                self.start_web_firewall()
            elif choice == '4':
                self.run_ids()
            elif choice == '5':
                self.show_alerts()
            elif choice == '6':
                self.show_stats()
            elif choice == '7':
                self.stop_all()
            elif choice == '8':
                self.stop_all()
                cprint("[*] Luminary Shield deactivated...", Colors.GREEN)
                break
            else:
                cprint("[-] Invalid selection", Colors.RED)

# ==================== MAIN ====================
def main():
    parser = argparse.ArgumentParser(
        description="LUMINARY SHIELD - Ultimate Defense Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 luminary_shield.py
  python3 luminary_shield.py --monitor eth0
  python3 luminary_shield.py --firewall 8080
  python3 luminary_shield.py --ids /var/log/syslog
        """
    )
    
    parser.add_argument("-i", "--interface", default="eth0", help="Network interface")
    parser.add_argument("--monitor", action="store_true", help="Network monitor only")
    parser.add_argument("--firewall", type=int, help="Start web firewall on port")
    parser.add_argument("--ids", help="Analyze log file")
    
    args = parser.parse_args()
    
    print_banner()
    
    if os.geteuid() != 0:
        cprint("[!] Root privileges required for packet capture", Colors.RED)
        sys.exit(1)
    
    shield = LuminaryShield(args.interface)
    
    if args.monitor:
        shield.start_network_monitor()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            shield.stop_all()
        sys.exit(0)
    
    if args.firewall:
        shield.web_firewall = WebFirewall(args.firewall)
        shield.web_firewall.start()
        sys.exit(0)
    
    if args.ids:
        shield.ids.analyze_log(args.ids)
        sys.exit(0)
    
    shield.run()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        cprint("\n[!] Interrupted", Colors.RED)
        sys.exit(0)
