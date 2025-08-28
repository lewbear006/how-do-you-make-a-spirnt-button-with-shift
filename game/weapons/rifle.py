"""
Rifle weapon for Rent Quest
High damage, medium fire rate
"""

from game.weapons.weapon import Weapon
from game.constants import WeaponType

class AssaultRifle(Weapon):
    """Assault rifle weapon"""
    
    def __init__(self):
        super().__init__(
            name="Assault Rifle",
            weapon_type=WeaponType.RIFLE,
            damage=40,
            fire_rate=0.15,  # ~6.7 shots per second
            bullet_speed=500,
            magazine_size=30,
            reload_time=2.0,
            price=500,
            description="High damage automatic rifle. Good for sustained combat."
        )