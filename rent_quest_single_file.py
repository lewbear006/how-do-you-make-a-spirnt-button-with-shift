#!/usr/bin/env python3
"""
RENT QUEST - Complete Single-File Version
A survival RPG where you hunt monsters to pay rent

All game systems combined into one file for easy distribution and execution.
"""

import pygame
import sys
import math
import random
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Callable
from enum import Enum

# ============================================================================
# CONSTANTS AND ENUMS
# ============================================================================

# Screen dimensions
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# Colors (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
LIGHT_GRAY = (192, 192, 192)
BACKGROUND_COLOR = (32, 32, 48)
UI_COLOR = (48, 48, 64)
HEALTH_COLOR = (220, 20, 20)
MONEY_COLOR = (255, 215, 0)
XP_COLOR = (0, 255, 128)

# Player constants
PLAYER_SPEED = 200
PLAYER_MAX_HEALTH = 100
PLAYER_START_MONEY = 50
PLAYER_SIZE = 32

# Weapon constants
BULLET_SPEED = 400
BULLET_DAMAGE_BASE = 25
BULLET_SIZE = 4

# Monster constants
MONSTER_SPAWN_RATE = 2.0
MONSTER_SPEED_BASE = 80
MONSTER_HEALTH_BASE = 50
MONSTER_DAMAGE_BASE = 10
MONSTER_MONEY_DROP_BASE = 10
MONSTER_SIZE = 24

# Rent system constants
RENT_AMOUNT = 500
RENT_DUE_DAYS = 7
SECONDS_PER_DAY = 60

# UI constants
FONT_SIZE_SMALL = 16
FONT_SIZE_MEDIUM = 24
FONT_SIZE_LARGE = 32
FONT_SIZE_HUGE = 48

# Game states
class GameState(Enum):
    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    SHOP = "shop"
    DIALOGUE = "dialogue"
    GAME_OVER = "game_over"

# Weapon types
class WeaponType(Enum):
    PISTOL = "pistol"
    RIFLE = "rifle"
    SHOTGUN = "shotgun"
    SMG = "smg"
    SNIPER = "sniper"

# Monster types
class MonsterType(Enum):
    ZOMBIE = "zombie"
    GOBLIN = "goblin"
    ORC = "orc"
    SKELETON = "skeleton"
    BOSS_TROLL = "boss_troll"

# Directions
class Direction(Enum):
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"

# Input keys
MOVE_UP = pygame.K_w
MOVE_DOWN = pygame.K_s
MOVE_LEFT = pygame.K_a
MOVE_RIGHT = pygame.K_d
SHOOT = pygame.K_SPACE
INTERACT = pygame.K_e
INVENTORY = pygame.K_i
PAUSE = pygame.K_ESCAPE

# ============================================================================
# AUDIO MANAGER
# ============================================================================

class AudioManager:
    """Manages all audio for the game"""
    
    def __init__(self):
        """Initialize audio manager"""
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        self.sounds = {}
        self.music_volume = 0.7
        self.sfx_volume = 0.8
        self.current_music = None
        self._load_audio()
        
    def _load_audio(self):
        """Load all audio files"""
        try:
            self._create_beep_sound("button_click", 440, 0.1)
            self._create_beep_sound("gun_shot", 220, 0.05)
            self._create_beep_sound("monster_death", 110, 0.2)
            self._create_beep_sound("pickup", 880, 0.1)
        except Exception as e:
            print(f"Warning: Could not create audio: {e}")
            
    def _create_beep_sound(self, name: str, frequency: int, duration: float):
        """Create a simple beep sound"""
        try:
            import numpy as np
            sample_rate = 22050
            frames = int(duration * sample_rate)
            arr = np.zeros((frames, 2))
            
            for i in range(frames):
                wave = np.sin(2 * np.pi * frequency * i / sample_rate)
                envelope = 1.0
                if i < frames * 0.1:
                    envelope = i / (frames * 0.1)
                elif i > frames * 0.8:
                    envelope = (frames - i) / (frames * 0.2)
                arr[i] = [wave * envelope * 0.3, wave * envelope * 0.3]
                
            arr = (arr * 32767).astype(np.int16)
            sound = pygame.sndarray.make_sound(arr)
            self.sounds[name] = sound
        except ImportError:
            sound = pygame.mixer.Sound(buffer=b'\x00\x00' * 1024)
            self.sounds[name] = sound
        
    def play_sound(self, sound_name: str, volume: Optional[float] = None):
        """Play a sound effect"""
        if sound_name in self.sounds:
            sound = self.sounds[sound_name]
            if volume is not None:
                sound.set_volume(volume * self.sfx_volume)
            else:
                sound.set_volume(self.sfx_volume)
            sound.play()
            
    def update(self):
        """Update audio manager"""
        pass

# ============================================================================
# UI COMPONENTS
# ============================================================================

class Button:
    """A clickable button UI element"""
    
    def __init__(self, x: int, y: int, width: int, height: int, text: str, 
                 callback: Optional[Callable] = None, font_size: int = FONT_SIZE_MEDIUM):
        """Initialize button"""
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.font = pygame.font.Font(None, font_size)
        self.enabled = True
        self.is_selected = False
        self.is_pressed = False
        
    def handle_event(self, event: pygame.event.Event):
        """Handle button events"""
        if not self.enabled:
            return
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                self.is_pressed = True
                
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.is_pressed and self.rect.collidepoint(event.pos):
                self.click()
            self.is_pressed = False
            
    def click(self):
        """Handle button click"""
        if self.enabled and self.callback:
            self.callback()
            
    def render(self, screen: pygame.Surface):
        """Render the button"""
        if not self.enabled:
            bg_color = DARK_GRAY
            text_color = GRAY
            border_color = GRAY
        elif self.is_pressed:
            bg_color = GRAY
            text_color = WHITE
            border_color = WHITE
        elif self.is_selected:
            bg_color = UI_COLOR
            text_color = WHITE
            border_color = WHITE
        else:
            bg_color = UI_COLOR
            text_color = LIGHT_GRAY
            border_color = LIGHT_GRAY
            
        pygame.draw.rect(screen, bg_color, self.rect)
        pygame.draw.rect(screen, border_color, self.rect, 2)
        
        text_surface = self.font.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

# ============================================================================
# INVENTORY SYSTEM
# ============================================================================

class ItemType(Enum):
    WEAPON = "weapon"
    CONSUMABLE = "consumable"
    UPGRADE = "upgrade"
    QUEST_ITEM = "quest_item"

