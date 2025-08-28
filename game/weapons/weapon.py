"""
Base Weapon class for Rent Quest
All weapons inherit from this base class
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from game.constants import WeaponType
from game.systems.inventory import Item, ItemType

class Weapon(Item):
    """Base weapon class"""
    
    def __init__(self, name: str, weapon_type: WeaponType, damage: int, 
                 fire_rate: float, bullet_speed: float = 400, 
                 magazine_size: int = -1, reload_time: float = 0.0,
                 price: int = 100, description: str = ""):
        """Initialize weapon"""
        super().__init__(name, ItemType.WEAPON, description, price)
        
        # Weapon stats
        self.weapon_type = weapon_type
        self.base_damage = damage
        self.damage = damage  # Current damage (can be upgraded)
        self.fire_rate = fire_rate  # Time between shots in seconds
        self.bullet_speed = bullet_speed
        self.magazine_size = magazine_size  # -1 for unlimited
        self.reload_time = reload_time
        
        # Current state
        self.current_ammo = magazine_size if magazine_size > 0 else -1
        self.is_reloading = False
        self.reload_timer = 0.0
        
        # Upgrade levels
        self.damage_level = 1
        self.fire_rate_level = 1
        self.magazine_level = 1
        
    def update(self, dt: float):
        """Update weapon state"""
        if self.is_reloading:
            self.reload_timer -= dt
            if self.reload_timer <= 0:
                self.is_reloading = False
                self.current_ammo = self.magazine_size
                
    def can_shoot(self) -> bool:
        """Check if weapon can shoot"""
        if self.is_reloading:
            return False
        if self.magazine_size > 0 and self.current_ammo <= 0:
            return False
        return True
        
    def shoot(self) -> bool:
        """Attempt to shoot the weapon"""
        if not self.can_shoot():
            return False
            
        if self.magazine_size > 0:
            self.current_ammo -= 1
            
        return True
        
    def reload(self):
        """Start reloading the weapon"""
        if self.magazine_size > 0 and not self.is_reloading and self.current_ammo < self.magazine_size:
            self.is_reloading = True
            self.reload_timer = self.reload_time
            
    def upgrade_damage(self) -> int:
        """Upgrade weapon damage, returns upgrade cost"""
        cost = self.damage_level * 100
        self.damage_level += 1
        self.damage = int(self.base_damage * (1 + (self.damage_level - 1) * 0.25))
        return cost
        
    def upgrade_fire_rate(self) -> int:
        """Upgrade weapon fire rate, returns upgrade cost"""
        cost = self.fire_rate_level * 75
        self.fire_rate_level += 1
        self.fire_rate = max(0.1, self.fire_rate * 0.9)  # Reduce time between shots
        return cost
        
    def upgrade_magazine(self) -> int:
        """Upgrade magazine size, returns upgrade cost"""
        if self.magazine_size <= 0:  # Can't upgrade unlimited ammo weapons
            return 0
            
        cost = self.magazine_level * 50
        self.magazine_level += 1
        self.magazine_size = int(self.magazine_size * 1.2)
        self.current_ammo = self.magazine_size  # Refill on upgrade
        return cost
        
    def get_stats(self) -> Dict[str, Any]:
        """Get weapon statistics"""
        return {
            "name": self.name,
            "type": self.weapon_type.value,
            "damage": self.damage,
            "fire_rate": round(1.0 / self.fire_rate, 1),  # Shots per second
            "magazine_size": self.magazine_size if self.magazine_size > 0 else "Unlimited",
            "current_ammo": self.current_ammo if self.current_ammo > 0 else "Unlimited",
            "damage_level": self.damage_level,
            "fire_rate_level": self.fire_rate_level,
            "magazine_level": self.magazine_level
        }