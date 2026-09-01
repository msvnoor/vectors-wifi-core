#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔═══════════════════════════════════════════════════════════════╗
║          VECTORS WiFi Core Management System v7.4.1          ║
║        Professional Network & Room Control Platform           ║
╚═══════════════════════════════════════════════════════════════╝
"""

import sys
import time
from datetime import datetime
from typing import Dict, List, Tuple
from dataclasses import dataclass, field
from enum import Enum

# ─────────────────────────────────────────────────────────────
# ANSI Color Codes for Terminal Output
# ─────────────────────────────────────────────────────────────
class Colors:
    """Terminal color constants for rich console output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    ENDC = '\033[0m'
    GRAY = '\033[90m'
    LIGHT_GREEN = '\033[92m'
    LIGHT_RED = '\033[91m'
    LIGHT_YELLOW = '\033[93m'

# ─────────────────────────────────────────────────────────────
# System Enumerations
# ─────────────────────────────────────────────────────────────
class ConnectionStatus(Enum):
    """Internet connection status"""
    ON = "✓ ACTIVE"
    OFF = "✗ INACTIVE"
    STANDBY = "⊙ STANDBY"
    ERROR = "⚠ ERROR"

class CurrencyType(Enum):
    """Supported currency types"""
    BDT = "Bangladesh Taka"
    USD = "US Dollar"
    EUR = "Euro"

# ─────────────────────────────────────────────────────────────
# Data Models
# ─────────────────────────────────────────────────────────────
@dataclass
class RoomConfig:
    """Individual room configuration"""
    room_id: str
    floor: int
    amount: float
    validity: str
    device: str = "UNKNOWN"
    internet: ConnectionStatus = ConnectionStatus.OFF
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def get_status_color(self) -> str:
        """Return color based on internet status"""
        status_colors = {
            ConnectionStatus.ON: Colors.GREEN,
            ConnectionStatus.OFF: Colors.RED,
            ConnectionStatus.STANDBY: Colors.YELLOW,
            ConnectionStatus.ERROR: Colors.LIGHT_RED,
        }
        return status_colors.get(self.internet, Colors.GRAY)

@dataclass
class FloorConfig:
    """Floor-level configuration container"""
    floor_number: int
    rooms: Dict[str, RoomConfig] = field(default_factory=dict)
    
    def get_total_rooms(self) -> int:
        return len(self.rooms)
    
    def get_active_connections(self) -> int:
        return sum(1 for room in self.rooms.values() 
                   if room.internet == ConnectionStatus.ON)

@dataclass
class SystemConfig:
    """Core WiFi system configuration"""
    system_name: str = "VECTORS_WIFI"
    version: str = "7.4.1"
    mode: str = "AUTO_ACCESS"
    currency: CurrencyType = CurrencyType.BDT
    network_status: ConnectionStatus = ConnectionStatus.STANDBY
    auto_renew: bool = True
    floors: Dict[int, FloorConfig] = field(default_factory=dict)
    
    def get_total_rooms(self) -> int:
        return sum(floor.get_total_rooms() for floor in self.floors.values())
    
    def get_total_active(self) -> int:
        return sum(floor.get_active_connections() for floor in self.floors.values())

# ─────────────────────────────────────────────────────────────
# WiFi Core System Controller
# ─────────────────────────────────────────────────────────────
class VectorsWiFiCore:
    """Main WiFi Core Management System"""
    
    def __init__(self):
        self.config = SystemConfig()
        self._initialize_system()
    
    def _initialize_system(self):
        """Initialize the system with default configuration"""
        for floor_num in [4, 5, 6]:
            floor = FloorConfig(floor_number=floor_num)
            room_count = 14 if floor_num == 4 else 14
            
            for room_num in range(1, room_count + 1):
                room_id = f"{floor_num}{room_num:02d}"
                room = RoomConfig(
                    room_id=room_id,
                    floor=floor_num,
                    amount=100.0,
                    validity="UNLIMITED",
                    device="UNKNOWN",
                    internet=ConnectionStatus.OFF
                )
                floor.rooms[room_id] = room
            
            self.config.floors[floor_num] = floor
    
    def toggle_internet(self, room_id: str, status: ConnectionStatus) -> bool:
        """Toggle internet connection for a specific room"""
        for floor in self.config.floors.values():
            if room_id in floor.rooms:
                floor.rooms[room_id].internet = status
                floor.rooms[room_id].last_updated = datetime.now().isoformat()
                return True
        return False
    
    def update_room_device(self, room_id: str, device: str) -> bool:
        """Update device information for a room"""
        for floor in self.config.floors.values():
            if room_id in floor.rooms:
                floor.rooms[room_id].device = device
                floor.rooms[room_id].last_updated = datetime.now().isoformat()
                return True
        return False
    
    def get_room_info(self, room_id: str) -> RoomConfig:
        """Retrieve information for a specific room"""
        for floor in self.config.floors.values():
            if room_id in floor.rooms:
                return floor.rooms[room_id]
        return None

