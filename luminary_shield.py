#!/usr/bin/env python3
"""
LUMINARY SHIELD v2.0 - Ultimate Defense & Detection Framework
APT Grade | Zero Trust | Real-time Monitoring | Military Grade
Advanced Security Defense - Threat Detection - Automated Response

Author: F1REW0LF
License: MIT - For authorized security testing only
Version: 2.0.0
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
import secrets
import tempfile
import shutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union, Set
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse
import ipaddress
import logging
from pathlib import Path

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

try:
    from scapy.all import *
    from scapy.layers.inet import IP, TCP, UDP, ICMP
    from scapy.layers.l2 import ARP, Ether
    from scapy.layers.dns import DNS, DNSQR, DNSRR
    from scapy.layers.http import HTTP, HTTPRequest
    from scapy.layers.ssl import TLS, TLSClientHello, TLSServerHello
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
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    import yara
    YARA_AVAILABLE = True
except ImportError:
    YARA_AVAILABLE = False

VERSION = "2.0.0"
AUTHOR = "F1REW0LF"
LICENSE = "MIT"

# ============================[ COLORS ]================================
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
    DARK_RED = '\033[31m'
    ORANGE = '\033[38;5;208m'
    PINK = '\033[95m'

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
                                                   
{Colors.NEON}{Colors.BOLD}          ULTIMATE DEFENSE & DETECTION FRAMEWORK v2.0{Colors.WHITE}
{Colors.RED}{Colors.BOLD}    APT Grade | Zero Trust | Real-time Monitoring | Military Grade{Colors.WHITE}
{Colors.CYAN}    Advanced Threat Detection | Automated Response | Zero Trace{Colors.WHITE}
{Colors.YELLOW}    Author: {AUTHOR} | {LICENSE}{Colors.WHITE}
"""
    print(banner)
    print("=" * 80)

# ============================[ DATA CLASSES ]================================
@dataclass
class SecurityAlert:
    timestamp: str
    severity: str
    source: str
    message: str
    details: Dict
    mitigated: bool = False
    auto_response: bool = False

@dataclass
class SecurityStats:
    total_alerts: int = 0
    critical_alerts: int = 0
    high_alerts: int = 0
    medium_alerts: int = 0
    low_alerts: int = 0
    mitigated_alerts: int = 0
    auto_responses: int = 0
    blocked_ips: int = 0
    blocked_ports: int = 0
    system_uptime: float = 0

# ============================[ ADVANCED THREAT DATABASE ]================================
class AdvancedThreatDatabase:
    """Comprehensive threat intelligence database"""
    
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
        8443: 'HTTPS-Alt - Web Attack',
        9200: 'Elasticsearch - Exploit',
        9300: 'Elasticsearch - Exploit',
        27017: 'MongoDB - Exploit'
    }
    
    MALICIOUS_PATTERNS = [
        # SQL Injection
        r'(\%27)|(\')|(\-\-)|(\%23)|(#)',
        r'((\%3D)|(=))[^\n]*((\%27)|(\')|(\-\-)|(\%3B)|(;))',
        r'UNION.*SELECT.*FROM',
        r'INSERT.*INTO.*VALUES',
        r'DELETE.*FROM.*WHERE',
        r'DROP.*TABLE',
        # XSS
        r'((\%3C)|<)((\%2F)|/)*[a-z0-9\%]+((\%3E)|>)',
        r'<script.*?>.*?</script>',
        r'javascript:',
        r'onerror=',
        r'onload=',
        r'<iframe.*?>',
        # Command Injection
        r';.*?(\||\&|\;)',
        r'\|\|.*?(\||\&|\;)',
        r'`.*?`',
        r'\$\(.*?\)',
        r'\$\{.*?\}',
        # Path Traversal
        r'\.\./',
        r'\.\.\\',
        r'\.\.\%2f',
        r'\.\.\%5c',
        # File Inclusion
        r'php://',
        r'file://',
        r'http://.*?\.(php|txt|cfg|conf|ini)',
        r'zip://',
        r'phar://',
        # RCE
        r'base64_decode',
        r'eval\(',
        r'system\(',
        r'exec\(',
        r'passthru\(',
        r'shell_exec\(',
        # Data Exfiltration
        r'aws_access_key',
        r'aws_secret_key',
        r'api_key',
        r'api_secret',
        r'password.*=.*',
        r'passwd.*=.*',
        r'token.*=.*'
    ]
    
    MALICIOUS_USER_AGENTS = [
        'sqlmap', 'nmap', 'nikto', 'w3af', 'wpscan', 'dirb',
        'gobuster', 'ffuf', 'wfuzz', 'arachni', 'zap', 'burp',
        'python-requests', 'curl', 'wget', 'masscan', 'zmap',
        'hydra', 'medusa', 'ncrack', 'thc-hydra', 'nessus',
        'openvas', 'metasploit', 'cobaltstrike', 'empire'
    ]
    
    MALICIOUS_DOMAINS = [
        'malware.com', 'phishing.com', 'spam.net', 'virus.org',
        'ransomware.com', 'trojan.org', 'keylogger.net', 'rootkit.com'
    ]
    
    @classmethod
    def check_ip(cls, ip: str) -> Optional[str]:
        try:
            for subnet, desc in cls.MALICIOUS_IPS.items():
                if ipaddress.ip_address(ip) in ipaddress.ip_network(subnet):
                    return desc
        except:
            pass
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
    
    @classmethod
    def check_domain(cls, domain: str) -> bool:
        for malicious in cls.MALICIOUS_DOMAINS:
            if malicious.lower() in domain.lower():
                return True
        return False

