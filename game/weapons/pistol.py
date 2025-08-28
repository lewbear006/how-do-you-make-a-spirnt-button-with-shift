"""
Pistol weapon for Rent Quest
Basic starting weapon
"""

from game.weapons.weapon import Weapon
from game.constants import WeaponType

class Pistol(Weapon):
    """Basic pistol weapon"""
    
    def __init__(self):
        super().__init__(
            name="Basic Pistol",
            weapon_type=WeaponType.PISTOL,
            damage=25,
            fire_rate=0.5,  # 2 shots per second
            bullet_speed=400,
            magazine_size=12,
            reload_time=1.5,
            price=0,  # Starting weapon
            description="A reliable sidearm. Good for beginners."
        )