class Item:
    """Base item class"""
    
    def __init__(self, name: str, item_type: ItemType, description: str = "", 
                 value: int = 0, stackable: bool = False, max_stack: int = 1):
        self.name = name
        self.item_type = item_type
        self.description = description
        self.value = value
        self.stackable = stackable
        self.max_stack = max_stack
        
    def __str__(self):
        return self.name

class InventorySlot:
    """Represents a single inventory slot"""
    
    def __init__(self, item: Optional[Item] = None, quantity: int = 0):
        self.item = item
        self.quantity = quantity
        
    def is_empty(self) -> bool:
        return self.item is None or self.quantity <= 0

class Inventory:
    """Player inventory system"""
    
    def __init__(self, size: int = 30):
        self.size = size
        self.slots: List[InventorySlot] = [InventorySlot() for _ in range(size)]

# ============================================================================
# WEAPON SYSTEM
# ============================================================================

class Weapon(Item):
    """Base weapon class"""
    
    def __init__(self, name: str, weapon_type: WeaponType, damage: int, 
                 fire_rate: float, bullet_speed: float = 400, 
                 magazine_size: int = -1, reload_time: float = 0.0,
                 price: int = 100, description: str = ""):
        super().__init__(name, ItemType.WEAPON, description, price)
        
        self.weapon_type = weapon_type
        self.base_damage = damage
        self.damage = damage
        self.fire_rate = fire_rate
        self.bullet_speed = bullet_speed
        self.magazine_size = magazine_size
        self.reload_time = reload_time
        
        self.current_ammo = magazine_size if magazine_size > 0 else -1
        self.is_reloading = False
        self.reload_timer = 0.0
        
        self.damage_level = 1
        self.fire_rate_level = 1
        self.magazine_level = 1
        
    def update(self, dt: float):
        if self.is_reloading:
            self.reload_timer -= dt
            if self.reload_timer <= 0:
                self.is_reloading = False
                self.current_ammo = self.magazine_size
                
    def can_shoot(self) -> bool:
        if self.is_reloading:
            return False
        if self.magazine_size > 0 and self.current_ammo <= 0:
            return False
        return True
        
    def shoot(self) -> bool:
        if not self.can_shoot():
            return False
        if self.magazine_size > 0:
            self.current_ammo -= 1
        return True
        
    def reload(self):
        if self.magazine_size > 0 and not self.is_reloading and self.current_ammo < self.magazine_size:
            self.is_reloading = True
            self.reload_timer = self.reload_time
            
    def upgrade_damage(self) -> int:
        cost = self.damage_level * 100
        self.damage_level += 1
        self.damage = int(self.base_damage * (1 + (self.damage_level - 1) * 0.25))
        return cost
        
    def upgrade_fire_rate(self) -> int:
        cost = self.fire_rate_level * 75
        self.fire_rate_level += 1
        self.fire_rate = max(0.1, self.fire_rate * 0.9)
        return cost

class Pistol(Weapon):
    def __init__(self):
        super().__init__(
            name="Basic Pistol", weapon_type=WeaponType.PISTOL, damage=25,
            fire_rate=0.5, bullet_speed=400, magazine_size=12, reload_time=1.5,
            price=0, description="A reliable sidearm. Good for beginners."
        )

class AssaultRifle(Weapon):
    def __init__(self):
        super().__init__(
            name="Assault Rifle", weapon_type=WeaponType.RIFLE, damage=40,
            fire_rate=0.15, bullet_speed=500, magazine_size=30, reload_time=2.0,
            price=500, description="High damage automatic rifle. Good for sustained combat."
        )

class SMG(Weapon):
    def __init__(self):
        super().__init__(
            name="SMG", weapon_type=WeaponType.SMG, damage=18,
            fire_rate=0.08, bullet_speed=350, magazine_size=40, reload_time=1.8,
            price=400, description="High rate of fire weapon. Great for crowd control."
        )

class Shotgun(Weapon):
    def __init__(self):
        super().__init__(
            name="Combat Shotgun", weapon_type=WeaponType.SHOTGUN, damage=80,
            fire_rate=1.0, bullet_speed=350, magazine_size=8, reload_time=2.5,
            price=750, description="Devastating close-range weapon. Fires multiple pellets."
        )

class SniperRifle(Weapon):
    def __init__(self):
        super().__init__(
            name="Sniper Rifle", weapon_type=WeaponType.SNIPER, damage=150,
            fire_rate=2.0, bullet_speed=800, magazine_size=5, reload_time=3.0,
            price=1200, description="Extremely high damage precision weapon. One shot, one kill."
        )

# ============================================================================
# BULLET SYSTEM
# ============================================================================

class Bullet:
    """Bullet projectile class"""
    
    def __init__(self, x: float, y: float, dir_x: float, dir_y: float, 
                 damage: int, speed: float = BULLET_SPEED):
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
        self.x += self.dir_x * self.speed * dt
        self.y += self.dir_y * self.speed * dt
        self.rect.center = (int(self.x), int(self.y))
        
    def render(self, screen: pygame.Surface):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size // 2)
        
    def get_rect(self) -> pygame.Rect:
        return self.rect

# ============================================================================
# MONSTER SYSTEM
# ============================================================================

