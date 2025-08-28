"""
Shotgun weapon for Rent Quest
High damage, slow fire rate, multiple pellets
"""

from game.weapons.weapon import Weapon
from game.constants import WeaponType

class Shotgun(Weapon):
    """Shotgun weapon"""
    
    def __init__(self):
        super().__init__(
            name="Combat Shotgun",
            weapon_type=WeaponType.SHOTGUN,
            damage=80,  # Per pellet, fires multiple
            fire_rate=1.0,  # 1 shot per second
            bullet_speed=350,
            magazine_size=8,
            reload_time=2.5,
            price=750,
            description="Devastating close-range weapon. Fires multiple pellets."
        )