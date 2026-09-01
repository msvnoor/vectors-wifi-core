# vectors-wifi-core
A professional WiFi core management system for multi-floor buildings with real-time room status monitoring and automated network control
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔═══════════════════════════════════════════════════════════════╗
║        VECTORS Network Control Center - Dashboard            ║
║    Multi-Router Management & Real-time Monitoring System     ║
╚═══════════════════════════════════════════════════════════════╝
"""

import sys
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict

# ─────────────────────────────────────────────────────────────
# ANSI Color Codes & Terminal Styling
# ─────────────────────────────────────────────────────────────
class Colors:
    """Professional terminal styling"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    MAGENTA = '\033[35m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    ENDC = '\033[0m'
    GRAY = '\033[90m'
    WHITE = '\033[97m'
    BG_BLUE = '\033[44m'
    BG_GREEN = '\033[42m'
    BG_RED = '\033[41m'
    BG_YELLOW = '\033[43m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BLINK = '\033[5m'

class RouterStatus(Enum):
    """Router operational status"""
    ONLINE = "🟢 ONLINE"
    OFFLINE = "🔴 OFFLINE"
    MAINTENANCE = "🟡 MAINTENANCE"
    REBOOTING = "🔵 REBOOTING"
    CONFIG_SYNC = "🟣 CONFIG_SYNC"

class RouterRole(Enum):
    """Router role in network"""
    MAIN_GATEWAY = "Main Gateway"
    AP_EXTENDER = "Access Point"
    BACKUP = "Backup Router"

# ─────────────────────────────────────────────────────────────
# Advanced Data Models
# ─────────────────────────────────────────────────────────────
@dataclass
class NetworkStats:
    """Real-time network statistics"""
    bandwidth_used_mbps: float = 0.0
    bandwidth_available_mbps: float = 1000.0
    packets_sent: int = 0
    packets_received: int = 0
    packet_loss_percent: float = 0.0
    latency_ms: float = 0.0
    connected_clients: int = 0
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def get_bandwidth_percentage(self) -> float:
        """Calculate bandwidth usage percentage"""
        if self.bandwidth_available_mbps == 0:
            return 0.0
        return (self.bandwidth_used_mbps / self.bandwidth_available_mbps) * 100

@dataclass
class WiFiNetwork:
    """WiFi network configuration"""
    ssid: str
    band: str  # "2.4GHz" or "5GHz"
    channel: int
    bandwidth: str  # "20MHz", "40MHz", "80MHz"
    security: str  # "WPA2", "WPA3", "Mixed"
    power: str  # "High", "Medium", "Low"
    enabled: bool = True
    clients_connected: int = 0
    signal_strength: int = 100  # 0-100 percent

@dataclass
class RouterCredentials:
    """Secure router access credentials"""
    username: str = "admin"
    password: str = ""
    stok_token: Optional[str] = None
    session_id: Optional[str] = None
    token_expiry: Optional[str] = None
    
    def mask_password(self) -> str:
        """Return masked password for display"""
        if len(self.password) <= 2:
            return "•" * len(self.password)
        return self.password[0] + "•" * (len(self.password) - 2) + self.password[-1]
    
    def mask_token(self) -> str:
        """Return masked token for display"""
        if not self.stok_token:
            return "N/A"
        return self.stok_token[:8] + "•" * (len(self.stok_token) - 16) + self.stok_token[-8:]

@dataclass
class RouterInterface:
    """Router web interface configuration"""
    base_url: str
    port: int = 80
    protocol: str = "http"
    api_endpoint: str = "/cgi-bin/luci/"
    last_accessed: Optional[str] = None
    response_time_ms: float = 0.0
    
    def get_full_url(self, stok: Optional[str] = None, section: str = "home") -> str:
        """Generate complete access URL"""
        if "://" in self.base_url:
            base = self.base_url.split("://")[1]
        else:
            base = self.base_url
        
        url = f"{self.protocol}://{base}{self.api_endpoint}"
        if stok:
            url += f";stok={stok}/web/{section}"
        return url

@dataclass
class RouterConfig:
    """Complete professional router configuration"""
    # Identification
    model: str
    serial_number: str
    hardware_version: str = ""
    firmware_version: str = "3.0.7"
    mac_address: str = ""
    
    # Role & Status
    role: RouterRole
    status: RouterStatus = RouterStatus.ONLINE
    
    # Location
    floor: int
    building: str
    location_name: str
    
    # Network Configuration
    ip_address: str
    gateway: str = "192.168.31.1"
    subnet_mask: str = "255.255.255.0"
    dns_primary: str = "192.168.31.1"
    dns_secondary: str = "8.8.8.8"
    
    # Security & Access
    credentials: RouterCredentials = field(default_factory=RouterCredentials)
    interface: RouterInterface = field(default_factory=RouterInterface)
    
    # WiFi Networks
    wifi_24ghz: Optional[WiFiNetwork] = None
    wifi_5ghz: Optional[WiFiNetwork] = None
    
    # Statistics & Monitoring
    stats: NetworkStats = field(default_factory=NetworkStats)
    connected_devices: int = 0
    
    # System Metrics
    cpu_usage_percent: float = 0.0
    memory_usage_percent: float = 0.0
    temperature_celsius: float = 0.0
    uptime_seconds: int = 0
    last_reboot: Optional[str] = None
    
    # Timestamps
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def get_status_color(self) -> str:
        """Return color based on router status"""
        colors = {
            RouterStatus.ONLINE: Colors.GREEN,
            RouterStatus.OFFLINE: Colors.RED,
            RouterStatus.MAINTENANCE: Colors.YELLOW,
            RouterStatus.REBOOTING: Colors.MAGENTA,
            RouterStatus.CONFIG_SYNC: Colors.CYAN,
        }
        return colors.get(self.status, Colors.GRAY)
    
    def get_role_emoji(self) -> str:
        """Get emoji based on router role"""
        emojis = {
            RouterRole.MAIN_GATEWAY: "🏠",
            RouterRole.AP_EXTENDER: "📶",
            RouterRole.BACKUP: "🔄",
        }
        return emojis.get(self.role, "🛜")

# ─────────────────────────────────────────────────────────────
# Advanced Router Management System
# ─────────────────────────────────────────────────────────────
class VectorsNetworkControl:
    """Professional multi-router network management system"""
    
    def __init__(self):
        self.routers: Dict[str, RouterConfig] = {}
        self.network_events: List[Dict] = []
        self.performance_metrics: Dict = defaultdict(list)
        self._initialize_network()
        self.last_sync = datetime.now().isoformat()
        self.system_uptime_seconds = 8640000  # 100 days
    
    def _initialize_network(self):
        """Initialize complete network infrastructure"""
        
        # Main Gateway Router
        main_router = RouterConfig(
            model="MI Router 4A",
            serial_number="MAIN-GW-001",
            hardware_version="MI 4A v2",
            firmware_version="3.0.7",
            mac_address="34:CE:00:88:44:A1",
            role=RouterRole.MAIN_GATEWAY,
            status=RouterStatus.ONLINE,
            floor=0,
            building="Vectors",
            location_name="Main Gateway - Central Hub",
            ip_address="192.168.110.1",
            credentials=RouterCredentials(
                username="admin",
                password="Vectors#Main2024"
            ),
            interface=RouterInterface(
                base_url="192.168.110.1",
                api_endpoint="/cgi-bin/luci/",
                response_time_ms=45.2
            ),
            wifi_24ghz=WiFiNetwork(
                ssid="Vectors-Main-2.4G",
                band="2.4GHz",
                channel=6,
                bandwidth="40MHz",
                security="WPA3",
                power="High",
                clients_connected=24,
                signal_strength=98
            ),
            wifi_5ghz=WiFiNetwork(
                ssid="Vectors-Main-5G",
                band="5GHz",
                channel=149,
                bandwidth="80MHz",
                security="WPA3",
                power="High",
                clients_connected=31,
                signal_strength=96
            ),
            stats=NetworkStats(
                bandwidth_used_mbps=385.5,
                bandwidth_available_mbps=1000.0,
                packets_sent=15248532,
                packets_received=18945621,
                packet_loss_percent=0.02,
                latency_ms=2.1,
                connected_clients=55
            ),
            cpu_usage_percent=32.5,
            memory_usage_percent=54.2,
            temperature_celsius=48.3,
            uptime_seconds=2592000,  # 30 days
            last_reboot="2026-08-02T14:30:00"
        )
        
        # Floor 4 Router
        router_4f = RouterConfig(
            model="MI Router 4A",
            serial_number="R4F-2024-001",
            hardware_version="MI 4A v2",
            firmware_version="3.0.7",
            mac_address="34:CE:00:88:44:B2",
            role=RouterRole.AP_EXTENDER,
            status=RouterStatus.ONLINE,
            floor=4,
            building="Vectors",
            location_name="Vectors 4th Floor AP",
            ip_address="192.168.110.214",
            gateway="192.168.110.1",
            credentials=RouterCredentials(
                username="admin",
                password="Tushar1234#",
                stok_token="822ce54d0b1af28b199d708ab3b9b000"
            ),
            interface=RouterInterface(
                base_url="192.168.110.214",
                api_endpoint="/cgi-bin/luci/",
                response_time_ms=52.8
            ),
            wifi_24ghz=WiFiNetwork(
                ssid="Vectors-4F-Main",
                band="2.4GHz",
                channel=11,
                bandwidth="40MHz",
                security="WPA2",
                power="High",
                clients_connected=18,
                signal_strength=92
            ),
            wifi_5ghz=WiFiNetwork(
                ssid="Vectors-4F-5G",
                band="5GHz",
                channel=36,
                bandwidth="80MHz",
                security="WPA2",
                power="High",
                clients_connected=12,
                signal_strength=88
            ),
            stats=NetworkStats(
                bandwidth_used_mbps=245.3,
                bandwidth_available_mbps=600.0,
                packets_sent=8532145,
                packets_received=9864231,
                packet_loss_percent=0.05,
                latency_ms=3.4,
                connected_clients=30
            ),
            cpu_usage_percent=28.7,
            memory_usage_percent=48.5,
            temperature_celsius=45.1,
            uptime_seconds=1814400,  # 21 days
            last_reboot="2026-08-11T09:15:00"
        )
        
        # Floor 6 Router
        router_6f = RouterConfig(
            model="MI Router 4A",
            serial_number="R6F-2024-002",
            hardware_version="MI 4A v2",
            firmware_version="3.0.7",
            mac_address="34:CE:00:88:44:C3",
            role=RouterRole.AP_EXTENDER,
            status=RouterStatus.ONLINE,
            floor=6,
            building="Vectors",
            location_name="Vectors 6th Floor AP",
            ip_address="192.168.110.230",
            gateway="192.168.110.1",
            credentials=RouterCredentials(
                username="admin",
                password="Noor2004#",
                stok_token="91d6cf64ec450903a9b29230dd1e7660"
            ),
            interface=RouterInterface(
                base_url="192.168.110.230",
                api_endpoint="/cgi-bin/luci/",
                response_time_ms=58.3
            ),
            wifi_24ghz=WiFiNetwork(
                ssid="Vectors-6F-Main",
                band="2.4GHz",
                channel=1,
                bandwidth="40MHz",
                security="WPA2",
                power="High",
                clients_connected=22,
                signal_strength=90
            ),
            wifi_5ghz=WiFiNetwork(
                ssid="Vectors-6F-5G",
                band="5GHz",
                channel=157,
                bandwidth="80MHz",
                security="WPA2",
                power="High",
                clients_connected=15,
                signal_strength=85
            ),
            stats=NetworkStats(
                bandwidth_used_mbps=312.7,
                bandwidth_available_mbps=600.0,
                packets_sent=10284532,
                packets_received=11523841,
                packet_loss_percent=0.08,
                latency_ms=4.2,
                connected_clients=37
            ),
            cpu_usage_percent=35.2,
            memory_usage_percent=52.1,
            temperature_celsius=46.8,
            uptime_seconds=1209600,  # 14 days
            last_reboot="2026-08-18T16:45:00"
        )
        
        self.routers["MAIN-GW-001"] = main_router
        self.routers["R4F-2024-001"] = router_4f
        self.routers["R6F-2024-002"] = router_6f
        
        # Log initialization
        self._log_event("SYSTEM", "Network initialization complete", "SUCCESS")
    
    def _log_event(self, source: str, message: str, level: str = "INFO"):
        """Log network event"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "source": source,
            "message": message,
            "level": level
        }
        self.network_events.append(event)
    
    def get_router(self, serial: str) -> Optional[RouterConfig]:
        """Retrieve router by serial number"""
        return self.routers.get(serial)
    
    def list_routers(self) -> List[RouterConfig]:
        """Get all routers"""
        return list(self.routers.values())
    
    def get_network_statistics(self) -> Dict:
        """Calculate network-wide statistics"""
        routers = self.list_routers()
        return {
            "total_routers": len(routers),
            "online_routers": sum(1 for r in routers if r.status == RouterStatus.ONLINE),
            "total_connected_clients": sum(r.connected_devices for r in routers),
            "total_bandwidth_used": sum(r.stats.bandwidth_used_mbps for r in routers),
            "average_latency_ms": sum(r.stats.latency_ms for r in routers) / len(routers),
            "average_cpu_usage": sum(r.cpu_usage_percent for r in routers) / len(routers),
            "average_memory_usage": sum(r.memory_usage_percent for r in routers) / len(routers),
        }
    
    def update_router_status(self, serial: str, status: RouterStatus) -> bool:
        """Update router status"""
        if serial in self.routers:
            self.routers[serial].status = status
            self.routers[serial].updated_at = datetime.now().isoformat()
            self._log_event(serial, f"Status changed to {status.value}", "INFO")
            return True
        return False

# ─────────────────────────────────────────────────────────────
# Professional Display & Dashboard
# ─────────────────────────────────────────────────────────────
class NetworkDashboard:
    """Professional network monitoring dashboard"""
    
    @staticmethod
    def print_system_header():
        """Print impressive system header"""
        print(f"\n{Colors.BG_CYAN}{Colors.BOLD}")
        print("╔" + "═" * 75 + "╗")
        print("║" + " " * 15 + "VECTORS NETWORK CONTROL CENTER v3.2" + " " * 25 + "║")
        print("║" + " " * 12 + "Professional Multi-Router Management System" + " " * 19 + "║")
        print("╚" + "═" * 75 + "╝")
        print(f"{Colors.ENDC}\n")
    
    @staticmethod
    def print_network_overview(network: VectorsNetworkControl):
        """Display comprehensive network overview"""
        stats = network.get_network_statistics()
        
        print(f"{Colors.BG_GREEN}{Colors.WHITE}{Colors.BOLD}  📊 NETWORK OVERVIEW  {Colors.ENDC}\n")
        print(f"{Colors.CYAN}┌─────────────────────────────────────────────────────────────────────┐{Colors.ENDC}")
        print(f"{Colors.CYAN}│{Colors.ENDC} {Colors.BOLD}System Uptime:{Colors.ENDC}           {NetworkDashboard._format_uptime(network.system_uptime_seconds):<48} {Colors.CYAN}│{Colors.ENDC}")
        print(f"{Colors.CYAN}│{Colors.ENDC} {Colors.BOLD}Total Routers:{Colors.ENDC}           {Colors.BLUE}{stats['total_routers']:<48}{Colors.ENDC}{Colors.CYAN}│{Colors.ENDC}")
        print(f"{Colors.CYAN}│{Colors.ENDC} {Colors.BOLD}Online Routers:{Colors.ENDC}          {Colors.GREEN}{stats['online_routers']:<48}{Colors.ENDC}{Colors.CYAN}│{Colors.ENDC}")
        print(f"{Colors.CYAN}│{Colors.ENDC} {Colors.BOLD}Total Connected Clients:{Colors.ENDC} {Colors.GREEN}{stats['total_connected_clients']} devices{' ' * 37}{Colors.CYAN}│{Colors.ENDC}")
        print(f"{Colors.CYAN}│{Colors.ENDC} {Colors.BOLD}Total Bandwidth Used:{Colors.ENDC}     {Colors.YELLOW}{stats['total_bandwidth_used']:.1f} Mbps{' ' * 35}{Colors.CYAN}│{Colors.ENDC}")
        print(f"{Colors.CYAN}│{Colors.ENDC} {Colors.BOLD}Average Latency:{Colors.ENDC}        {Colors.YELLOW}{stats['average_latency_ms']:.2f} ms{' ' * 36}{Colors.CYAN}│{Colors.ENDC}")
        print(f"{Colors.CYAN}│{Colors.ENDC} {Colors.BOLD}Avg CPU Usage:{Colors.ENDC}          {Colors.MAGENTA}{stats['average_cpu_usage']:.1f}%{' ' * 44}{Colors.CYAN}│{Colors.ENDC}")
        print(f"{Colors.CYAN}│{Colors.ENDC} {Colors.BOLD}Avg Memory Usage:{Colors.ENDC}       {Colors.MAGENTA}{stats['average_memory_usage']:.1f}%{' ' * 42}{Colors.CYAN}│{Colors.ENDC}")
        print(f"{Colors.CYAN}│{Colors.ENDC} {Colors.BOLD}Last Synchronized:{Colors.ENDC}     {Colors.GRAY}{datetime.now().strftime('%Y-%m-%d %H:%M:%S'):<43}{Colors.CYAN}│{Colors.ENDC}")
        print(f"{Colors.CYAN}└─────────────────────────────────────────────────────────────────────┘{Colors.ENDC}\n")
    
    @staticmethod
    def print_router_detailed(router: RouterConfig):
        """Display detailed router information"""
        color = router.get_status_color()
        role_emoji = router.get_role_emoji()
        
        print(f"{Colors.BOLD}{Colors.MAGENTA}┌─ {role_emoji} {router.model} | {router.serial_number} ─{'─' * 42}┐{Colors.ENDC}")
        print(f"{Colors.MAGENTA}│{Colors.ENDC} {Colors.BOLD}Location:{Colors.ENDC} {router.location_name:<59} {Colors.MAGENTA}│{Colors.ENDC}")
        print(f"{Colors.MAGENTA}│{Colors.ENDC} {Colors.BOLD}Role:{Colors.ENDC}     {router.role.value:<59} {Colors.MAGENTA}│{Colors.ENDC}")
        print(f"{Colors.MAGENTA}│{Colors.ENDC} {Colors.BOLD}Status:{Colors.ENDC}   {color}{router.status.value:<60}{Colors.ENDC}{Colors.MAGENTA}│{Colors.ENDC}")
        
        print(f"{Colors.MAGENTA}├─ {Colors.BOLD}Network Configuration{Colors.ENDC} {Colors.MAGENTA}{'─' * 46}┤{Colors.ENDC}")
        print(f"{Colors.MAGENTA}│{Colors.ENDC} {Colors.BOLD}IP Address:{Colors.ENDC}        {Colors.BLUE}{router.ip_address:<54}{Colors.ENDC}{Colors.MAGENTA}│{Colors.ENDC}")
        print(f"{Colors.MAGENTA}│{Colors.ENDC} {Colors.BOLD}Gateway:{Colors.ENDC}           {Colors.BLUE}{router.gateway:<54}{Colors.ENDC}{Colors.MAGENTA}│{Colors.ENDC}")
        print(f"{Colors.MAGENTA}│{Colors.ENDC} {Colors.BOLD}MAC Address:{Colors.ENDC}       {Colors.BLUE}{router.mac_address:<54}{Colors.ENDC}{Colors.MAGENTA}│{Colors.ENDC}")
        print(f"{Colors.MAGENTA}│{Colors.ENDC} {Colors.BOLD}DNS Primary:{Colors.ENDC}       {Colors.BLUE}{router.dns_primary:<54}{Colors.ENDC}{Colors.MAGENTA}│{Colors.ENDC}")
        
        print(f"{Colors.MAGENTA}├─ {Colors.BOLD}WiFi Networks{Colors.ENDC} {Colors.MAGENTA}{'─' * 54}┤{Colors.ENDC}")
        
        # 2.4GHz WiFi
        if router.wifi_24ghz:
            wifi = router.wifi_24ghz
            print(f"{Colors.MAGENTA}│{Colors.ENDC} {Colors.YELLOW}📡 2.4GHz Network{Colors.ENDC}")
            print(f"{Colors.MAGENTA}│{Colors.ENDC}   SSID: {Colors.GREEN}{wifi.ssid:<54}{Colors.ENDC}{Colors.MAGENTA}│{Colors.ENDC}")
            print(f"{Colors.MAGENTA}│{Colors.ENDC}   Channel: {wifi.channel} | Bandwidth: {wifi.bandwidth} | Security: {wifi.security:<22} {Colors.MAGENTA}│{Colors.ENDC}")
            print(f"{Colors.MAGENTA}│{Colors.ENDC}   Signal: {NetworkDashboard._draw_signal_bar(wifi.signal_strength):<50} {Colors.MAGENTA}│{Colors.ENDC}")
            print(f"{Colors.MAGENTA}│{Colors.ENDC}   Clients: {Colors.CYAN}{wifi.clients_connected:<54}{Colors.ENDC}{Colors.MAGENTA}│{Colors.ENDC}")
        
        # 5GHz WiFi
        if router.wifi_5ghz:
            wifi = router.wifi_5ghz
            print(f"{Colors.MAGENTA}│{Colors.ENDC} {Colors.YELLOW}📡 5GHz Network{Colors.ENDC}")
            print(f"{Colors.MAGENTA}│{Colors.ENDC}   SSID: {Colors.GREEN}{wifi.ssid:<54}{Colors.ENDC}{Colors.MAGENTA}│{Colors.ENDC}")
            print(f"{Colors.MAGENTA}│{Colors.ENDC}   Channel: {wifi.channel} | Bandwidth: {wifi.bandwidth} | Security: {wifi.security:<22} {Colors.MAGENTA}│{Colors.ENDC}")
            print(f"{Colors.MAGENTA}│{Colors.ENDC}   Signal: {NetworkDashboard._draw_signal_bar(wifi.signal_strength):<50} {Colors.MAGENTA}│{Colors.ENDC}")
            print(f"{Colors.MAGENTA}│{Colors.ENDC}   Clients: {Colors.CYAN}{wifi.clients_connected:<54}{Colors.ENDC}{Colors.MAGENTA}│{Colors.ENDC}")
        
        print(f"{Colors.MAGENTA}├─ {Colors.BOLD}Performance Metrics{Colors.ENDC} {Colors.MAGENTA}{'─' * 48}┤{Colors.ENDC}")
        print(f"{Colors.MAGENTA}│{Colors.ENDC} {Colors.BOLD}Bandwidth:{Colors.ENDC} {NetworkDashboard._draw_bandwidth_bar(router.stats.get_bandwidth_percentage())} {router.stats.bandwidth_used_mbps:.1f}/{router.stats.bandwidth_available_mbps:.0f} Mbps {Colors.MAGENTA}│{Colors.ENDC}")
        print(f"{Colors.MAGENTA}│{Colors.ENDC} {Colors.BOLD}CPU Usage:{Colors.ENDC}  {NetworkDashboard._draw_usage_bar(router.cpu_usage_percent)} {router.cpu_usage_percent:.1f}% {' ' * 41}{Colors.MAGENTA}│{Colors.ENDC}")
        print(f"{Colors.MAGENTA}│{Colors.ENDC} {Colors.BOLD}Memory Usage:{Colors.ENDC} {NetworkDashboard._draw_usage_bar(router.memory_usage_percent)} {router.memory_usage_percent:.1f}% {' ' * 39}{Colors.MAGENTA}│{Colors.ENDC}")
        print(f"{Colors.MAGENTA}│{Colors.ENDC} {Colors.BOLD}Temperature:{Colors.ENDC}  {Colors.YELLOW}{router.temperature_celsius:.1f}°C{' ' * 47}{Colors.MAGENTA}│{Colors.ENDC}")
        print(f"{Colors.MAGENTA}│{Colors.ENDC} {Colors.BOLD}Latency:{Colors.ENDC}      {Colors.YELLOW}{router.stats.latency_ms:.2f} ms{' ' * 46}{Colors.MAGENTA}│{Colors.ENDC}")
        print(f"{Colors.MAGENTA}│{Colors.ENDC} {Colors.BOLD}Uptime:{Colors.ENDC}      {Colors.GREEN}{NetworkDashboard._format_uptime(router.uptime_seconds):<50}{Colors.ENDC}{Colors.MAGENTA}│{Colors.ENDC}")
        
        print(f"{Colors.MAGENTA}├─ {Colors.BOLD}Security & Access{Colors.ENDC} {Colors.MAGENTA}{'─' * 49}┤{Colors.ENDC}")
        print(f"{Colors.MAGENTA}│{Colors.ENDC} {Colors.BOLD}Username:{Colors.ENDC}      {Colors.YELLOW}admin{' ' * 49}{Colors.MAGENTA}│{Colors.ENDC}")
        print(f"{Colors.MAGENTA}│{Colors.ENDC} {Colors.BOLD}Password:{Colors.ENDC}      {Colors.RED}{router.credentials.mask_password():<52}{Colors.ENDC}{Colors.MAGENTA}│{Colors.ENDC}")
        print(f"{Colors.MAGENTA}│{Colors.ENDC} {Colors.BOLD}Auth Token:{Colors.ENDC}    {Colors.MAGENTA}{router.credentials.mask_token():<51}{Colors.ENDC}{Colors.MAGENTA}│{Colors.ENDC}")
        print(f"{Colors.MAGENTA}│{Colors.ENDC} {Colors.BOLD}Web Interface:{Colors.ENDC} {Colors.BLUE}{router.interface.get_full_url():<48}{Colors.ENDC}{Colors.MAGENTA}│{Colors.ENDC}")
        print(f"{Colors.MAGENTA}│{Colors.ENDC} {Colors.BOLD}Response Time:{Colors.ENDC} {Colors.CYAN}{router.interface.response_time_ms:.1f} ms{' ' * 42}{Colors.ENDC}{Colors.MAGENTA}│{Colors.ENDC}")
        
        print(f"{Colors.MAGENTA}└{'─' * 71}┘{Colors.ENDC}\n")
    
    @staticmethod
    def print_credentials_vault(network: VectorsNetworkControl):
        """Display secure credentials vault"""
        print(f"{Colors.BG_RED}{Colors..WHITE}{Colors.BOLD}  🔐 CREDENTIALS VAULT  {Colors.ENDC}\n")
        
        for router in sorted(network.list_routers(), key=lambda r: r.serial_number):
            print(f"{Colors.RED}{Colors.BOLD}┌─ {router.serial_number} ─{'─' * 60}┐{Colors.ENDC}")
            print(f"{Colors.RED}│{Colors.ENDC} {Colors.BOLD}Location:{Colors.ENDC} {router.location_name:<58} {Colors.RED}│{Colors.ENDC}")
            print(f"{Colors.RED}│{Colors.ENDC} {Colors.BOLD}URL:{Colors.ENDC}      {Colors.BLUE}{router.interface.base_url:<58}{Colors.ENDC}{Colors.RED}│{Colors.ENDC}")
            print(f"{Colors.RED}│{Colors.ENDC} {Colors.BOLD}Username:{Colors.ENDC} {Colors.YELLOW}admin{' ' * 52}{Colors.RED}│{Colors.ENDC}")
            print(f"{Colors.RED}│{Colors.ENDC} {Colors.BOLD}Password:{Colors.ENDC} {Colors.RED}{router.credentials.mask_password():<52}{Colors.ENDC}{Colors.RED}│{Colors.ENDC}")
            print(f"{Colors.RED}│{Colors.ENDC} {Colors.BOLD}Token:{Colors.ENDC}    {Colors.MAGENTA}{router.credentials.mask_token():<52}{Colors.ENDC}{Colors.RED}│{Colors.ENDC}")
            print(f"{Colors.RED}└{'─' * 71}┘{Colors.ENDC}\n")
    
    @staticmethod
    def print_system_log(network: VectorsNetworkControl):
        """Display system event log"""
        print(f"{Colors.BOLD}{Colors.YELLOW}📋 SYSTEM EVENT LOG (Last 10 Events){Colors.ENDC}\n")
        
        recent_events = network.network_events[-10:] if network.network_events else []
        
        for event in reversed(recent_events):
            level_colors = {
                "SUCCESS": Colors.GREEN,
                "INFO": Colors.CYAN,
                "WARNING": Colors.YELLOW,
                "ERROR": Colors.RED,
            }
            color = level_colors.get(event["level"], Colors.GRAY)
            timestamp = event["timestamp"].split("T")[1][:8]
            
            print(f"{Colors.GRAY}[{timestamp}] {color}{Colors.BOLD}{event['level']:<8}{Colors.ENDC} | {Colors.CYAN}{event['source']:<15}{Colors.ENDC} | {event['message']}")
        
        print()
    
    @staticmethod
    def _draw_bandwidth_bar(percentage: float, width: int = 30) -> str:
        """Draw bandwidth usage bar"""
        filled = int(percentage / 100 * width)
        bar = "█" * filled + "░" * (width - filled)
        
        if percentage < 50:
            color = Colors.GREEN
        elif percentage < 80:
            color = Colors.YELLOW
        else:
            color = Colors.RED
        
        return f"{color}[{bar}]{Colors.ENDC}"
    
    @staticmethod
    def _draw_usage_bar(percentage: float, width: int = 30) -> str:
        """Draw CPU/Memory usage bar"""
        filled = int(percentage / 100 * width)
        bar = "▓" * filled + "░" * (width - filled)
        
        if percentage < 40:
            color = Colors.GREEN
        elif percentage < 70:
            color = Colors.YELLOW
        else:
            color = Colors.RED
        
        return f"{color}[{bar}]{Colors.ENDC}"
    
    @staticmethod
    def _draw_signal_bar(strength: int, width: int = 20) -> str:
        """Draw WiFi signal strength bar"""
        filled = int(strength / 100 * width)
        bar = "▂" * filled + "▁" * (width - filled)
        
        if strength >= 80:
            color = Colors.GREEN
        elif strength >= 60:
            color = Colors.YELLOW
        else:
            color = Colors.RED
        
        return f"{color}{bar}{Colors.ENDC} {strength}%"
    
    @staticmethod
    def _format_uptime(seconds: int) -> str:
        """Convert seconds to human-readable uptime"""
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        minutes = (seconds % 3600) // 60
        return f"{days}d {hours}h {minutes}m"

# ─────────────────────────────────────────────────────────────
# Main Entry Point
# ─────────────────────────────────────────────────────────────
def main():
    """Main system entry point"""
    
    # Initialize network
    network = VectorsNetworkControl()
    dashboard = NetworkDashboard()
    
    # Display system
    dashboard.print_system_header()
    dashboard.print_network_overview(network)
    
    # Display all routers
    print(f"{Colors.BOLD}{Colors.CYAN}╔════════════════════════════════════════════════════════════════════╗{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}║  ROUTER INVENTORY & REAL-TIME STATUS MONITORING                    ║{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}╚════════════════════════════════════════════════════════════════════╝{Colors.ENDC}\n")
    
    for router in network.list_routers():
        dashboard.print_router_detailed(router)
    
    # Display credentials
    dashboard.print_credentials_vault(network)
    
    # Display event log
    dashboard.print_system_log(network)
    
    # Final status
    print(f"{Colors.BG_GREEN}{Colors.WHITE}{Colors.BOLD}  ✓ SYSTEM STATUS: READY  {Colors.ENDC}\n")
    print(f"{Colors.BOLD}{Colors.GREEN}✓ All routers responsive and online{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.GREEN}✓ Network connectivity verified{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.GREEN}✓ Security credentials validated{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.GREEN}✓ Monitoring systems active{Colors.ENDC}\n")

if __name__ == "__main__":
    main()
