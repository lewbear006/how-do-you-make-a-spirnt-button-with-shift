"""
Upgrade System for Rent Quest
Handles weapon and player upgrades
"""

from typing import Dict, Any, Optional, TYPE_CHECKING
from game.constants import *

if TYPE_CHECKING:
    from game.entities.player import Player
    from game.weapons.weapon import Weapon

class UpgradeSystem:
    """Manages upgrades for weapons and player"""
    
    def __init__(self):
        """Initialize upgrade system"""
        self.upgrade_costs = {
            "damage": {"base": 100, "multiplier": 1.5},
            "fire_rate": {"base": 75, "multiplier": 1.3},
            "magazine": {"base": 50, "multiplier": 1.2},
            "player_health": {"base": 200, "multiplier": 2.0},
            "player_speed": {"base": 150, "multiplier": 1.8}
        }
        
    def calculate_upgrade_cost(self, upgrade_type: str, current_level: int) -> int:
        """Calculate cost for specific upgrade level"""
        if upgrade_type not in self.upgrade_costs:
            return 999999  # Invalid upgrade
            
        base_cost = self.upgrade_costs[upgrade_type]["base"]
        multiplier = self.upgrade_costs[upgrade_type]["multiplier"]
        
        return int(base_cost * (multiplier ** (current_level - 1)))
        
    def upgrade_weapon_damage(self, weapon: 'Weapon', player: 'Player') -> bool:
        """Upgrade weapon damage"""
        cost = self.calculate_upgrade_cost("damage", weapon.damage_level)
        
        if player.spend_money(cost):
            weapon.upgrade_damage()
            return True
        return False
        
    def upgrade_weapon_fire_rate(self, weapon: 'Weapon', player: 'Player') -> bool:
        """Upgrade weapon fire rate"""
        cost = self.calculate_upgrade_cost("fire_rate", weapon.fire_rate_level)
        
        if player.spend_money(cost):
            weapon.upgrade_fire_rate()
            return True
        return False
        
    def upgrade_weapon_magazine(self, weapon: 'Weapon', player: 'Player') -> bool:
        """Upgrade weapon magazine size"""
        if weapon.magazine_size <= 0:  # Can't upgrade unlimited ammo weapons
            return False
            
        cost = self.calculate_upgrade_cost("magazine", weapon.magazine_level)
        
        if player.spend_money(cost):
            weapon.upgrade_magazine()
            return True
        return False
        
    def upgrade_player_health(self, player: 'Player') -> bool:
        """Upgrade player maximum health"""
        # Track player health upgrade level (could add to player class)
        if not hasattr(player, 'health_upgrade_level'):
            player.health_upgrade_level = 1
            
        cost = self.calculate_upgrade_cost("player_health", player.health_upgrade_level)
        
        if player.spend_money(cost):
            old_max = player.max_health
            player.max_health += 25
            player.health += 25  # Also heal player
            player.health_upgrade_level += 1
            print(f"Health upgraded! {old_max} -> {player.max_health}")
            return True
        return False
        
    def upgrade_player_speed(self, player: 'Player') -> bool:
        """Upgrade player movement speed"""
        # Track player speed upgrade level (could add to player class)
        if not hasattr(player, 'speed_upgrade_level'):
            player.speed_upgrade_level = 1
            
        cost = self.calculate_upgrade_cost("player_speed", player.speed_upgrade_level)
        
        if player.spend_money(cost):
            # Increase player speed by 10%
            global PLAYER_SPEED
            PLAYER_SPEED = int(PLAYER_SPEED * 1.1)
            player.speed_upgrade_level += 1
            print(f"Speed upgraded! New speed: {PLAYER_SPEED}")
            return True
        return False
        
    def get_upgrade_info(self, upgrade_type: str, current_level: int) -> Dict[str, Any]:
        """Get information about an upgrade"""
        cost = self.calculate_upgrade_cost(upgrade_type, current_level)
        
        upgrade_descriptions = {
            "damage": f"Increase weapon damage by 25% (Level {current_level} -> {current_level + 1})",
            "fire_rate": f"Increase fire rate by 10% (Level {current_level} -> {current_level + 1})",
            "magazine": f"Increase magazine size by 20% (Level {current_level} -> {current_level + 1})",
            "player_health": f"Increase max health by 25 (Level {current_level} -> {current_level + 1})",
            "player_speed": f"Increase movement speed by 10% (Level {current_level} -> {current_level + 1})"
        }
        
        return {
            "type": upgrade_type,
            "current_level": current_level,
            "cost": cost,
            "description": upgrade_descriptions.get(upgrade_type, "Unknown upgrade")
        }
        
    def get_all_weapon_upgrades(self, weapon: 'Weapon') -> Dict[str, Dict[str, Any]]:
        """Get all available upgrades for a weapon"""
        upgrades = {}
        
        upgrades["damage"] = self.get_upgrade_info("damage", weapon.damage_level)
        upgrades["fire_rate"] = self.get_upgrade_info("fire_rate", weapon.fire_rate_level)
        
        if weapon.magazine_size > 0:  # Only for weapons with limited ammo
            upgrades["magazine"] = self.get_upgrade_info("magazine", weapon.magazine_level)
            
        return upgrades
        
    def get_all_player_upgrades(self, player: 'Player') -> Dict[str, Dict[str, Any]]:
        """Get all available upgrades for player"""
        upgrades = {}
        
        health_level = getattr(player, 'health_upgrade_level', 1)
        speed_level = getattr(player, 'speed_upgrade_level', 1)
        
        upgrades["player_health"] = self.get_upgrade_info("player_health", health_level)
        upgrades["player_speed"] = self.get_upgrade_info("player_speed", speed_level)
        
        return upgrades