# ============================[ THREAT INTELLIGENCE ENGINE ]================================
class ThreatIntelligenceEngine:
    """Advanced threat intelligence and IoC management"""
    
    def __init__(self):
        self.iocs = {
            'ips': set(),
            'domains': set(),
            'hashes': set(),
            'urls': set()
        }
        self.threat_scores = {}
        self.lock = threading.Lock()
    
    def add_ioc(self, ioc_type: str, value: str):
        with self.lock:
            if ioc_type in self.iocs:
                self.iocs[ioc_type].add(value)
    
    def check_ioc(self, ioc_type: str, value: str) -> bool:
        with self.lock:
            if ioc_type in self.iocs:
                return value in self.iocs[ioc_type]
        return False
    
    def update_threat_score(self, key: str, increment: int = 1):
        with self.lock:
            self.threat_scores[key] = self.threat_scores.get(key, 0) + increment
    
    def get_threat_score(self, key: str) -> int:
        with self.lock:
            return self.threat_scores.get(key, 0)
    
    def get_high_risk(self, threshold: int = 10) -> List[str]:
        with self.lock:
            return [k for k, v in self.threat_scores.items() if v >= threshold]

# ============================[ NETWORK MONITOR ]================================
class AdvancedNetworkMonitor:
    """Advanced network monitoring with deep packet inspection"""
    
    def __init__(self, interface: str = 'eth0'):
        self.interface = interface
        self.running = False
        self.stop_event = threading.Event()
        self.packets = []
        self.alerts: List[SecurityAlert] = []
        self.stats = SecurityStats()
        self.lock = threading.Lock()
        self.db = AdvancedThreatDatabase()
        self.threat_intel = ThreatIntelligenceEngine()
        self.last_stats = time.time()
        self.alert_queue = queue.Queue()
        self._start_alert_processor()
    
    def _start_alert_processor(self):
        """Start alert processing thread"""
        def process_alerts():
            while self.running:
                try:
                    alert = self.alert_queue.get(timeout=1)
                    self._process_alert(alert)
                except queue.Empty:
                    continue
                except Exception as e:
                    pass
        
        thread = threading.Thread(target=process_alerts, daemon=True)
        thread.start()
    
    def _process_alert(self, alert: SecurityAlert):
        """Process and respond to alerts"""
        # Auto-mitigation for critical alerts
        if alert.severity == 'CRITICAL':
            alert.auto_response = True
            
            # Block source IP
            if 'src_ip' in alert.details:
                self._block_ip(alert.details['src_ip'])
            
            # Block destination IP
            if 'dst_ip' in alert.details:
                self._block_ip(alert.details['dst_ip'])
            
            alert.mitigated = True
        
        # High severity alerts - block ports
        elif alert.severity == 'HIGH':
            if 'dport' in alert.details:
                self._block_port(alert.details['dport'])
            if 'sport' in alert.details:
                self._block_port(alert.details['sport'])
        
        with self.lock:
            self.alerts.append(alert)
            self.stats.total_alerts += 1
            if alert.severity == 'CRITICAL':
                self.stats.critical_alerts += 1
            elif alert.severity == 'HIGH':
                self.stats.high_alerts += 1
            elif alert.severity == 'MEDIUM':
                self.stats.medium_alerts += 1
            else:
                self.stats.low_alerts += 1
            
            if alert.mitigated:
                self.stats.mitigated_alerts += 1
            if alert.auto_response:
                self.stats.auto_responses += 1
    
    def _block_ip(self, ip: str):
        """Block IP using iptables"""
        try:
            subprocess.run(['iptables', '-A', 'INPUT', '-s', ip, '-j', 'DROP'], capture_output=True)
            subprocess.run(['iptables', '-A', 'OUTPUT', '-d', ip, '-j', 'DROP'], capture_output=True)
            with self.lock:
                self.stats.blocked_ips += 1
            cprint(f"[BLOCK] IP {ip} blocked", Colors.RED)
        except:
            pass
    
    def _block_port(self, port: int):
        """Block port using iptables"""
        try:
            subprocess.run(['iptables', '-A', 'INPUT', '-p', 'tcp', '--dport', str(port), '-j', 'DROP'], capture_output=True)
            with self.lock:
                self.stats.blocked_ports += 1
            cprint(f"[BLOCK] Port {port} blocked", Colors.YELLOW)
        except:
            pass
    
    def start(self):
        cprint("[MONITOR] Starting advanced network monitoring...", Colors.BLUE)
        
        if not SCAPY_AVAILABLE:
            cprint("[-] Scapy not available", Colors.RED)
            return
        
        self.running = True
        self.stats.system_uptime = time.time()
        
        def packet_handler(pkt):
            if not self.running:
                return
            
            with self.lock:
                self.stats.total_alerts += 1
            
            self._analyze_packet(pkt)
        
        try:
            sniff(iface=self.interface, prn=packet_handler, store=0,
                  stop_filter=lambda x: self.stop_event.is_set())
        except Exception as e:
            cprint(f"[-] Sniff error: {e}", Colors.RED)
    
    def _analyze_packet(self, pkt):
        try:
            details = {}
            
            # IP Layer
            if pkt.haslayer(IP):
                ip = pkt[IP]
                src = ip.src
                dst = ip.dst
                details['src_ip'] = src
                details['dst_ip'] = dst
                
                # Check for suspicious IPs
                ip_check = self.db.check_ip(src)
                if ip_check:
                    self.alert_queue.put(SecurityAlert(
                        timestamp=datetime.now().isoformat(),
                        severity='HIGH',
                        source='Network Monitor',
                        message=f"Suspicious source IP: {src} - {ip_check}",
                        details=details
                    ))
                    self.threat_intel.update_threat_score(src, 5)
            
            # TCP Layer
            if pkt.haslayer(TCP):
                tcp = pkt[TCP]
                sport = tcp.sport
                dport = tcp.dport
                details['sport'] = sport
                details['dport'] = dport
                
                # Check for suspicious ports
                if self.db.check_port(sport):
                    self.alert_queue.put(SecurityAlert(
                        timestamp=datetime.now().isoformat(),
                        severity='MEDIUM',
                        source='Network Monitor',
                        message=f"Suspicious source port: {sport}",
                        details=details
                    ))
                
                if self.db.check_port(dport):
                    self.alert_queue.put(SecurityAlert(
                        timestamp=datetime.now().isoformat(),
                        severity='MEDIUM',
                        source='Network Monitor',
                        message=f"Suspicious destination port: {dport}",
                        details=details
                    ))
                
                # SYN flood detection
                if tcp.flags == 'S':
                    self.alert_queue.put(SecurityAlert(
                        timestamp=datetime.now().isoformat(),
                        severity='HIGH',
                        source='Network Monitor',
                        message=f"SYN packet: {src} -> {dst}:{dport}",
                        details=details
                    ))
                    self.threat_intel.update_threat_score(src, 3)
                
                # Port scan detection
                if tcp.flags == 'SA':
                    self.alert_queue.put(SecurityAlert(
                        timestamp=datetime.now().isoformat(),
                        severity='MEDIUM',
                        source='Network Monitor',
                        message=f"SYN-ACK packet: {src} -> {dst}:{dport}",
                        details=details
                    ))
            
            # UDP Layer
            if pkt.haslayer(UDP):
                udp = pkt[UDP]
                if udp.dport == 53:
                    details['dns_query'] = True
                    self.alert_queue.put(SecurityAlert(
                        timestamp=datetime.now().isoformat(),
                        severity='LOW',
                        source='Network Monitor',
                        message=f"DNS query: {src} -> {dst}",
                        details=details
                    ))
            
            # HTTP Layer
            if pkt.haslayer(HTTPRequest):
                http = pkt[HTTPRequest]
                host = http.Host.decode() if http.Host else 'unknown'
                path = http.Path.decode() if http.Path else '/'
                method = http.Method.decode() if http.Method else 'GET'
                details['host'] = host
                details['path'] = path
                details['method'] = method
                
                # Check for malicious patterns
                if self.db.check_pattern(path):
                    self.alert_queue.put(SecurityAlert(
                        timestamp=datetime.now().isoformat(),
                        severity='CRITICAL',
                        source='Network Monitor',
                        message=f"Malicious HTTP request: {method} {host}{path}",
                        details=details
                    ))
                    self.threat_intel.update_threat_score(src, 10)
                
                # Check User-Agent
                if http.User_Agent:
                    ua = http.User_Agent.decode()
                    details['user_agent'] = ua
                    if self.db.check_user_agent(ua):
                        self.alert_queue.put(SecurityAlert(
                            timestamp=datetime.now().isoformat(),
                            severity='HIGH',
                            source='Network Monitor',
                            message=f"Suspicious User-Agent: {ua}",
                            details=details
                        ))
                        self.threat_intel.update_threat_score(src, 5)
                
                # Check Host header
                if self.db.check_domain(host):
                    self.alert_queue.put(SecurityAlert(
                        timestamp=datetime.now().isoformat(),
                        severity='HIGH',
                        source='Network Monitor',
                        message=f"Suspicious domain: {host}",
                        details=details
                    ))
            
            # DNS Layer
            if pkt.haslayer(DNS) and pkt[DNS].qr == 0:
                if pkt[DNS].qd:
                    qname = pkt[DNS].qd.qname.decode('utf-8', errors='ignore')
                    details['dns_query'] = qname
                    if self.db.check_domain(qname):
                        self.alert_queue.put(SecurityAlert(
                            timestamp=datetime.now().isoformat(),
                            severity='HIGH',
                            source='Network Monitor',
                            message=f"Malicious DNS query: {qname}",
                            details=details
                        ))
        
        except Exception as e:
            pass
    
    def get_stats(self) -> SecurityStats:
        with self.lock:
            self.stats.system_uptime = time.time() - self.stats.system_uptime
            return self.stats
    
    def get_alerts(self, severity: str = None) -> List[SecurityAlert]:
        with self.lock:
            if severity:
                return [a for a in self.alerts if a.severity == severity]
            return self.alerts
    
    def stop(self):
        cprint("[MONITOR] Stopping advanced network monitoring...", Colors.YELLOW)
        self.running = False
        self.stop_event.set()
        cprint("[+] Network monitoring stopped", Colors.GREEN)

