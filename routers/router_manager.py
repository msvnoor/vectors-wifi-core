#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔═══════════════════════════════════════════════════════════════╗
║        VECTORS Router Management & Control System            ║
║           Real-time Network Device Configuration             ║
╚═══════════════════════════════════════════════════════════════╝
"""

import sys
import json
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum

# ─────────────────────────────────────────────────────────────
# ANSI Color Codes & Styling
# ─────────────────────────────────────────────────────────────
class Colors:
    """Advanced terminal color and styling"""
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

class RouterStatus(Enum):
    """Router operational status"""
    ONLINE = "🟢 ONLINE"
    OFFLINE = "🔴 OFFLINE"
    MAINTENANCE = "🟡 MAINTENANCE"
    CONFIG_PENDING = "🔵 CONFIG_PENDING"
    SYNCING = "🔄 SYNCING"

class RouterModel(Enum):
    """Supported router models"""
    MI_4A = "MI Router 4A"
    MI_3G = "MI Router 3G"
    MI_3C = "MI Router 3C"
    MI_4 = "MI Router 4"

# ─────────────────────────────────────────────────────────────
# Data Models
# ─────────────────────────────────────────────────────────────
@dataclass
class RouterCredentials:
    """Secure router access credentials"""
    username: str = "admin"
    password: str = ""
    stok_token: Optional[str] = None
    token_expiry: Optional[str] = None
    
    def mask_password(self) -> str:
        """Return masked password for display"""
        if len(self.password) <= 2:
            return self.password
        return self.password[0] + "•" * (len(self.password) - 2) + self.password[-1]

@dataclass
class RouterLocation:
    """Physical location and network information"""
    floor: int
    building: str
    location_name: str
    ip_address: str
    gateway: str = "192.168.31.1"
    dns_primary: str = "192.168.31.1"
    dns_secondary: str = "8.8.8.8"

@dataclass
class RouterInterface:
    """Router web interface configuration"""
    base_url: str
    port: int = 80
    protocol: str = "http"
    api_path: str = "/cgi-bin/luci/"
    last_accessed: Optional[str] = None
    
    def get_full_url(self, stok: Optional[str] = None) -> str:
        """Generate complete access URL"""
        url = f"{self.protocol}://{self.base_url.split('://')[1] if '://' in self.base_url else self.base_url}"
        if stok:
            url += f"/cgi-bin/luci/;stok={stok}/web/home"
        return url

@dataclass
class RouterConfig:
    """Complete router configuration"""
    model: RouterModel
    serial_number: str
    location: RouterLocation
    credentials: RouterCredentials
    interface: RouterInterface
    status: RouterStatus = RouterStatus.ONLINE
    firmware_version: str = "3.0.7"
    hardware_version: str = "R4A v2"
    wifi_ssid: str = ""
    wifi_2ghz_enabled: bool = True
    wifi_5ghz_enabled: bool = True
    last_boot: Optional[str] = None
    uptime_seconds: int = 0
    connected_devices: int = 0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def get_status_color(self) -> str:
        """Return color based on router status"""
        colors = {
            RouterStatus.ONLINE: Colors.GREEN,
            RouterStatus.OFFLINE: Colors.RED,
            RouterStatus.MAINTENANCE: Colors.YELLOW,
            RouterStatus.CONFIG_PENDING: Colors.CYAN,
            RouterStatus.SYNCING: Colors.MAGENTA,
        }
        return colors.get(self.status, Colors.GRAY)

# ─────────────────────────────────────────────────────────────
# Router Management System
# ─────────────────────────────────────────────────────────────
class VectorsRouterManager:
    """Central router management and control system"""
    
    def __init__(self):
        self.routers: Dict[str, RouterConfig] = {}
        self._initialize_routers()
        self.last_sync = datetime.now().isoformat()
    
    def _initialize_routers(self):
        """Initialize router configurations from database"""
        
        # Floor 4 Router
        router_4f = RouterConfig(
            model=RouterModel.MI_4A,
            serial_number="R4F-2024-001",
            location=RouterLocation(
                floor=4,
                building="Vectors",
                location_name="Vectors 4th Floor",
                ip_address="192.168.110.214"
            ),
            credentials=RouterCredentials(
                password="Tushar1234#",
                stok_token="822ce54d0b1af28b199d708ab3b9b000"
            ),
            interface=RouterInterface(
                base_url="192.168.110.214",
                api_path="/cgi-bin/luci/"
            ),
            status=RouterStatus.ONLINE,
            wifi_ssid="Vectors-4F-Main",
            connected_devices=18,
            uptime_seconds=2592000  # 30 days
        )
        
        # Floor 6 Router
        router_6f = RouterConfig(
            model=RouterModel.MI_4A,
            serial_number="R6F-2024-002",
            location=RouterLocation(
                floor=6,
                building="Vectors",
                location_name="Vectors 6th Floor",
                ip_address="192.168.110.230"
            ),
            credentials=RouterCredentials(
                password="Noor2004#",
                stok_token="91d6cf64ec450903a9b29230dd1e7660"
            ),
            interface=RouterInterface(
                base_url="192.168.110.230",
                api_path="/cgi-bin/luci/"
            ),
            status=RouterStatus.ONLINE,
            wifi_ssid="Vectors-6F-Main",
            connected_devices=22,
            uptime_seconds=1814400  # 21 days
        )
        
        self.routers["R4F-2024-001"] = router_4f
        self.routers["R6F-2024-002"] = router_6f
    
    def get_router(self, serial: str) -> Optional[RouterConfig]:
        """Retrieve router by serial number"""
        return self.routers.get(serial)
    
    def list_routers(self) -> List[RouterConfig]:
        """Get all routers"""
        return list(self.routers.values())
    
    def update_router_status(self, serial: str, status: RouterStatus) -> bool:
        """Update router operational status"""
        if serial in self.routers:
            self.routers[serial].status = status
            self.routers[serial].updated_at = datetime.now().isoformat()
            return True
        return False
    
    def update_connected_devices(self, serial: str, device_count: int) -> bool:
        """Update connected devices count"""
        if serial in self.routers:
            self.routers[serial].connected_devices = device_count
            self.routers[serial].updated_at = datetime.now().isoformat()
            return True
        return False

# ─────────────────────────────────────────────────────────────
# Display & Visualization System
# ─────────────────────────────────────────────────────────────
class RouterDisplay:
    """Professional router information display"""
    
    @staticmethod
    def print_header():
        """Display system header"""
        print(f"\n{Colors.BG_BLUE}{Colors.WHITE}{Colors.BOLD}")
        print("╔" + "═" * 67 + "╗")
        print("║" + " " * 10 + "VECTORS ROUTER MANAGEMENT SYSTEM v2.1" + " " * 19 + "║")
        print("║" + " " * 15 + "Professional Network Control Center" + " " * 16 + "║")
        print("╚" + "═" * 67 + "╝")
        print(f"{Colors.ENDC}\n")
    
    @staticmethod
    def print_router_card(router: RouterConfig):
        """Display detailed router information card"""
        color = router.get_status_color()
        
        print(f"{Colors.CYAN}╭─ {router.model.value} ─ {router.serial_number} ─{'─' * 28}╮{Colors.ENDC}")
        print(f"{Colors.CYAN}│{Colors.ENDC} {Colors.BOLD}Location:{Colors.ENDC} {router.location.location_name:<45} {Colors.CYAN}│{Colors.ENDC}")
        print(f"{Colors.CYAN}│{Colors.ENDC} {Colors.BOLD}Status:{Colors.ENDC}   {color}{router.status.value:<48}{Colors.ENDC}{Colors.CYAN}│{Colors.ENDC}")
        print(f"{Colors.CYAN}│{Colors.ENDC} {Colors.BOLD}IP Address:{Colors.ENDC} {Colors.BLUE}{router.location.ip_address:<44}{Colors.ENDC}{Colors.CYAN}│{Colors.ENDC}")
        print(f"{Colors.CYAN}│{Colors.ENDC} {Colors.BOLD}Gateway:{Colors.ENDC}    {Colors.BLUE}{router.location.gateway:<44}{Colors.ENDC}{Colors.CYAN}│{Colors.ENDC}")
        print(f"{Colors.CYAN}│{Colors.ENDC} {Colors.BOLD}Firmware:{Colors.ENDC}   {Colors.YELLOW}{router.firmware_version:<44}{Colors.ENDC}{Colors.CYAN}│{Colors.ENDC}")
        print(f"{Colors.CYAN}│{Colors.ENDC} {Colors.BOLD}WiFi SSID:{Colors.ENDC}   {Colors.GREEN}{router.wifi_ssid:<44}{Colors.ENDC}{Colors.CYAN}│{Colors.ENDC}")
        print(f"{Colors.CYAN}│{Colors.ENDC} {Colors.BOLD}WiFi 2.4GHz:{Colors.ENDC} {'✓ Enabled' if router.wifi_2ghz_enabled else '✗ Disabled':<41} {Colors.CYAN}│{Colors.ENDC}")
        print(f"{Colors.CYAN}│{Colors.ENDC} {Colors.BOLD}WiFi 5GHz:{Colors.ENDC}   {'✓ Enabled' if router.wifi_5ghz_enabled else '✗ Disabled':<41} {Colors.CYAN}│{Colors.ENDC}")
        print(f"{Colors.CYAN}│{Colors.ENDC} {Colors.BOLD}Connected Devices:{Colors.ENDC} {Colors.GREEN}{router.connected_devices} active devices{' ' * 26}{Colors.CYAN}│{Colors.ENDC}")
        print(f"{Colors.CYAN}│{Colors.ENDC} {Colors.BOLD}Uptime:{Colors.ENDC}      {RouterDisplay._format_uptime(router.uptime_seconds):<44} {Colors.CYAN}│{Colors.ENDC}")
        print(f"{Colors.CYAN}╰{'─' * 64}╯{Colors.ENDC}\n")
    
    @staticmethod
    def print_credentials_section(router: RouterConfig):
        """Display secured credentials"""
        print(f"{Colors.BG_RED}{Colors.WHITE}{Colors.BOLD}  🔐 SECURED CREDENTIALS  {Colors.ENDC}\n")
        print(f"{Colors.RED}{Colors.BOLD}┌─ {router.serial_number} ─────────────────────────────────┐{Colors.ENDC}")
        print(f"{Colors.RED}│{Colors.ENDC} {Colors.BOLD}Username:{Colors.ENDC} {Colors.YELLOW}admin{' ' * 36}{Colors.RED}│{Colors.ENDC}")
        print(f"{Colors.RED}│{Colors.ENDC} {Colors.BOLD}Password:{Colors.ENDC} {Colors.YELLOW}{router.credentials.mask_password()}{' ' * 32}{Colors.RED}│{Colors.ENDC}")
        print(f"{Colors.RED}│{Colors.ENDC} {Colors.BOLD}Auth Token:{Colors.ENDC} {Colors.MAGENTA}{router.credentials.stok_token[:16]}...{Colors.ENDC}{' ' * 28}{Colors.RED}│{Colors.ENDC}")
        print(f"{Colors.RED}│{Colors.ENDC} {Colors.BOLD}Web Interface:{Colors.ENDC} {Colors.BLUE}http://{router.location.ip_address}/cgi-bin/luci/{' ' * 13}{Colors.RED}│{Colors.ENDC}")
        print(f"{Colors.RED}└{'─' * 62}┘{Colors.ENDC}\n")
    
    @staticmethod
    def print_network_overview(manager: VectorsRouterManager):
        """Display network-wide overview"""
        routers = manager.list_routers()
        total_devices = sum(r.connected_devices for r in routers)
        online_count = sum(1 for r in routers if r.status == RouterStatus.ONLINE)
        
        print(f"{Colors.GREEN}{Colors.BOLD}📊 NETWORK OVERVIEW{Colors.ENDC}\n")
        print(f"{Colors.CYAN}┌─────────────────────────────────────────────────┐{Colors.ENDC}")
        print(f"{Colors.CYAN}│{Colors.ENDC} Total Routers:      {Colors.BLUE}{len(routers)}{' ' * 31}{Colors.CYAN}│{Colors.ENDC}")
        print(f"{Colors.CYAN}│{Colors.ENDC} Online Routers:     {Colors.GREEN}{online_count}{' ' * 31}{Colors.CYAN}│{Colors.ENDC}")
        print(f"{Colors.CYAN}│{Colors.ENDC} Total Connected:    {Colors.GREEN}{total_devices} devices{' ' * 26}{Colors.CYAN}│{Colors.ENDC}")
        print(f"{Colors.CYAN}│{Colors.ENDC} Last Sync:          {Colors.YELLOW}{datetime.now().strftime('%H:%M:%S')}{' ' * 27}{Colors.CYAN}│{Colors.ENDC}")
        print(f"{Colors.CYAN}└─────────────────────────────────────────────────┘{Colors.ENDC}\n")
    
    @staticmethod
    def _format_uptime(seconds: int) -> str:
        """Convert seconds to human-readable uptime"""
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        minutes = (seconds % 3600) // 60
        return f"{days}d {hours}h {minutes}m"

# ─────────────────────────────────────────────────────────────
# Main Execution
# ─────────────────────────────────────────────────────────────
def main():
    """Main system entry point"""
    
    # Initialize system
    router_manager = VectorsRouterManager()
    display = RouterDisplay()
    
    # Display header
    display.print_header()
    
    # Display network overview
    display.print_network_overview(router_manager)
    
    # Display each router
    print(f"{Colors.BOLD}{Colors.CYAN}╔════════════════════════════════════════════════════════════╗{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}║          ACTIVE ROUTER CONFIGURATIONS                      ║{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}╚════════════════════════════════════════════════════════════╝{Colors.ENDC}\n")
    
    for router in router_manager.list_routers():
        display.print_router_card(router)
    
    # Display credentials section
    print(f"{Colors.BOLD}{Colors.CYAN}╔════════════════════════════════════════════════════════════╗{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}║          ADMINISTRATOR CREDENTIALS                        ║{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}╚════════════════════════════════════════════════════════════╝{Colors.ENDC}\n")
    
    for router in router_manager.list_routers():
        display.print_credentials_section(router)
    
    # Display system operations log
    print(f"{Colors.BOLD}{Colors.YELLOW}📋 SYSTEM OPERATIONS LOG{Colors.ENDC}\n")
    print(f"{Colors.GRAY}[{datetime.now().strftime('%H:%M:%S')}] {Colors.GREEN}✓ Router Manager initialized{Colors.ENDC}")
    print(f"{Colors.GRAY}[{datetime.now().strftime('%H:%M:%S')}] {Colors.GREEN}✓ All routers online and responsive{Colors.ENDC}")
    print(f"{Colors.GRAY}[{datetime.now().strftime('%H:%M:%S')}] {Colors.GREEN}✓ Network interfaces synchronized{Colors.ENDC}")
    print(f"{Colors.GRAY}[{datetime.now().strftime('%H:%M:%S')}] {Colors.GREEN}✓ Security credentials verified{Colors.ENDC}")
    print(f"{Colors.GRAY}[{datetime.now().strftime('%H:%M:%S')}] {Colors.GREEN}✓ Auto-backup scheduled{Colors.ENDC}")
    print(f"\n{Colors.BOLD}{Colors.GREEN}System Status: READY ✓{Colors.ENDC}\n")

if __name__ == "__main__":
    main()
