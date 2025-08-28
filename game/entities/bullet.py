"""
Bullet Entity for Rent Quest
Projectiles fired by weapons
"""

import pygame
from game.constants import *

class Bullet:
    """Bullet projectile class"""
    
    def __init__(self, x: float, y: float, dir_x: float, dir_y: float, 
                 damage: int, speed: float = BULLET_SPEED):
        """Initialize bullet"""
        self.x = x
        self.y = y
        self.dir_x = dir_x
        self.dir_y = dir_y
        self.damage = damage
        self.speed = speed
        self.size = BULLET_SIZE
        self.color = YELLOW
        self.rect = pygame.Rect(x - self.size//2, y - self.size//2, self.size, self.size)
        
    def update(self, dt: float):
        """Update bullet position"""
        self.x += self.dir_x * self.speed * dt
        self.y += self.dir_y * self.speed * dt
        self.rect.center = (int(self.x), int(self.y))
        
    def render(self, screen: pygame.Surface):
        """Render the bullet"""
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size // 2)
        
    def get_rect(self) -> pygame.Rect:
        """Get bullet collision rectangle"""
        return self.rect