# ============================[ SYSTEM MONITOR ]================================
class AdvancedSystemMonitor:
    """Advanced system monitoring with performance analysis"""
    
    def __init__(self):
        self.running = False
        self.stop_event = threading.Event()
        self.alerts: List[SecurityAlert] = []
        self.stats = {}
        self.lock = threading.Lock()
        self.thresholds = {
            'cpu': 80,
            'memory': 80,
            'disk': 80,
            'connections': 100,
            'processes': 500
        }
    
    def start(self):
        cprint("[SYSTEM] Starting advanced system monitoring...", Colors.BLUE)
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
            details = {}
            
            # CPU
            cpu = psutil.cpu_percent(interval=0.1)
            details['cpu'] = cpu
            if cpu > self.thresholds['cpu']:
                self.alert_queue(SecurityAlert(
                    timestamp=datetime.now().isoformat(),
                    severity='HIGH',
                    source='System Monitor',
                    message=f"High CPU usage: {cpu}%",
                    details=details
                ))
            
            # Memory
            mem = psutil.virtual_memory()
            details['memory'] = mem.percent
            if mem.percent > self.thresholds['memory']:
                self.alert_queue(SecurityAlert(
                    timestamp=datetime.now().isoformat(),
                    severity='HIGH',
                    source='System Monitor',
                    message=f"High memory usage: {mem.percent}%",
                    details=details
                ))
            
            # Disk
            disk = psutil.disk_usage('/')
            details['disk'] = disk.percent
            if disk.percent > self.thresholds['disk']:
                self.alert_queue(SecurityAlert(
                    timestamp=datetime.now().isoformat(),
                    severity='MEDIUM',
                    source='System Monitor',
                    message=f"High disk usage: {disk.percent}%",
                    details=details
                ))
            
            # Network connections
            connections = psutil.net_connections()
            established = len([c for c in connections if c.status == 'ESTABLISHED'])
            details['connections'] = established
            if established > self.thresholds['connections']:
                self.alert_queue(SecurityAlert(
                    timestamp=datetime.now().isoformat(),
                    severity='MEDIUM',
                    source='System Monitor',
                    message=f"Many established connections: {established}",
                    details=details
                ))
            
            # Running processes
            processes = len(psutil.pids())
            details['processes'] = processes
            if processes > self.thresholds['processes']:
                self.alert_queue(SecurityAlert(
                    timestamp=datetime.now().isoformat(),
                    severity='LOW',
                    source='System Monitor',
                    message=f"Many running processes: {processes}",
                    details=details
                ))
            
            # Check for suspicious processes
            for proc in psutil.process_iter(['name', 'pid', 'cpu_percent']):
                try:
                    proc_name = proc.info['name'].lower()
                    suspicious_names = ['miner', 'crypto', 'xmr', 'bitcoin', 'monero']
                    for sus in suspicious_names:
                        if sus in proc_name:
                            self.alert_queue(SecurityAlert(
                                timestamp=datetime.now().isoformat(),
                                severity='CRITICAL',
                                source='System Monitor',
                                message=f"Suspicious process: {proc_name} (PID: {proc.info['pid']})",
                                details={'process': proc_name, 'pid': proc.info['pid']}
                            ))
                except:
                    pass
            
        except Exception as e:
            pass
    
    def alert_queue(self, alert: SecurityAlert):
        with self.lock:
            self.alerts.append(alert)
    
    def get_alerts(self) -> List[SecurityAlert]:
        with self.lock:
            return self.alerts
    
    def stop(self):
        cprint("[SYSTEM] Stopping system monitoring...", Colors.YELLOW)
        self.running = False
        self.stop_event.set()
        cprint("[+] System monitoring stopped", Colors.GREEN)

