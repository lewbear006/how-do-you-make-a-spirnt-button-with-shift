"""
SMG weapon for Rent Quest
Low damage, very high fire rate
"""

from game.weapons.weapon import Weapon
from game.constants import WeaponType

class SMG(Weapon):
    """Submachine gun weapon"""
    
    def __init__(self):
        super().__init__(
            name="SMG",
            weapon_type=WeaponType.SMG,
            damage=18,
            fire_rate=0.08,  # 12.5 shots per second
            bullet_speed=350,
            magazine_size=40,
            reload_time=1.8,
            price=400,
            description="High rate of fire weapon. Great for crowd control."
        )