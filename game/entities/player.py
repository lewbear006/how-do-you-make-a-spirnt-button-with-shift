"""
Player Entity for Rent Quest
The main character controlled by the player
"""

import pygame
import math
from typing import List, Dict, Optional
from game.constants import *
from game.entities.bullet import Bullet
from game.systems.inventory import Inventory
from game.weapons.weapon import Weapon
from game.weapons.pistol import Pistol

class Player:
    """Player character class"""
    
    def __init__(self, x: float, y: float):
        """Initialize player"""
        # Position and movement
        self.x = x
        self.y = y
        self.vel_x = 0.0
        self.vel_y = 0.0
        
        # Visual properties
        self.size = PLAYER_SIZE
        self.color = BLUE
        self.rect = pygame.Rect(x - self.size//2, y - self.size//2, self.size, self.size)
        
        # Player stats
        self.max_health = PLAYER_MAX_HEALTH
        self.health = self.max_health
        self.money = PLAYER_START_MONEY
        self.level = 1
        self.experience = 0
        self.experience_to_next_level = 100
        
        # Combat
        self.current_weapon: Optional[Weapon] = Pistol()
        self.bullets: List[Bullet] = []
        self.last_shot_time = 0.0
        
        # Inventory and equipment
        self.inventory = Inventory()
        
        # Input state
        self.keys_pressed = set()
        self.mouse_pos = (0, 0)
        self.is_shooting = False
        
        # Animation and effects
        self.damage_flash_timer = 0.0
        self.is_moving = False
        
    def update(self, dt: float, screen_width: int, screen_height: int):
        """Update player state"""
        self._handle_movement(dt, screen_width, screen_height)
        self._handle_shooting(dt)
        self._update_bullets(dt, screen_width, screen_height)
        self._update_effects(dt)
        self._update_rect()
        
    def _handle_movement(self, dt: float, screen_width: int, screen_height: int):
        """Handle player movement"""
        # Reset velocity
        self.vel_x = 0.0
        self.vel_y = 0.0
        
        # Check movement keys
        if MOVE_LEFT in self.keys_pressed:
            self.vel_x -= PLAYER_SPEED
        if MOVE_RIGHT in self.keys_pressed:
            self.vel_x += PLAYER_SPEED
        if MOVE_UP in self.keys_pressed:
            self.vel_y -= PLAYER_SPEED
        if MOVE_DOWN in self.keys_pressed:
            self.vel_y += PLAYER_SPEED
            
        # Normalize diagonal movement
        if self.vel_x != 0 and self.vel_y != 0:
            length = math.sqrt(self.vel_x**2 + self.vel_y**2)
            self.vel_x = (self.vel_x / length) * PLAYER_SPEED
            self.vel_y = (self.vel_y / length) * PLAYER_SPEED
            
        # Update position
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt
        
        # Keep player on screen
        half_size = self.size // 2
        self.x = max(half_size, min(screen_width - half_size, self.x))
        self.y = max(half_size, min(screen_height - half_size, self.y))
        
        # Update moving state
        self.is_moving = (self.vel_x != 0 or self.vel_y != 0)
        
    def _handle_shooting(self, dt: float):
        """Handle player shooting"""
        current_time = pygame.time.get_ticks() / 1000.0
        
        if self.is_shooting and self.current_weapon:
            if current_time - self.last_shot_time >= self.current_weapon.fire_rate:
                self._shoot()
                self.last_shot_time = current_time
                
    def _shoot(self):
        """Create a bullet in the direction of the mouse"""
        if not self.current_weapon:
            return
            
        # Calculate direction to mouse
        dx = self.mouse_pos[0] - self.x
        dy = self.mouse_pos[1] - self.y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 0:
            # Normalize direction
            dir_x = dx / distance
            dir_y = dy / distance
            
            # Create bullet
            bullet = Bullet(
                self.x, self.y, 
                dir_x, dir_y,
                self.current_weapon.damage,
                self.current_weapon.bullet_speed
            )
            self.bullets.append(bullet)
            
            # Play sound effect (if audio manager is available)
            # self.game_engine.audio_manager.play_sound("gun_shot")
            
    def _update_bullets(self, dt: float, screen_width: int, screen_height: int):
        """Update all player bullets"""
        # Update bullets
        for bullet in self.bullets[:]:  # Copy list to avoid modification during iteration
            bullet.update(dt)
            
            # Remove bullets that are off-screen
            if (bullet.x < 0 or bullet.x > screen_width or 
                bullet.y < 0 or bullet.y > screen_height):
                self.bullets.remove(bullet)
                
    def _update_effects(self, dt: float):
        """Update visual effects"""
        if self.damage_flash_timer > 0:
            self.damage_flash_timer -= dt
            
    def _update_rect(self):
        """Update collision rectangle"""
        self.rect.center = (int(self.x), int(self.y))
        
    def handle_event(self, event: pygame.event.Event):
        """Handle input events"""
        if event.type == pygame.KEYDOWN:
            self.keys_pressed.add(event.key)
            if event.key == SHOOT:
                self.is_shooting = True
                
        elif event.type == pygame.KEYUP:
            self.keys_pressed.discard(event.key)
            if event.key == SHOOT:
                self.is_shooting = False
                
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                self.is_shooting = True
                
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.is_shooting = False
                
        elif event.type == pygame.MOUSEMOTION:
            self.mouse_pos = event.pos
            
    def take_damage(self, damage: int):
        """Take damage and handle death"""
        self.health -= damage
        self.damage_flash_timer = 0.2  # Flash red for 0.2 seconds
        
        if self.health <= 0:
            self.health = 0
            return True  # Player is dead
        return False
        
    def heal(self, amount: int):
        """Heal the player"""
        self.health = min(self.max_health, self.health + amount)
        
    def add_money(self, amount: int):
        """Add money to player"""
        self.money += amount
        
    def spend_money(self, amount: int) -> bool:
        """Spend money if player has enough"""
        if self.money >= amount:
            self.money -= amount
            return True
        return False
        
    def add_experience(self, amount: int):
        """Add experience and handle level ups"""
        self.experience += amount
        
        while self.experience >= self.experience_to_next_level:
            self.experience -= self.experience_to_next_level
            self.level += 1
            self.experience_to_next_level = int(self.experience_to_next_level * 1.5)
            
            # Level up bonuses
            self.max_health += 10
            self.health = self.max_health  # Full heal on level up
            
    def render(self, screen: pygame.Surface):
        """Render the player"""
        # Choose color based on damage flash
        color = RED if self.damage_flash_timer > 0 else self.color
        
        # Draw player as a circle
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.size // 2)
        
        # Draw weapon direction indicator
        if self.current_weapon:
            dx = self.mouse_pos[0] - self.x
            dy = self.mouse_pos[1] - self.y
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance > 0:
                # Draw line showing aim direction
                end_x = self.x + (dx / distance) * (self.size // 2 + 10)
                end_y = self.y + (dy / distance) * (self.size // 2 + 10)
                pygame.draw.line(screen, WHITE, (int(self.x), int(self.y)), 
                               (int(end_x), int(end_y)), 3)
                
        # Render bullets
        for bullet in self.bullets:
            bullet.render(screen)
            
    def get_rect(self) -> pygame.Rect:
        """Get player collision rectangle"""
        return self.rect