class Monster:
    """Base monster class"""
    
    def __init__(self, x: float, y: float, monster_type: MonsterType, 
                 health: int, damage: int, speed: float, money_drop: int):
        self.x = x
        self.y = y
        self.vel_x = 0.0
        self.vel_y = 0.0
        
        self.monster_type = monster_type
        self.max_health = health
        self.health = health
        self.damage = damage
        self.speed = speed
        self.money_drop = money_drop
        
        self.size = MONSTER_SIZE
        self.color = self._get_color_for_type()
        self.rect = pygame.Rect(x - self.size//2, y - self.size//2, self.size, self.size)
        
        self.target = None
        self.attack_range = 30.0
        self.attack_cooldown = 1.0
        self.last_attack_time = 0.0
        
        self.damage_flash_timer = 0.0
        self.is_dead = False
        
    def _get_color_for_type(self) -> tuple:
        color_map = {
            MonsterType.ZOMBIE: (100, 150, 100),
            MonsterType.GOBLIN: (150, 100, 100),
            MonsterType.ORC: (120, 120, 100),
            MonsterType.SKELETON: (200, 200, 200),
            MonsterType.BOSS_TROLL: (80, 50, 120),
        }
        return color_map.get(self.monster_type, GRAY)
        
    def update(self, dt: float, player):
        if self.is_dead:
            return
            
        self.target = player
        self._update_ai(dt)
        self._update_movement(dt)
        self._update_effects(dt)
        self._update_rect()
        
    def _update_ai(self, dt: float):
        if not self.target:
            return
            
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance <= self.attack_range:
            current_time = pygame.time.get_ticks() / 1000.0
            if current_time - self.last_attack_time >= self.attack_cooldown:
                self._attack_target()
                self.last_attack_time = current_time
        else:
            if distance > 0:
                self.vel_x = (dx / distance) * self.speed
                self.vel_y = (dy / distance) * self.speed
                
    def _update_movement(self, dt: float):
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt
        
    def _update_effects(self, dt: float):
        if self.damage_flash_timer > 0:
            self.damage_flash_timer -= dt
            
    def _update_rect(self):
        self.rect.center = (int(self.x), int(self.y))
        
    def _attack_target(self):
        if self.target:
            self.target.take_damage(self.damage)
            
    def take_damage(self, damage: int) -> bool:
        self.health -= damage
        self.damage_flash_timer = 0.1
        
        if self.health <= 0:
            self.health = 0
            self.is_dead = True
            return True
        return False
        
    def render(self, screen: pygame.Surface):
        if self.is_dead:
            return
            
        color = RED if self.damage_flash_timer > 0 else self.color
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.size // 2)
        
        if self.health < self.max_health:
            self._render_health_bar(screen)
            
    def _render_health_bar(self, screen: pygame.Surface):
        bar_width = self.size
        bar_height = 4
        bar_x = int(self.x - bar_width // 2)
        bar_y = int(self.y - self.size // 2 - 8)
        
        pygame.draw.rect(screen, DARK_GRAY, (bar_x, bar_y, bar_width, bar_height))
        
        health_percentage = self.health / self.max_health
        fill_width = int(bar_width * health_percentage)
        pygame.draw.rect(screen, HEALTH_COLOR, (bar_x, bar_y, fill_width, bar_height))
        
    def get_rect(self) -> pygame.Rect:
        return self.rect
        
    def get_money_drop(self) -> int:
        base_money = self.money_drop
        variation = random.randint(-2, 3)
        return max(1, base_money + variation)

class Zombie(Monster):
    def __init__(self, x: float, y: float):
        super().__init__(x, y, MonsterType.ZOMBIE, health=80, damage=15, speed=60, money_drop=12)

class Goblin(Monster):
    def __init__(self, x: float, y: float):
        super().__init__(x, y, MonsterType.GOBLIN, health=40, damage=8, speed=120, money_drop=8)

class Orc(Monster):
    def __init__(self, x: float, y: float):
        super().__init__(x, y, MonsterType.ORC, health=60, damage=12, speed=80, money_drop=15)

class Skeleton(Monster):
    def __init__(self, x: float, y: float):
        super().__init__(x, y, MonsterType.SKELETON, health=50, damage=10, speed=90, money_drop=10)

class BossTroll(Monster):
    def __init__(self, x: float, y: float):
        super().__init__(x, y, MonsterType.BOSS_TROLL, health=300, damage=25, speed=50, money_drop=100)
        self.size = MONSTER_SIZE * 2
        self.attack_range = 50.0

# ============================================================================
# PLAYER SYSTEM
# ============================================================================

class Player:
    """Player character class"""
    
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.vel_x = 0.0
        self.vel_y = 0.0
        
        self.size = PLAYER_SIZE
        self.color = BLUE
        self.rect = pygame.Rect(x - self.size//2, y - self.size//2, self.size, self.size)
        
        self.max_health = PLAYER_MAX_HEALTH
        self.health = self.max_health
        self.money = PLAYER_START_MONEY
        self.level = 1
        self.experience = 0
        self.experience_to_next_level = 100
        
        self.current_weapon: Optional[Weapon] = Pistol()
        self.bullets: List[Bullet] = []
        self.last_shot_time = 0.0
        
        self.inventory = Inventory()
        
        self.keys_pressed = set()
        self.mouse_pos = (0, 0)
        self.is_shooting = False
        
        self.damage_flash_timer = 0.0
        self.is_moving = False
        
    def update(self, dt: float, screen_width: int, screen_height: int):
        self._handle_movement(dt, screen_width, screen_height)
        self._handle_shooting(dt)
        self._update_bullets(dt, screen_width, screen_height)
        self._update_effects(dt)
        self._update_rect()
        
    def _handle_movement(self, dt: float, screen_width: int, screen_height: int):
        self.vel_x = 0.0
        self.vel_y = 0.0
        
        if MOVE_LEFT in self.keys_pressed:
            self.vel_x -= PLAYER_SPEED
        if MOVE_RIGHT in self.keys_pressed:
            self.vel_x += PLAYER_SPEED
        if MOVE_UP in self.keys_pressed:
            self.vel_y -= PLAYER_SPEED
        if MOVE_DOWN in self.keys_pressed:
            self.vel_y += PLAYER_SPEED
            
        if self.vel_x != 0 and self.vel_y != 0:
            length = math.sqrt(self.vel_x**2 + self.vel_y**2)
            self.vel_x = (self.vel_x / length) * PLAYER_SPEED
            self.vel_y = (self.vel_y / length) * PLAYER_SPEED
            
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt
        
        half_size = self.size // 2
        self.x = max(half_size, min(screen_width - half_size, self.x))
        self.y = max(half_size, min(screen_height - half_size, self.y))
        
        self.is_moving = (self.vel_x != 0 or self.vel_y != 0)
        
    def _handle_shooting(self, dt: float):
        current_time = pygame.time.get_ticks() / 1000.0
        
        if self.is_shooting and self.current_weapon:
            if current_time - self.last_shot_time >= self.current_weapon.fire_rate:
                self._shoot()
                self.last_shot_time = current_time
                
    def _shoot(self):
        if not self.current_weapon:
            return
            
        dx = self.mouse_pos[0] - self.x
        dy = self.mouse_pos[1] - self.y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 0:
            dir_x = dx / distance
            dir_y = dy / distance
            
            bullet = Bullet(
                self.x, self.y, dir_x, dir_y,
                self.current_weapon.damage,
                self.current_weapon.bullet_speed
            )
            self.bullets.append(bullet)
            
    def _update_bullets(self, dt: float, screen_width: int, screen_height: int):
        for bullet in self.bullets[:]:
            bullet.update(dt)
            
            if (bullet.x < 0 or bullet.x > screen_width or 
                bullet.y < 0 or bullet.y > screen_height):
                self.bullets.remove(bullet)
                
    def _update_effects(self, dt: float):
        if self.damage_flash_timer > 0:
            self.damage_flash_timer -= dt
            
    def _update_rect(self):
        self.rect.center = (int(self.x), int(self.y))
        
    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            self.keys_pressed.add(event.key)
            if event.key == SHOOT:
                self.is_shooting = True
                
        elif event.type == pygame.KEYUP:
            self.keys_pressed.discard(event.key)
            if event.key == SHOOT:
                self.is_shooting = False
                
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.is_shooting = True
                
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.is_shooting = False
                
        elif event.type == pygame.MOUSEMOTION:
            self.mouse_pos = event.pos
            
    def take_damage(self, damage: int):
        self.health -= damage
        self.damage_flash_timer = 0.2
        
        if self.health <= 0:
            self.health = 0
            return True
        return False
        
    def heal(self, amount: int):
        self.health = min(self.max_health, self.health + amount)
        
    def add_money(self, amount: int):
        self.money += amount
        
    def spend_money(self, amount: int) -> bool:
        if self.money >= amount:
            self.money -= amount
            return True
        return False
        
    def add_experience(self, amount: int):
        self.experience += amount
        
        while self.experience >= self.experience_to_next_level:
            self.experience -= self.experience_to_next_level
            self.level += 1
            self.experience_to_next_level = int(self.experience_to_next_level * 1.5)
            
            self.max_health += 10
            self.health = self.max_health
            
    def render(self, screen: pygame.Surface):
        color = RED if self.damage_flash_timer > 0 else self.color
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.size // 2)
        
        if self.current_weapon:
            dx = self.mouse_pos[0] - self.x
            dy = self.mouse_pos[1] - self.y
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance > 0:
                end_x = self.x + (dx / distance) * (self.size // 2 + 10)
                end_y = self.y + (dy / distance) * (self.size // 2 + 10)
                pygame.draw.line(screen, WHITE, (int(self.x), int(self.y)), 
                               (int(end_x), int(end_y)), 3)
                
        for bullet in self.bullets:
            bullet.render(screen)
            
    def get_rect(self) -> pygame.Rect:
        return self.rect

# ============================================================================
# MONSTER SPAWNER SYSTEM
# ============================================================================

class MonsterSpawner:
    """Handles monster spawning logic"""
    
    def __init__(self):
        self.monsters: List[Monster] = []
        self.last_spawn_time = 0.0
        self.spawn_rate = MONSTER_SPAWN_RATE
        self.max_monsters = 15
        self.spawn_distance = 400
        self.despawn_distance = 800
        
        self.wave_number = 1
        self.monsters_killed_this_wave = 0
        self.monsters_needed_for_wave = 10
        
    def update(self, dt: float, player, screen_width: int, screen_height: int):
        current_time = pygame.time.get_ticks() / 1000.0
        
        for monster in self.monsters[:]:
            monster.update(dt, player)
            
            if monster.is_dead:
                self.monsters.remove(monster)
                self.monsters_killed_this_wave += 1
                player.add_money(monster.get_money_drop())
                player.add_experience(10)
                
            elif self._get_distance_to_player(monster, player) > self.despawn_distance:
                self.monsters.remove(monster)
                
        if self.monsters_killed_this_wave >= self.monsters_needed_for_wave:
            self._advance_wave()
            
        if (current_time - self.last_spawn_time >= self.spawn_rate and 
            len(self.monsters) < self.max_monsters):
            self._spawn_monster(player, screen_width, screen_height)
            self.last_spawn_time = current_time
            
    def _get_distance_to_player(self, monster: Monster, player) -> float:
        dx = monster.x - player.x
        dy = monster.y - player.y
        return math.sqrt(dx**2 + dy**2)
        
    def _spawn_monster(self, player, screen_width: int, screen_height: int):
        angle = random.uniform(0, 2 * math.pi)
        spawn_x = player.x + math.cos(angle) * self.spawn_distance
        spawn_y = player.y + math.sin(angle) * self.spawn_distance
        
        spawn_x = max(50, min(screen_width - 50, spawn_x))
        spawn_y = max(50, min(screen_height - 50, spawn_y))
        
        monster = self._create_monster_for_wave(spawn_x, spawn_y)
        self.monsters.append(monster)
        
    def _create_monster_for_wave(self, x: float, y: float) -> Monster:
        if self.wave_number == 1:
            if random.random() < 0.7:
                return Zombie(x, y)
            else:
                return Goblin(x, y)
        elif self.wave_number <= 3:
            rand = random.random()
            if rand < 0.4:
                return Zombie(x, y)
            elif rand < 0.7:
                return Goblin(x, y)
            else:
                return Orc(x, y)
        elif self.wave_number <= 5:
            rand = random.random()
            if rand < 0.3:
                return Zombie(x, y)
            elif rand < 0.5:
                return Goblin(x, y)
            elif rand < 0.8:
                return Orc(x, y)
            else:
                return Skeleton(x, y)
        else:
            if self.wave_number % 5 == 0:
                return BossTroll(x, y)
            else:
                rand = random.random()
                if rand < 0.25:
                    return Zombie(x, y)
                elif rand < 0.45:
                    return Goblin(x, y)
                elif rand < 0.7:
                    return Orc(x, y)
                else:
                    return Skeleton(x, y)
                    
    def _advance_wave(self):
        self.wave_number += 1
        self.monsters_killed_this_wave = 0
        self.monsters_needed_for_wave = int(self.monsters_needed_for_wave * 1.2)
        
        self.spawn_rate = max(0.5, self.spawn_rate * 0.95)
        self.max_monsters = min(25, self.max_monsters + 1)
        
        print(f"Wave {self.wave_number} begins! Need to kill {self.monsters_needed_for_wave} monsters.")
        
    def handle_bullet_collisions(self, bullets: List) -> int:
        total_damage = 0
        
        for bullet in bullets[:]:
            for monster in self.monsters:
                if monster.is_dead:
                    continue
                    
                if monster.get_rect().colliderect(bullet.get_rect()):
                    if monster.take_damage(bullet.damage):
                        total_damage += bullet.damage
                    
                    if bullet in bullets:
                        bullets.remove(bullet)
                    break
                    
        return total_damage
        
    def handle_player_collisions(self, player):
        player_rect = player.get_rect()
        
        for monster in self.monsters:
            if monster.is_dead:
                continue
                
            if monster.get_rect().colliderect(player_rect):
                dx = player.x - monster.x
                dy = player.y - monster.y
                distance = math.sqrt(dx**2 + dy**2)
                
                if distance > 0:
                    push_force = 50
                    player.x += (dx / distance) * push_force * 0.016
                    player.y += (dy / distance) * push_force * 0.016
                    
    def render(self, screen: pygame.Surface):
        for monster in self.monsters:
            monster.render(screen)
            
    def get_wave_info(self) -> dict:
        return {
            "wave_number": self.wave_number,
            "monsters_killed": self.monsters_killed_this_wave,
            "monsters_needed": self.monsters_needed_for_wave,
            "active_monsters": len(self.monsters)
        }

# ============================================================================
# RENT SYSTEM
# ============================================================================

class RentSystem:
    """Manages rent payments and deadlines"""
    
    def __init__(self, player):
        self.player = player
        self.rent_amount = RENT_AMOUNT
        self.days_between_rent = RENT_DUE_DAYS
        self.seconds_per_day = SECONDS_PER_DAY
        
        self.game_time = 0.0
        self.current_day = 1
        self.days_until_rent = self.days_between_rent
        self.last_rent_payment = 0
        
        self.rent_increases = 0
        self.rent_increase_rate = 1.2
        
        self.eviction_warnings = 0
        self.max_warnings = 3
        self.grace_period = 2
        self.is_evicted = False
        
        self.show_rent_due_warning = False
        self.show_eviction_warning = False
        self.warning_timer = 0.0
        
    def update(self, dt: float):
        self.game_time += dt
        
        new_day = int(self.game_time // self.seconds_per_day) + 1
        if new_day > self.current_day:
            self._advance_day(new_day)
            
        if self.warning_timer > 0:
            self.warning_timer -= dt
            
        self.days_until_rent = self.days_between_rent - ((self.current_day - 1) % self.days_between_rent)
        
        if self.days_until_rent <= 0 and not self._rent_paid_this_period():
            self._handle_overdue_rent()
            
        if self.days_until_rent <= 2 and not self._rent_paid_this_period():
            self.show_rent_due_warning = True
        else:
            self.show_rent_due_warning = False
            
    def _advance_day(self, new_day: int):
        self.current_day = new_day
        print(f"Day {self.current_day} begins!")
        
    def _rent_paid_this_period(self) -> bool:
        current_period = (self.current_day - 1) // self.days_between_rent
        last_payment_period = (self.last_rent_payment - 1) // self.days_between_rent
        return current_period <= last_payment_period
        
    def _handle_overdue_rent(self):
        days_overdue = abs(self.days_until_rent)
        
        if days_overdue > self.grace_period:
            self.eviction_warnings += 1
            self.show_eviction_warning = True
            self.warning_timer = 5.0
            
            if self.eviction_warnings >= self.max_warnings:
                self.is_evicted = True
                
    def attempt_rent_payment(self) -> bool:
        if self.player.money >= self.rent_amount:
            if self.player.spend_money(self.rent_amount):
                self.last_rent_payment = self.current_day
                self.eviction_warnings = 0
                self.show_eviction_warning = False
                
                self.rent_increases += 1
                self.rent_amount = int(RENT_AMOUNT * (self.rent_increase_rate ** self.rent_increases))
                
                print(f"Rent paid! Next rent: ${self.rent_amount}")
                return True
                
        return False
        
    def can_pay_rent(self) -> bool:
        return self.player.money >= self.rent_amount
        
    def get_time_until_rent(self) -> str:
        if self.days_until_rent > 0:
            return f"{self.days_until_rent} days"
        elif self.days_until_rent == 0:
            return "Today!"
        else:
            return f"{abs(self.days_until_rent)} days overdue!"
            
    def get_rent_status(self) -> dict:
        return {
            "current_day": self.current_day,
            "rent_amount": self.rent_amount,
            "days_until_rent": self.days_until_rent,
            "time_until_rent": self.get_time_until_rent(),
            "can_pay": self.can_pay_rent(),
            "overdue": self.days_until_rent < 0,
            "eviction_warnings": self.eviction_warnings,
            "max_warnings": self.max_warnings,
            "is_evicted": self.is_evicted,
            "show_rent_due_warning": self.show_rent_due_warning,
            "show_eviction_warning": self.show_eviction_warning and self.warning_timer > 0
        }
        
    def render_notifications(self, screen: pygame.Surface):
        font_large = pygame.font.Font(None, FONT_SIZE_LARGE)
        font_medium = pygame.font.Font(None, FONT_SIZE_MEDIUM)
        
        if self.show_rent_due_warning:
            warning_text = f"RENT DUE IN {self.days_until_rent} DAYS!"
            color = ORANGE if self.days_until_rent > 1 else RED
            
            text_surface = font_large.render(warning_text, True, color)
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, 150))
            
            bg_rect = text_rect.inflate(20, 10)
            pygame.draw.rect(screen, BLACK, bg_rect)
            pygame.draw.rect(screen, color, bg_rect, 2)
            
            screen.blit(text_surface, text_rect)
            
            rent_text = f"Amount Due: ${self.rent_amount}"
            rent_surface = font_medium.render(rent_text, True, WHITE)
            rent_rect = rent_surface.get_rect(center=(SCREEN_WIDTH // 2, 180))
            screen.blit(rent_surface, rent_rect)
            
        if self.show_eviction_warning and self.warning_timer > 0:
            warning_text = f"EVICTION WARNING {self.eviction_warnings}/{self.max_warnings}!"
            
            text_surface = font_large.render(warning_text, True, RED)
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, 200))
            
            bg_rect = text_rect.inflate(40, 20)
            pygame.draw.rect(screen, RED, bg_rect, 3)
            screen.blit(text_surface, text_rect)
            
        if self.is_evicted:
            self._render_eviction_screen(screen)
            
    def _render_eviction_screen(self, screen: pygame.Surface):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        font_huge = pygame.font.Font(None, FONT_SIZE_HUGE)
        font_large = pygame.font.Font(None, FONT_SIZE_LARGE)
        font_medium = pygame.font.Font(None, FONT_SIZE_MEDIUM)
        
        game_over_text = font_huge.render("EVICTED!", True, RED)
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
        screen.blit(game_over_text, game_over_rect)
        
        explanation = [
            "You failed to pay rent too many times.",
            "The landlord has evicted you from the building.",
            "Game Over!",
            "",
            "Press ESC to return to main menu"
        ]
        
        for i, line in enumerate(explanation):
            color = WHITE if line != "Game Over!" else RED
            font = font_medium if line != "Game Over!" else font_large
            
            text_surface = font.render(line, True, color)
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + i * 30))
            screen.blit(text_surface, text_rect)

# ============================================================================
# QUEST SYSTEM
# ============================================================================

class QuestStatus(Enum):
    NOT_STARTED = "not_started"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"

class QuestObjective:
    def __init__(self, description: str, objective_type: str, target_value: int = 1):
        self.description = description
        self.objective_type = objective_type
        self.target_value = target_value
        self.current_value = 0
        self.completed = False
        
    def update_progress(self, amount: int = 1):
        self.current_value = min(self.target_value, self.current_value + amount)
        self.completed = self.current_value >= self.target_value

class Quest:
    def __init__(self, quest_id: str, title: str, description: str, 
                 money_reward: int = 0, xp_reward: int = 0):
        self.quest_id = quest_id
        self.title = title
        self.description = description
        self.money_reward = money_reward
        self.xp_reward = xp_reward
        self.status = QuestStatus.NOT_STARTED
        self.objectives: List[QuestObjective] = []
        
    def add_objective(self, objective: QuestObjective):
        self.objectives.append(objective)
        
    def update_objective(self, objective_type: str, amount: int = 1):
        for objective in self.objectives:
            if objective.objective_type == objective_type and not objective.completed:
                objective.update_progress(amount)
                
    def check_completion(self) -> bool:
        if self.status == QuestStatus.ACTIVE:
            all_completed = all(obj.completed for obj in self.objectives)
            if all_completed:
                self.status = QuestStatus.COMPLETED
                return True
        return False
        
    def start(self):
        if self.status == QuestStatus.NOT_STARTED:
            self.status = QuestStatus.ACTIVE
            
    def complete(self, player):
        if self.status == QuestStatus.COMPLETED:
            player.add_money(self.money_reward)
            player.add_experience(self.xp_reward)
            print(f"Quest completed: {self.title}")
            print(f"Rewards: ${self.money_reward}, {self.xp_reward} XP")

class QuestSystem:
    def __init__(self):
        self.quests: Dict[str, Quest] = {}
        self.active_quests: List[str] = []
        self.completed_quests: List[str] = []
        self._create_default_quests()
        
    def _create_default_quests(self):
        tutorial = Quest("tutorial", "First Day", 
                        "Learn the basics of survival and monster hunting.",
                        money_reward=50, xp_reward=25)
        tutorial.add_objective(QuestObjective("Kill 5 monsters", "kill_monsters", 5))
        tutorial.add_objective(QuestObjective("Earn $100", "earn_money", 100))
        self.quests["tutorial"] = tutorial
        
        rent_prep = Quest("rent_prep", "Rent Day Approaches", 
                         "Prepare for your first rent payment.",
                         money_reward=100, xp_reward=50)
        rent_prep.add_objective(QuestObjective("Earn $500 for rent", "earn_money", 500))
        rent_prep.add_objective(QuestObjective("Survive 5 days", "survive_days", 5))
        self.quests["rent_prep"] = rent_prep
        
        self.start_quest("tutorial")
        
    def start_quest(self, quest_id: str) -> bool:
        if quest_id in self.quests and quest_id not in self.active_quests:
            quest = self.quests[quest_id]
            quest.start()
            self.active_quests.append(quest_id)
            print(f"New quest started: {quest.title}")
            return True
        return False
        
    def update_quest_progress(self, objective_type: str, amount: int = 1):
        for quest_id in self.active_quests[:]:
            quest = self.quests[quest_id]
            quest.update_objective(objective_type, amount)
            
            if quest.check_completion():
                self._complete_quest(quest_id)
                
    def _complete_quest(self, quest_id: str):
        if quest_id in self.active_quests:
            quest = self.quests[quest_id]
            self.active_quests.remove(quest_id)
            self.completed_quests.append(quest_id)
            
            quest_chains = {
                "tutorial": "rent_prep"
            }
            
            if quest_id in quest_chains:
                next_quest = quest_chains[quest_id]
                self.start_quest(next_quest)

# ============================================================================
# HUD SYSTEM
# ============================================================================

class HUD:
    """Heads up display for gameplay"""
    
    def __init__(self, player, monster_spawner=None, rent_system=None):
        self.player = player
        self.monster_spawner = monster_spawner
        self.rent_system = rent_system
        self.font_small = pygame.font.Font(None, FONT_SIZE_SMALL)
        self.font_medium = pygame.font.Font(None, FONT_SIZE_MEDIUM)
        
    def update(self, dt: float):
        pass
        
    def render(self, screen: pygame.Surface):
        self._render_health_bar(screen)
        self._render_money(screen)
        self._render_level(screen)
        self._render_weapon_info(screen)
        self._render_wave_info(screen)
        self._render_rent_info(screen)
        
    def _render_health_bar(self, screen: pygame.Surface):
        bar_width = 200
        bar_height = 20
        bar_x = 20
        bar_y = SCREEN_HEIGHT - 80
        
        pygame.draw.rect(screen, DARK_GRAY, (bar_x, bar_y, bar_width, bar_height))
        
        health_percentage = self.player.health / self.player.max_health
        fill_width = int(bar_width * health_percentage)
        health_color = HEALTH_COLOR if health_percentage > 0.3 else RED
        pygame.draw.rect(screen, health_color, (bar_x, bar_y, fill_width, bar_height))
        
        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 2)
        
        health_text = f"HP: {self.player.health}/{self.player.max_health}"
        text_surface = self.font_small.render(health_text, True, WHITE)
        screen.blit(text_surface, (bar_x, bar_y - 20))
        
    def _render_money(self, screen: pygame.Surface):
        money_text = f"Money: ${self.player.money}"
        text_surface = self.font_medium.render(money_text, True, MONEY_COLOR)
        screen.blit(text_surface, (SCREEN_WIDTH - 200, 20))
        
    def _render_level(self, screen: pygame.Surface):
        level_text = f"Level: {self.player.level}"
        text_surface = self.font_medium.render(level_text, True, WHITE)
        screen.blit(text_surface, (SCREEN_WIDTH - 200, 50))
        
        bar_width = 150
        bar_height = 10
        bar_x = SCREEN_WIDTH - 200
        bar_y = 80
        
        pygame.draw.rect(screen, DARK_GRAY, (bar_x, bar_y, bar_width, bar_height))
        
        xp_percentage = self.player.experience / self.player.experience_to_next_level
        fill_width = int(bar_width * xp_percentage)
        pygame.draw.rect(screen, XP_COLOR, (bar_x, bar_y, fill_width, bar_height))
        
        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 1)
        
        xp_text = f"XP: {self.player.experience}/{self.player.experience_to_next_level}"
        text_surface = self.font_small.render(xp_text, True, WHITE)
        screen.blit(text_surface, (bar_x, bar_y + 15))
        
    def _render_weapon_info(self, screen: pygame.Surface):
        if not self.player.current_weapon:
            return
            
        weapon = self.player.current_weapon
        
        weapon_text = weapon.name
        text_surface = self.font_medium.render(weapon_text, True, WHITE)
        screen.blit(text_surface, (20, 20))
        
        if weapon.magazine_size > 0:
            if weapon.is_reloading:
                ammo_text = "Reloading..."
                text_color = ORANGE
            else:
                ammo_text = f"Ammo: {weapon.current_ammo}/{weapon.magazine_size}"
                text_color = WHITE if weapon.current_ammo > 0 else RED
                
            text_surface = self.font_small.render(ammo_text, True, text_color)
            screen.blit(text_surface, (20, 50))
            
        stats_y = 80
        stats = [
            f"Damage: {weapon.damage}",
            f"Fire Rate: {weapon.fire_rate_level}",
            f"Upgrades: D{weapon.damage_level} F{weapon.fire_rate_level} M{weapon.magazine_level}"
        ]
        
        for i, stat in enumerate(stats):
            text_surface = self.font_small.render(stat, True, LIGHT_GRAY)
            screen.blit(text_surface, (20, stats_y + i * 18))
            
    def _render_wave_info(self, screen: pygame.Surface):
        if not self.monster_spawner:
            return
            
        wave_info = self.monster_spawner.get_wave_info()
        
        wave_text = f"Wave: {wave_info['wave_number']}"
        text_surface = self.font_medium.render(wave_text, True, WHITE)
        screen.blit(text_surface, (SCREEN_WIDTH // 2 - 100, 20))
        
        progress_text = f"Progress: {wave_info['monsters_killed']}/{wave_info['monsters_needed']}"
        text_surface = self.font_small.render(progress_text, True, LIGHT_GRAY)
        screen.blit(text_surface, (SCREEN_WIDTH // 2 - 100, 50))
        
        active_text = f"Active Monsters: {wave_info['active_monsters']}"
        text_surface = self.font_small.render(active_text, True, LIGHT_GRAY)
        screen.blit(text_surface, (SCREEN_WIDTH // 2 - 100, 70))
        
    def _render_rent_info(self, screen: pygame.Surface):
        if not self.rent_system:
            return
            
        rent_status = self.rent_system.get_rent_status()
        
        rent_text = f"Rent: ${rent_status['rent_amount']}"
        color = RED if not rent_status['can_pay'] else WHITE
        text_surface = self.font_medium.render(rent_text, True, color)
        screen.blit(text_surface, (SCREEN_WIDTH - 200, 100))
        
        time_text = f"Due: {rent_status['time_until_rent']}"
        color = RED if rent_status['overdue'] else (ORANGE if rent_status['days_until_rent'] <= 2 else WHITE)
        text_surface = self.font_small.render(time_text, True, color)
        screen.blit(text_surface, (SCREEN_WIDTH - 200, 130))
        
        day_text = f"Day: {rent_status['current_day']}"
        text_surface = self.font_small.render(day_text, True, WHITE)
        screen.blit(text_surface, (SCREEN_WIDTH - 200, 150))
        
        if rent_status['can_pay'] and rent_status['days_until_rent'] <= 2:
            instruction_text = "Press P to pay rent"
            text_surface = self.font_small.render(instruction_text, True, GREEN)
            screen.blit(text_surface, (SCREEN_WIDTH - 200, 170))

# ============================================================================
# SCENES
# ============================================================================

class Scene(ABC):
    """Abstract base class for all game scenes"""
    
    def __init__(self, game_engine):
        self.game_engine = game_engine
        self.name = self.__class__.__name__.lower().replace("scene", "")
        
    @abstractmethod
    def enter(self):
        pass
        
    @abstractmethod
    def exit(self):
        pass
        
    @abstractmethod
    def handle_event(self, event: pygame.event.Event):
        pass
        
    @abstractmethod
    def update(self, dt: float):
        pass
        
    @abstractmethod
    def render(self, screen: pygame.Surface):
        pass

class MainMenuScene(Scene):
    """Main menu scene with game options"""
    
    def __init__(self, game_engine):
        super().__init__(game_engine)
        self.font_title = None
        self.font_menu = None
        self.buttons: List[Button] = []
        self.selected_button = 0
        
    def enter(self):
        self.font_title = pygame.font.Font(None, FONT_SIZE_HUGE)
        self.font_menu = pygame.font.Font(None, FONT_SIZE_LARGE)
        
        button_width = 200
        button_height = 50
        button_x = SCREEN_WIDTH // 2 - button_width // 2
        start_y = SCREEN_HEIGHT // 2
        
        self.buttons = [
            Button(button_x, start_y, button_width, button_height, "New Game", self._start_new_game),
            Button(button_x, start_y + 70, button_width, button_height, "Continue", self._continue_game),
            Button(button_x, start_y + 140, button_width, button_height, "Quit", self._quit_game)
        ]
        
        self.buttons[1].enabled = False  # Disable continue for now
        
    def exit(self):
        pass
        
    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_button = max(0, self.selected_button - 1)
            elif event.key == pygame.K_DOWN:
                self.selected_button = min(len(self.buttons) - 1, self.selected_button + 1)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                if self.buttons[self.selected_button].enabled:
                    self.buttons[self.selected_button].click()
                    
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                for button in self.buttons:
                    if button.rect.collidepoint(event.pos) and button.enabled:
                        button.click()
                        
        elif event.type == pygame.MOUSEMOTION:
            for i, button in enumerate(self.buttons):
                if button.rect.collidepoint(event.pos):
                    self.selected_button = i
                    
    def update(self, dt: float):
        for i, button in enumerate(self.buttons):
            button.is_selected = (i == self.selected_button)
            
    def render(self, screen: pygame.Surface):
        self._render_background(screen)
        
        title_text = self.font_title.render("RENT QUEST", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 150))
        screen.blit(title_text, title_rect)
        
        subtitle_text = self.font_menu.render("Survive. Hunt. Pay Rent.", True, LIGHT_GRAY)
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, 200))
        screen.blit(subtitle_text, subtitle_rect)
        
        for button in self.buttons:
            button.render(screen)
            
        controls_font = pygame.font.Font(None, FONT_SIZE_SMALL)
        controls_text = controls_font.render("Use ARROW KEYS and ENTER to navigate, or use MOUSE", True, GRAY)
        controls_rect = controls_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        screen.blit(controls_text, controls_rect)
        
    def _render_background(self, screen: pygame.Surface):
        screen.fill(BACKGROUND_COLOR)
        
        for i in range(50):
            x = (i * 37 + pygame.time.get_ticks() // 50) % SCREEN_WIDTH
            y = (i * 73) % SCREEN_HEIGHT
            alpha = int(128 + 127 * math.sin(pygame.time.get_ticks() / 1000 + i))
            
            particle_surf = pygame.Surface((2, 2), pygame.SRCALPHA)
            particle_surf.fill((*GRAY, alpha))
            screen.blit(particle_surf, (x, y))
            
    def _start_new_game(self):
        self.game_engine.change_scene("gameplay")
        
    def _continue_game(self):
        self.game_engine.change_scene("gameplay")
        
    def _quit_game(self):
        self.game_engine.running = False

class GameplayScene(Scene):
    """Main gameplay scene with player and world"""
    
    def __init__(self, game_engine):
        super().__init__(game_engine)
        self.font = None
        self.player = None
        self.hud = None
        self.monster_spawner = None
        self.rent_system = None
        self.quest_system = None
        
    def enter(self):
        self.font = pygame.font.Font(None, FONT_SIZE_LARGE)
        
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.monster_spawner = MonsterSpawner()
        self.rent_system = RentSystem(self.player)
        self.quest_system = QuestSystem()
        self.hud = HUD(self.player, self.monster_spawner, self.rent_system)
        
        print("Entered gameplay scene")
        
    def exit(self):
        print("Exited gameplay scene")
        
    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                self.game_engine.change_scene("main_menu")
            elif event.key == pygame.K_r and self.player.current_weapon:
                self.player.current_weapon.reload()
            elif event.key == pygame.K_p:
                if self.rent_system:
                    self.rent_system.attempt_rent_payment()
                
        if self.player:
            self.player.handle_event(event)
                
    def update(self, dt: float):
        if self.player:
            self.player.update(dt, SCREEN_WIDTH, SCREEN_HEIGHT)
            
            if self.player.current_weapon:
                self.player.current_weapon.update(dt)
                
        if self.monster_spawner:
            monsters_before = len(self.monster_spawner.monsters)
            
            self.monster_spawner.update(dt, self.player, SCREEN_WIDTH, SCREEN_HEIGHT)
            self.monster_spawner.handle_bullet_collisions(self.player.bullets)
            self.monster_spawner.handle_player_collisions(self.player)
            
            monsters_after = len(self.monster_spawner.monsters)
            monsters_killed = monsters_before - monsters_after
            if monsters_killed > 0 and self.quest_system:
                self.quest_system.update_quest_progress("kill_monsters", monsters_killed)
            
        if self.rent_system:
            self.rent_system.update(dt)
            
            if self.rent_system.is_evicted:
                pass
            
        if self.quest_system:
            if hasattr(self, '_last_money'):
                money_earned = self.player.money - self._last_money
                if money_earned > 0:
                    self.quest_system.update_quest_progress("earn_money", money_earned)
            self._last_money = self.player.money
                
        if self.hud:
            self.hud.update(dt)
        
    def render(self, screen: pygame.Surface):
        screen.fill((20, 30, 20))
        
        self._draw_background_pattern(screen)
        
        if self.monster_spawner:
            self.monster_spawner.render(screen)
            
        if self.player:
            self.player.render(screen)
            
        if self.hud:
            self.hud.render(screen)
            
        if self.rent_system:
            self.rent_system.render_notifications(screen)
            
        instruction_font = pygame.font.Font(None, FONT_SIZE_SMALL)
        instructions = [
            "WASD: Move",
            "Mouse/Space: Shoot",
            "R: Reload",
            "P: Pay Rent",
            "M: Main Menu"
        ]
        
        for i, instruction in enumerate(instructions):
            text = instruction_font.render(instruction, True, WHITE)
            screen.blit(text, (10, 10 + i * 20))
            
    def _draw_background_pattern(self, screen: pygame.Surface):
        grid_size = 32
        grid_color = (30, 40, 30)
        
        for x in range(0, SCREEN_WIDTH, grid_size):
            pygame.draw.line(screen, grid_color, (x, 0), (x, SCREEN_HEIGHT))
            
        for y in range(0, SCREEN_HEIGHT, grid_size):
            pygame.draw.line(screen, grid_color, (0, y), (SCREEN_WIDTH, y))

# ============================================================================
# GAME ENGINE
# ============================================================================

class GameEngine:
    """Core game engine that manages the main game loop and scenes"""
    
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Rent Quest - Survival RPG")
        
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.audio_manager = AudioManager()
        
        self.scenes: Dict[str, Scene] = {}
        self.current_scene: Optional[Scene] = None
        self.scene_transition_requested = False
        self.next_scene_name = ""
        
        self._initialize_scenes()
        self.change_scene("main_menu")
        
    def _initialize_scenes(self):
        self.scenes["main_menu"] = MainMenuScene(self)
        self.scenes["gameplay"] = GameplayScene(self)
        
    def change_scene(self, scene_name: str):
        if scene_name in self.scenes:
            self.scene_transition_requested = True
            self.next_scene_name = scene_name
        else:
            print(f"Warning: Scene '{scene_name}' not found!")
            
    def _handle_scene_transition(self):
        if self.scene_transition_requested:
            if self.current_scene:
                self.current_scene.exit()
                
            self.current_scene = self.scenes[self.next_scene_name]
            self.current_scene.enter()
            
            self.scene_transition_requested = False
            self.next_scene_name = ""
            
    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                self._toggle_fullscreen()
            elif event.key == pygame.K_ESCAPE:
                if self.current_scene and hasattr(self.current_scene, 'name'):
                    if self.current_scene.name == "gameplay":
                        self.change_scene("main_menu")
                    elif self.current_scene.name == "main_menu":
                        self.running = False
                        
        if self.current_scene:
            self.current_scene.handle_event(event)
            
    def _toggle_fullscreen(self):
        if self.screen.get_flags() & pygame.FULLSCREEN:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        else:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            
    def update(self, dt: float):
        self._handle_scene_transition()
        
        if self.current_scene:
            self.current_scene.update(dt)
            
        self.audio_manager.update()
        
    def render(self):
        self.screen.fill(BACKGROUND_COLOR)
        
        if self.current_scene:
            self.current_scene.render(self.screen)
            
        pygame.display.flip()
        
    def run(self):
        print("Starting Rent Quest...")
        
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            
            for event in pygame.event.get():
                self.handle_event(event)
                
            self.update(dt)
            self.render()
            
        print("Game ended.")

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main function to start the game"""
    print("=" * 50)
    print("RENT QUEST - Survival RPG")
    print("=" * 50)
    print()
    print("Game Overview:")
    print("- Hunt monsters to earn money")
    print("- Pay rent to avoid eviction")
    print("- Upgrade weapons and abilities")
    print("- Complete quests and survive waves")
    print()
    print("Controls:")
    print("- WASD: Move")
    print("- Mouse/Space: Shoot")
    print("- R: Reload")
    print("- P: Pay Rent")
    print("- E: Interact")
    print("- M: Main Menu")
    print("- F11: Fullscreen")
    print()
    
    try:
        pygame.init()
        game = GameEngine()
        game.run()
        
    except KeyboardInterrupt:
        print("\nGame interrupted by user")
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()
    finally:
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()