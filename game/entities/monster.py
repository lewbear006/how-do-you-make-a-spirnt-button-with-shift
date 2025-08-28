"""
Monster Entity for Rent Quest
Base class for all monsters in the game
"""

import pygame
import math
import random
from typing import Optional, TYPE_CHECKING
from game.constants import *

if TYPE_CHECKING:
    from game.entities.player import Player

class Monster:
    """Base monster class"""
    
    def __init__(self, x: float, y: float, monster_type: MonsterType, 
                 health: int, damage: int, speed: float, money_drop: int):
        """Initialize monster"""
        # Position and movement
        self.x = x
        self.y = y
        self.vel_x = 0.0
        self.vel_y = 0.0
        
        # Monster properties
        self.monster_type = monster_type
        self.max_health = health
        self.health = health
        self.damage = damage
        self.speed = speed
        self.money_drop = money_drop
        
        # Visual properties
        self.size = MONSTER_SIZE
        self.color = self._get_color_for_type()
        self.rect = pygame.Rect(x - self.size//2, y - self.size//2, self.size, self.size)
        
        # AI and behavior
        self.target: Optional['Player'] = None
        self.attack_range = 30.0
        self.attack_cooldown = 1.0  # seconds
        self.last_attack_time = 0.0
        
        # Effects
        self.damage_flash_timer = 0.0
        self.is_dead = False
        
    def _get_color_for_type(self) -> tuple:
        """Get color based on monster type"""
        color_map = {
            MonsterType.ZOMBIE: (100, 150, 100),    # Greenish
            MonsterType.GOBLIN: (150, 100, 100),    # Reddish
            MonsterType.ORC: (120, 120, 100),       # Brownish
            MonsterType.SKELETON: (200, 200, 200),  # White
            MonsterType.BOSS_TROLL: (80, 50, 120),  # Purple
        }
        return color_map.get(self.monster_type, GRAY)
        
    def update(self, dt: float, player: 'Player'):
        """Update monster state"""
        if self.is_dead:
            return
            
        self.target = player
        self._update_ai(dt)
        self._update_movement(dt)
        self._update_effects(dt)
        self._update_rect()
        
    def _update_ai(self, dt: float):
        """Update monster AI behavior"""
        if not self.target:
            return
            
        # Calculate distance to player
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance <= self.attack_range:
            # Attack if in range and cooldown is ready
            current_time = pygame.time.get_ticks() / 1000.0
            if current_time - self.last_attack_time >= self.attack_cooldown:
                self._attack_target()
                self.last_attack_time = current_time
        else:
            # Move towards player
            if distance > 0:
                self.vel_x = (dx / distance) * self.speed
                self.vel_y = (dy / distance) * self.speed
                
    def _update_movement(self, dt: float):
        """Update monster position"""
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt
        
    def _update_effects(self, dt: float):
        """Update visual effects"""
        if self.damage_flash_timer > 0:
            self.damage_flash_timer -= dt
            
    def _update_rect(self):
        """Update collision rectangle"""
        self.rect.center = (int(self.x), int(self.y))
        
    def _attack_target(self):
        """Attack the target player"""
        if self.target:
            self.target.take_damage(self.damage)
            
    def take_damage(self, damage: int) -> bool:
        """Take damage and return True if monster dies"""
        self.health -= damage
        self.damage_flash_timer = 0.1
        
        if self.health <= 0:
            self.health = 0
            self.is_dead = True
            return True
        return False
        
    def render(self, screen: pygame.Surface):
        """Render the monster"""
        if self.is_dead:
            return
            
        # Choose color based on damage flash
        color = RED if self.damage_flash_timer > 0 else self.color
        
        # Draw monster as a circle
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.size // 2)
        
        # Draw health bar above monster
        if self.health < self.max_health:
            self._render_health_bar(screen)
            
    def _render_health_bar(self, screen: pygame.Surface):
        """Render monster health bar"""
        bar_width = self.size
        bar_height = 4
        bar_x = int(self.x - bar_width // 2)
        bar_y = int(self.y - self.size // 2 - 8)
        
        # Background
        pygame.draw.rect(screen, DARK_GRAY, (bar_x, bar_y, bar_width, bar_height))
        
        # Health fill
        health_percentage = self.health / self.max_health
        fill_width = int(bar_width * health_percentage)
        pygame.draw.rect(screen, HEALTH_COLOR, (bar_x, bar_y, fill_width, bar_height))
        
    def get_rect(self) -> pygame.Rect:
        """Get monster collision rectangle"""
        return self.rect
        
    def get_money_drop(self) -> int:
        """Get money dropped when monster dies"""
        # Add some randomness to money drops
        base_money = self.money_drop
        variation = random.randint(-2, 3)
        return max(1, base_money + variation)

# Specific monster classes
class Zombie(Monster):
    """Zombie monster - slow but tanky"""
    
    def __init__(self, x: float, y: float):
        super().__init__(
            x, y,
            MonsterType.ZOMBIE,
            health=80,
            damage=15,
            speed=60,
            money_drop=12
        )

class Goblin(Monster):
    """Goblin monster - fast but weak"""
    
    def __init__(self, x: float, y: float):
        super().__init__(
            x, y,
            MonsterType.GOBLIN,
            health=40,
            damage=8,
            speed=120,
            money_drop=8
        )

class Orc(Monster):
    """Orc monster - balanced stats"""
    
    def __init__(self, x: float, y: float):
        super().__init__(
            x, y,
            MonsterType.ORC,
            health=60,
            damage=12,
            speed=80,
            money_drop=15
        )

class Skeleton(Monster):
    """Skeleton monster - medium stats"""
    
    def __init__(self, x: float, y: float):
        super().__init__(
            x, y,
            MonsterType.SKELETON,
            health=50,
            damage=10,
            speed=90,
            money_drop=10
        )

class BossTroll(Monster):
    """Boss Troll - very strong boss monster"""
    
    def __init__(self, x: float, y: float):
        super().__init__(
            x, y,
            MonsterType.BOSS_TROLL,
            health=300,
            damage=25,
            speed=50,
            money_drop=100
        )
        self.size = MONSTER_SIZE * 2  # Bigger than normal monsters
        self.attack_range = 50.0