# ============================[ WEB APPLICATION FIREWALL ]================================
class AdvancedWebFirewall:
    """Advanced WAF with real-time protection"""
    
    def __init__(self, port: int = 8080):
        self.port = port
        self.running = False
        self.server = None
        self.db = AdvancedThreatDatabase()
        self.blocked_ips = set()
        self.blocked_user_agents = set()
        self.stats = {'requests': 0, 'blocked': 0, 'alerts': 0}
        self.alerts: List[SecurityAlert] = []
        self.lock = threading.Lock()
        self.rate_limits = {}
    
    def start(self):
        cprint("[WAF] Starting advanced web firewall on port {}...".format(self.port), Colors.BLUE)
        
        try:
            from flask import Flask, request, jsonify, abort
            
            app = Flask(__name__)
            
            @app.before_request
            def before_request():
                ip = request.remote_addr
                path = request.path
                ua = request.headers.get('User-Agent', '')
                method = request.method
                
                with self.lock:
                    self.stats['requests'] += 1
                
                # Rate limiting
                current_time = time.time()
                if ip not in self.rate_limits:
                    self.rate_limits[ip] = []
                self.rate_limits[ip] = [t for t in self.rate_limits[ip] if current_time - t < 60]
                if len(self.rate_limits[ip]) > 60:
                    self._block_request(f"Rate limit exceeded: {ip}")
                    return "Too many requests", 429
                self.rate_limits[ip].append(current_time)
                
                # Check IP
                if ip in self.blocked_ips:
                    self._block_request(f"Blocked IP: {ip}")
                    return "Access Denied", 403
                
                # Check User-Agent
                if self.db.check_user_agent(ua):
                    self.blocked_ips.add(ip)
                    self._block_request(f"Suspicious User-Agent: {ua}")
                    return "Access Denied", 403
                
                # Check URL path
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
                
                # Check request body
                if request.is_json and request.get_json():
                    data = request.get_json()
                    for key, value in data.items():
                        if self.db.check_pattern(str(value)):
                            self.blocked_ips.add(ip)
                            self._block_request(f"Malicious body: {key}={value}")
                            return "Access Denied", 403
            
            @app.route('/')
            def index():
                return """
                <h1>🛡️ LUMINARY SHIELD - Advanced Web Firewall</h1>
                <p>Protected by enterprise-grade security system</p>
                <p>Status: <span style="color:green;">ACTIVE</span></p>
                """
            
            @app.route('/status')
            def status():
                return jsonify({
                    'status': 'active',
                    'requests': self.stats['requests'],
                    'blocked': self.stats['blocked'],
                    'alerts': self.stats['alerts'],
                    'blocked_ips': len(self.blocked_ips)
                })
            
            @app.route('/admin')
            def admin():
                ip = request.remote_addr
                if ip not in self.blocked_ips:
                    return """
                    <h1>Admin Panel</h1>
                    <p>Status: Active</p>
                    <p>Requests: {}</p>
                    <p>Blocked: {}</p>
                    <p>Alerts: {}</p>
                    """.format(self.stats['requests'], self.stats['blocked'], self.stats['alerts'])
                return "Access Denied", 403
            
            self.server = app
            self.running = True
            app.run(host='0.0.0.0', port=self.port, debug=False, threaded=True)
            
        except ImportError:
            cprint("[-] Flask not installed. Install with: pip3 install flask", Colors.RED)
        except Exception as e:
            cprint(f"[-] WAF start failed: {e}", Colors.RED)
    
    def _block_request(self, reason: str):
        with self.lock:
            self.stats['blocked'] += 1
            self.stats['alerts'] += 1
            alert = SecurityAlert(
                timestamp=datetime.now().isoformat(),
                severity='HIGH',
                source='Web Firewall',
                message=reason,
                details={}
            )
            self.alerts.append(alert)
        cprint(f"[WAF] Blocked: {reason}", Colors.RED)
    
    def get_alerts(self) -> List[SecurityAlert]:
        with self.lock:
            return self.alerts
    
    def stop(self):
        cprint("[WAF] Stopping web firewall...", Colors.YELLOW)
        self.running = False
        if self.server:
            self.server.do_teardown_appcontext()
        cprint("[+] Web firewall stopped", Colors.GREEN)

