"""
Sniper rifle for Rent Quest
Very high damage, very slow fire rate
"""

from game.weapons.weapon import Weapon
from game.constants import WeaponType

class SniperRifle(Weapon):
    """Sniper rifle weapon"""
    
    def __init__(self):
        super().__init__(
            name="Sniper Rifle",
            weapon_type=WeaponType.SNIPER,
            damage=150,
            fire_rate=2.0,  # 0.5 shots per second
            bullet_speed=800,
            magazine_size=5,
            reload_time=3.0,
            price=1200,
            description="Extremely high damage precision weapon. One shot, one kill."
        )