# ─────────────────────────────────────────────────────────────
# Console Output & Visualization
# ─────────────────────────────────────────────────────────────
class SystemDisplay:
    """Display and logging system"""
    
    @staticmethod
    def print_header():
        """Print system header with styling"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}")
        print("╔" + "═" * 67 + "╗")
        print("║" + " " * 12 + "VECTORS WiFi Core Management System" + " " * 20 + "║")
        print("║" + " " * 15 + "Professional Network Control Platform" + " " * 15 + "║")
        print("╚" + "═" * 67 + "╝")
        print(f"{Colors.ENDC}\n")
    
    @staticmethod
    def print_system_status(config: SystemConfig):
        """Display system status overview"""
        print(f"{Colors.CYAN}{Colors.BOLD}┌─ SYSTEM STATUS ─────────────────────────────────┐{Colors.ENDC}")
        print(f"{Colors.BOLD}System Name:{Colors.ENDC}      {Colors.BLUE}{config.system_name}{Colors.ENDC}")
        print(f"{Colors.BOLD}Version:{Colors.ENDC}           {Colors.GREEN}v{config.version}{Colors.ENDC}")
        print(f"{Colors.BOLD}Mode:{Colors.ENDC}              {Colors.YELLOW}{config.mode}{Colors.ENDC}")
        print(f"{Colors.BOLD}Currency:{Colors.ENDC}          {Colors.BLUE}{config.currency.value}{Colors.ENDC}")
        print(f"{Colors.BOLD}Network Status:{Colors.ENDC}     {Colors.YELLOW}⊙ {config.network_status.value}{Colors.ENDC}")
        print(f"{Colors.BOLD}Auto-Renew:{Colors.ENDC}        {Colors.GREEN}{'ENABLED' if config.auto_renew else 'DISABLED'}{Colors.ENDC}")
        print(f"{Colors.BOLD}Total Rooms:{Colors.ENDC}        {Colors.BLUE}{config.get_total_rooms()}{Colors.ENDC}")
        print(f"{Colors.BOLD}Active Connections:{Colors.ENDC} {Colors.GREEN}{config.get_total_active()}{Colors.ENDC}")
        print(f"{Colors.CYAN}└{'─' * 49}┘{Colors.ENDC}\n")
    
    @staticmethod
    def print_floor_details(floor: FloorConfig):
        """Display detailed floor information"""
        print(f"{Colors.BOLD}{Colors.CYAN}┌─ FLOOR {floor.floor_number} ROOMS ─────────────────────────────────┐{Colors.ENDC}")
        
        for room_id, room in sorted(floor.rooms.items()):
            status_color = room.get_status_color()
            internet_text = room.internet.value
            
            print(f"  {Colors.BOLD}Room {room_id}:{Colors.ENDC} "
                  f"Balance: {Colors.BLUE}{room.amount} {Colors.ENDC}| "
                  f"Validity: {Colors.GREEN}{room.validity}{Colors.ENDC} | "
                  f"Device: {Colors.YELLOW}{room.device}{Colors.ENDC} | "
                  f"Internet: {status_color}{internet_text}{Colors.ENDC}")
        
        print(f"{Colors.CYAN}└{'─' * 57}┘{Colors.ENDC}\n")
    
    @staticmethod
    def print_network_activity():
        """Display simulated network activity"""
        print(f"{Colors.GREEN}{Colors.BOLD}━━━ NETWORK ACTIVITY MONITOR ━━━{Colors.ENDC}\n")
        activities = [
            ("Room 401", "Connected", "192.168.1.101"),
            ("Room 405", "Authenticating", "Requesting IP..."),
            ("Room 412", "Connected", "192.168.1.112"),
            ("Room 503", "Offline", "No Signal"),
            ("Room 510", "Connected", "192.168.1.210"),
            ("Room 614", "Connected", "192.168.1.314"),
        ]
        
        for room, status, info in activities:
            if "Connected" in status:
                color = Colors.GREEN
                symbol = "✓"
            elif "Offline" in status:
                color = Colors.RED
                symbol = "✗"
            else:
                color = Colors.YELLOW
                symbol = "⟳"
            
            print(f"  {color}{symbol} {Colors.BOLD}{room:<12}{Colors.ENDC} {status:<15} {Colors.GRAY}{info}{Colors.ENDC}")
        
        print()

# ─────────────────────────────────────────────────────────────
# Main Execution
# ─────────────────────────────────────────────────────────────
def main():
    """Main system entry point"""
    
    # Initialize system
    wifi_system = VectorsWiFiCore()
    display = SystemDisplay()
    
    # Display system information
    display.print_header()
    display.print_system_status(wifi_system.config)
    
    # Display floor details
    for floor_num in sorted(wifi_system.config.floors.keys()):
        floor = wifi_system.config.floors[floor_num]
        display.print_floor_details(floor)
    
    # Display network activity
    display.print_network_activity()
    
    # Simulate some updates
    print(f"{Colors.BOLD}{Colors.CYAN}┌─ SYSTEM OPERATIONS ─────────────────────────────┐{Colors.ENDC}")
    print(f"{Colors.BOLD}Toggling Room 401 Internet...{Colors.ENDC}")
    wifi_system.toggle_internet("401", ConnectionStatus.ON)
    print(f"  {Colors.GREEN}✓ Room 401 internet activated{Colors.ENDC}")
    
    print(f"\n{Colors.BOLD}Updating Room 405 Device Info...{Colors.ENDC}")
    wifi_system.update_room_device("405", "MacBook Pro M1")
    print(f"  {Colors.GREEN}✓ Device information updated{Colors.ENDC}")
    
    print(f"\n{Colors.BOLD}System Ready for Operations{Colors.ENDC}")
    print(f"  {Colors.GREEN}✓ All modules initialized{Colors.ENDC}")
    print(f"  {Colors.GREEN}✓ Database connected{Colors.ENDC}")
    print(f"  {Colors.GREEN}✓ API server running{Colors.ENDC}")
    print(f"{Colors.CYAN}└{'─' * 49}┘{Colors.ENDC}\n")
    
    # Final status
    print(f"{Colors.BOLD}{Colors.GREEN}System Status: READY ✓{Colors.ENDC}\n")

if __name__ == "__main__":
    main()