# ============================[ INTRUSION DETECTION SYSTEM ]================================
class AdvancedIntrusionDetection:
    """Advanced IDS with log analysis and threat correlation"""
    
    def __init__(self):
        self.db = AdvancedThreatDatabase()
        self.threat_intel = ThreatIntelligenceEngine()
        self.alerts: List[SecurityAlert] = []
        self.stats = {'scans': 0, 'attacks': 0, 'alerts': 0}
        self.lock = threading.Lock()
        self.correlations = {}
    
    def analyze_log(self, log_file: str):
        cprint("[IDS] Analyzing log file: {}".format(log_file), Colors.BLUE)
        
        try:
            with open(log_file, 'r') as f:
                lines = f.readlines()
            
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = {executor.submit(self._analyze_line, line): line for line in lines}
                for future in as_completed(futures):
                    try:
                        future.result(timeout=5)
                    except:
                        pass
            
            cprint("[+] Log analysis complete", Colors.GREEN)
        except Exception as e:
            cprint(f"[-] Log analysis failed: {e}", Colors.RED)
    
    def _analyze_line(self, line: str):
        # Check for attack patterns
        if self.db.check_pattern(line):
            self._alert(f"Attack pattern detected", line, 'CRITICAL')
            self.threat_intel.update_threat_score('attack_detected', 10)
        
        # Check for suspicious IPs
        ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        ips = re.findall(ip_pattern, line)
        for ip in ips:
            if self.db.check_ip(ip):
                self._alert(f"Suspicious IP: {ip}", line, 'HIGH')
                self.threat_intel.update_threat_score(ip, 5)
        
        # Check for port scans
        port_pattern = r'port\s+(\d+)'
        ports = re.findall(port_pattern, line, re.IGNORECASE)
        for port in ports:
            if self.db.check_port(int(port)):
                self._alert(f"Suspicious port: {port}", line, 'MEDIUM')
                self.threat_intel.update_threat_score(f'port_{port}', 3)
        
        # Check for authentication failures
        if 'authentication failure' in line.lower() or 'failed login' in line.lower():
            self._alert("Authentication failure", line, 'HIGH')
            self.threat_intel.update_threat_score('auth_failure', 2)
        
        # Check for command injection
        command_patterns = ['cmd=', 'exec=', 'system=', 'eval=']
        for pattern in command_patterns:
            if pattern in line.lower():
                self._alert(f"Command injection attempt: {pattern}", line, 'CRITICAL')
                self.threat_intel.update_threat_score('command_injection', 10)
        
        # Correlate events
        self._correlate_events(line)
    
    def _correlate_events(self, line: str):
        """Correlate events to detect complex attacks"""
        timestamp = self._extract_timestamp(line)
        if not timestamp:
            return
        
        key = f"event_{int(time.time() / 60)}"
        
        with self.lock:
            if key not in self.correlations:
                self.correlations[key] = []
            self.correlations[key].append(line)
            
            # Check for attack patterns across multiple events
            if len(self.correlations[key]) > 5:
                attack_indicators = ['attack', 'exploit', 'exploitation', 'compromise']
                combined = ' '.join(self.correlations[key]).lower()
                for indicator in attack_indicators:
                    if indicator in combined:
                        self._alert(f"Complex attack pattern detected", combined, 'CRITICAL')
                        self.threat_intel.update_threat_score('complex_attack', 20)
                del self.correlations[key]
    
    def _extract_timestamp(self, line: str) -> Optional[str]:
        timestamp_pattern = r'\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}'
        match = re.search(timestamp_pattern, line)
        return match.group(0) if match else None
    
    def _alert(self, message: str, data: str, severity: str = 'MEDIUM'):
        with self.lock:
            alert = SecurityAlert(
                timestamp=datetime.now().isoformat(),
                severity=severity,
                source='IDS',
                message=message,
                details={'data': data[:200]}
            )
            self.alerts.append(alert)
            self.stats['alerts'] += 1
        
        color = Colors.RED if severity == 'CRITICAL' else Colors.YELLOW
        cprint(f"[IDS] {message}", color, bold=True)
    
    def get_alerts(self) -> List[SecurityAlert]:
        with self.lock:
            return self.alerts

# ============================[ MAIN FRAMEWORK ]================================
class LuminaryShieldV2:
    """Ultimate Defense & Detection Framework"""
    
    def __init__(self, interface: str = 'eth0'):
        self.interface = interface
        self.network_monitor = None
        self.system_monitor = None
        self.web_firewall = None
        self.ids = AdvancedIntrusionDetection()
        self.threat_intel = ThreatIntelligenceEngine()
        self.running = True
        self.components = []
        self.results = []
        
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        cprint("\n[!] Luminary Shield deactivating...", Colors.RED)
        self.running = False
        self.stop_all()
        sys.exit(0)
    
    def show_menu(self):
        print(f"""
{Colors.BLUE}{'='*70}{Colors.WHITE}
{Colors.BOLD}{Colors.PURPLE}LUMINARY SHIELD v{VERSION} - Ultimate Defense Framework{Colors.WHITE}
{Colors.RED}{Colors.BOLD}APT Grade | Zero Trust | Real-time Monitoring | Military Grade{Colors.WHITE}
{Colors.CYAN}Advanced Threat Detection | Automated Response | Zero Trace{Colors.WHITE}
{Colors.BLUE}{'='*70}{Colors.WHITE}
{Colors.GREEN}[1]  Network Monitor (Deep Packet Inspection)
{Colors.GREEN}[2]  System Monitor (Performance + Security)
{Colors.GREEN}[3]  Web Application Firewall (WAF)
{Colors.GREEN}[4]  Intrusion Detection System (IDS)
{Colors.GREEN}[5]  Threat Intelligence (IoC Management)
{Colors.GREEN}[6]  Show Alerts
{Colors.GREEN}[7]  Show Statistics
{Colors.GREEN}[8]  Generate Report
{Colors.RED}[9]  Stop All Components
{Colors.RED}[10] Exit
""")
    
    def start_network_monitor(self):
        if self.network_monitor and self.network_monitor.running:
            cprint("[!] Network monitor already running", Colors.YELLOW)
            return
        
        self.network_monitor = AdvancedNetworkMonitor(self.interface)
        thread = threading.Thread(target=self.network_monitor.start, daemon=True)
        thread.start()
        self.components.append(('Network Monitor', self.network_monitor))
        cprint("[+] Network monitor started", Colors.GREEN)
    
    def start_system_monitor(self):
        if self.system_monitor and self.system_monitor.running:
            cprint("[!] System monitor already running", Colors.YELLOW)
            return
        
        self.system_monitor = AdvancedSystemMonitor()
        self.system_monitor.start()
        self.components.append(('System Monitor', self.system_monitor))
        cprint("[+] System monitor started", Colors.GREEN)
    
    def start_web_firewall(self):
        if self.web_firewall and self.web_firewall.running:
            cprint("[!] Web firewall already running", Colors.YELLOW)
            return
        
        port = input("[>] Port (8080): ").strip() or "8080"
        self.web_firewall = AdvancedWebFirewall(int(port))
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
    
    def threat_intelligence(self):
        cprint("\n[THREAT] Threat Intelligence", Colors.PURPLE)
        
        print("\n1. Add IOC")
        print("2. Check IOC")
        print("3. View Threat Scores")
        print("4. View High Risk")
        
        choice = input("[>] Select: ").strip()
        
        if choice == '1':
            ioc_type = input("[>] IOC Type (ips/domains/hashes/urls): ").strip()
            value = input("[>] Value: ").strip()
            self.threat_intel.add_ioc(ioc_type, value)
            cprint("[+] IOC added", Colors.GREEN)
        
        elif choice == '2':
            ioc_type = input("[>] IOC Type: ").strip()
            value = input("[>] Value: ").strip()
            found = self.threat_intel.check_ioc(ioc_type, value)
            cprint(f"Found: {found}", Colors.GREEN if found else Colors.RED)
        
        elif choice == '3':
            cprint("[+] Threat Scores:", Colors.YELLOW)
            for key, score in self.threat_intel.threat_scores.items():
                cprint(f"  {key}: {score}", Colors.DIM)
        
        elif choice == '4':
            high_risk = self.threat_intel.get_high_risk()
            if high_risk:
                cprint("[+] High Risk Items:", Colors.RED)
                for item in high_risk:
                    cprint(f"  {item}", Colors.RED)
            else:
                cprint("[+] No high risk items", Colors.GREEN)
    
    def show_alerts(self):
        alerts = []
        
        if self.network_monitor:
            alerts.extend(self.network_monitor.get_alerts())
        if self.system_monitor:
            alerts.extend(self.system_monitor.get_alerts())
        if self.web_firewall:
            alerts.extend(self.web_firewall.get_alerts())
        alerts.extend(self.ids.get_alerts())
        
        if not alerts:
            cprint("[!] No alerts", Colors.YELLOW)
            return
        
        print("\n" + "="*70)
        cprint(" SECURITY ALERTS", Colors.RED, bold=True)
        print("="*70)
        print(f"{'Severity':<10} {'Source':<15} {'Message':<40} {'Time':<20}")
        print("-"*85)
        
        for alert in alerts[-20:]:
            color = {
                'CRITICAL': Colors.RED,
                'HIGH': Colors.YELLOW,
                'MEDIUM': Colors.ORANGE,
                'LOW': Colors.GREEN
            }.get(alert.severity, Colors.WHITE)
            
            cprint(f"{alert.severity:<10}", color, bold=True)
            print(f" {alert.source:<15} {alert.message[:38]:<40} {alert.timestamp[:19]:<20}")
        
        print("="*70)
    
    def show_stats(self):
        print("\n" + "="*70)
        cprint(" SECURITY STATISTICS", Colors.PURPLE, bold=True)
        print("="*70)
        
        if self.network_monitor:
            stats = self.network_monitor.get_stats()
            cprint("\n[Network Monitor]", Colors.CYAN)
            print(f"  Total Alerts: {stats.total_alerts}")
            print(f"  Critical: {stats.critical_alerts}")
            print(f"  High: {stats.high_alerts}")
            print(f"  Medium: {stats.medium_alerts}")
            print(f"  Low: {stats.low_alerts}")
            print(f"  Mitigated: {stats.mitigated_alerts}")
            print(f"  Auto Responses: {stats.auto_responses}")
            print(f"  Blocked IPs: {stats.blocked_ips}")
            print(f"  Blocked Ports: {stats.blocked_ports}")
            print(f"  Uptime: {stats.system_uptime:.1f}s")
        
        if self.system_monitor:
            alerts = self.system_monitor.get_alerts()
            cprint("\n[System Monitor]", Colors.CYAN)
            print(f"  Alerts: {len(alerts)}")
        
        if self.web_firewall:
            cprint("\n[Web Firewall]", Colors.CYAN)
            print(f"  Requests: {self.web_firewall.stats['requests']}")
            print(f"  Blocked: {self.web_firewall.stats['blocked']}")
            print(f"  Alerts: {self.web_firewall.stats['alerts']}")
        
        if self.ids:
            cprint("\n[Intrusion Detection]", Colors.CYAN)
            print(f"  Alerts: {self.ids.stats['alerts']}")
            print(f"  Scans: {self.ids.stats['scans']}")
        
        print("="*70)
    
    def generate_report(self):
        cprint("\n[REPORT] Generating Security Report", Colors.GREEN, bold=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"luminary_shield_report_{timestamp}.json"
        
        # Gather all alerts
        all_alerts = []
        if self.network_monitor:
            all_alerts.extend(self.network_monitor.get_alerts())
        if self.system_monitor:
            all_alerts.extend(self.system_monitor.get_alerts())
        if self.web_firewall:
            all_alerts.extend(self.web_firewall.get_alerts())
        all_alerts.extend(self.ids.get_alerts())
        
        report = {
            'version': VERSION,
            'author': AUTHOR,
            'timestamp': datetime.now().isoformat(),
            'statistics': {
                'total_alerts': len(all_alerts),
                'severity_breakdown': {}
            },
            'alerts': [a.__dict__ for a in all_alerts]
        }
        
        # Severity breakdown
        for alert in all_alerts:
            severity = alert.severity
            if severity not in report['statistics']['severity_breakdown']:
                report['statistics']['severity_breakdown'][severity] = 0
            report['statistics']['severity_breakdown'][severity] += 1
        
        # Add network stats
        if self.network_monitor:
            stats = self.network_monitor.get_stats()
            report['statistics']['network'] = {
                'blocked_ips': stats.blocked_ips,
                'blocked_ports': stats.blocked_ports,
                'auto_responses': stats.auto_responses
            }
        
        # Add threat intelligence
        report['threat_intelligence'] = {
            'total_iocs': sum(len(v) for v in self.threat_intel.iocs.values()),
            'high_risk_items': self.threat_intel.get_high_risk()
        }
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        cprint(f"[+] Report saved: {filename}", Colors.GREEN)
    
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
        cprint("[*] LUMINARY SHIELD v2.0 - Ultimate Defense Framework", Colors.CYAN)
        cprint("[*] APT Grade | Zero Trust | Real-time Monitoring | Military Grade", Colors.DIM)
        cprint("[!] This tool is for authorized security testing only", Colors.RED)
        
        while self.running:
            self.show_menu()
            choice = input(f"{Colors.CYAN}[>] Select (1-10): {Colors.WHITE}").strip()
            
            if choice == '1':
                self.start_network_monitor()
            elif choice == '2':
                self.start_system_monitor()
            elif choice == '3':
                self.start_web_firewall()
            elif choice == '4':
                self.run_ids()
            elif choice == '5':
                self.threat_intelligence()
            elif choice == '6':
                self.show_alerts()
            elif choice == '7':
                self.show_stats()
            elif choice == '8':
                self.generate_report()
            elif choice == '9':
                self.stop_all()
            elif choice == '10':
                self.stop_all()
                cprint("[*] Luminary Shield deactivated...", Colors.GREEN)
                break
            else:
                cprint("[-] Invalid selection", Colors.RED)

# ============================[ MAIN ]================================
def main():
    parser = argparse.ArgumentParser(
        description="LUMINARY SHIELD v2.0 - Ultimate Defense Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
  # Interactive Mode
  sudo python3 luminary_shield_v2.py
  
  # Network Monitor Only
  sudo python3 luminary_shield_v2.py --monitor eth0
  
  # Web Firewall Only
  sudo python3 luminary_shield_v2.py --firewall 8080
  
  # IDS Log Analysis
  sudo python3 luminary_shield_v2.py --ids /var/log/syslog
  
  # Generate Report
  sudo python3 luminary_shield_v2.py --report --output security_report
        """
    )
    
    parser.add_argument("-i", "--interface", default="eth0", help="Network interface")
    parser.add_argument("--monitor", action="store_true", help="Network monitor only")
    parser.add_argument("--firewall", type=int, help="Start web firewall on port")
    parser.add_argument("--ids", help="Analyze log file")
    parser.add_argument("--report", action="store_true", help="Generate report")
    parser.add_argument("-o", "--output", help="Output file")
    
    args = parser.parse_args()
    
    if os.geteuid() != 0:
        cprint("[!] Root privileges required for packet capture", Colors.RED)
        sys.exit(1)
    
    print_banner()
    
    shield = LuminaryShieldV2(args.interface)
    
    if args.monitor:
        shield.start_network_monitor()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            shield.stop_all()
        sys.exit(0)
    
    if args.firewall:
        shield.web_firewall = AdvancedWebFirewall(args.firewall)
        shield.web_firewall.start()
        sys.exit(0)
    
    if args.ids:
        shield.ids.analyze_log(args.ids)
        sys.exit(0)
    
    if args.report:
        shield.generate_report()
        sys.exit(0)
    
    shield.run()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        cprint("\n[!] Interrupted", Colors.RED)
        sys.exit(0)
    except Exception as e:
        cprint(f"\n[!] Error: {e}", Colors.RED)
        import traceback
        traceback.print_exc()
        sys.exit(1)
