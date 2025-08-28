"""
Monster Spawner System for Rent Quest
Handles spawning monsters around the player
"""

import pygame
import random
import math
from typing import List, TYPE_CHECKING
from game.constants import *
from game.entities.monster import Monster, Zombie, Goblin, Orc, Skeleton, BossTroll

if TYPE_CHECKING:
    from game.entities.player import Player

class MonsterSpawner:
    """Handles monster spawning logic"""
    
    def __init__(self):
        """Initialize monster spawner"""
        self.monsters: List[Monster] = []
        self.last_spawn_time = 0.0
        self.spawn_rate = MONSTER_SPAWN_RATE
        self.max_monsters = 15  # Maximum monsters on screen
        self.spawn_distance = 400  # Distance from player to spawn
        self.despawn_distance = 800  # Distance to despawn monsters
        
        # Wave system
        self.wave_number = 1
        self.monsters_killed_this_wave = 0
        self.monsters_needed_for_wave = 10
        
    def update(self, dt: float, player: 'Player', screen_width: int, screen_height: int):
        """Update monster spawner"""
        current_time = pygame.time.get_ticks() / 1000.0
        
        # Update existing monsters
        for monster in self.monsters[:]:  # Copy list to avoid modification issues
            monster.update(dt, player)
            
            # Remove dead monsters
            if monster.is_dead:
                self.monsters.remove(monster)
                self.monsters_killed_this_wave += 1
                player.add_money(monster.get_money_drop())
                player.add_experience(10)  # Base XP per monster
                
            # Remove monsters that are too far away
            elif self._get_distance_to_player(monster, player) > self.despawn_distance:
                self.monsters.remove(monster)
                
        # Check for wave completion
        if self.monsters_killed_this_wave >= self.monsters_needed_for_wave:
            self._advance_wave()
            
        # Spawn new monsters
        if (current_time - self.last_spawn_time >= self.spawn_rate and 
            len(self.monsters) < self.max_monsters):
            self._spawn_monster(player, screen_width, screen_height)
            self.last_spawn_time = current_time
            
    def _get_distance_to_player(self, monster: Monster, player: 'Player') -> float:
        """Calculate distance between monster and player"""
        dx = monster.x - player.x
        dy = monster.y - player.y
        return math.sqrt(dx**2 + dy**2)
        
    def _spawn_monster(self, player: 'Player', screen_width: int, screen_height: int):
        """Spawn a new monster"""
        # Choose spawn position around player
        angle = random.uniform(0, 2 * math.pi)
        spawn_x = player.x + math.cos(angle) * self.spawn_distance
        spawn_y = player.y + math.sin(angle) * self.spawn_distance
        
        # Keep spawn within reasonable bounds
        spawn_x = max(50, min(screen_width - 50, spawn_x))
        spawn_y = max(50, min(screen_height - 50, spawn_y))
        
        # Choose monster type based on wave
        monster = self._create_monster_for_wave(spawn_x, spawn_y)
        self.monsters.append(monster)
        
    def _create_monster_for_wave(self, x: float, y: float) -> Monster:
        """Create appropriate monster for current wave"""
        # Determine monster probabilities based on wave
        if self.wave_number == 1:
            # Only zombies and goblins
            if random.random() < 0.7:
                return Zombie(x, y)
            else:
                return Goblin(x, y)
        elif self.wave_number <= 3:
            # Add orcs
            rand = random.random()
            if rand < 0.4:
                return Zombie(x, y)
            elif rand < 0.7:
                return Goblin(x, y)
            else:
                return Orc(x, y)
        elif self.wave_number <= 5:
            # Add skeletons
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
            # Boss waves and mixed
            if self.wave_number % 5 == 0:  # Boss wave every 5th wave
                return BossTroll(x, y)
            else:
                # All monster types
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
        """Advance to the next wave"""
        self.wave_number += 1
        self.monsters_killed_this_wave = 0
        self.monsters_needed_for_wave = int(self.monsters_needed_for_wave * 1.2)
        
        # Increase difficulty
        self.spawn_rate = max(0.5, self.spawn_rate * 0.95)  # Spawn faster
        self.max_monsters = min(25, self.max_monsters + 1)  # More monsters
        
        print(f"Wave {self.wave_number} begins! Need to kill {self.monsters_needed_for_wave} monsters.")
        
    def handle_bullet_collisions(self, bullets: List) -> int:
        """Handle bullet-monster collisions, returns damage dealt"""
        total_damage = 0
        
        for bullet in bullets[:]:  # Copy to avoid modification issues
            for monster in self.monsters:
                if monster.is_dead:
                    continue
                    
                # Check collision
                if monster.get_rect().colliderect(bullet.get_rect()):
                    # Monster takes damage
                    if monster.take_damage(bullet.damage):
                        total_damage += bullet.damage
                    
                    # Remove bullet
                    if bullet in bullets:
                        bullets.remove(bullet)
                    break
                    
        return total_damage
        
    def handle_player_collisions(self, player: 'Player'):
        """Handle player-monster collisions"""
        player_rect = player.get_rect()
        
        for monster in self.monsters:
            if monster.is_dead:
                continue
                
            if monster.get_rect().colliderect(player_rect):
                # Push player away from monster
                dx = player.x - monster.x
                dy = player.y - monster.y
                distance = math.sqrt(dx**2 + dy**2)
                
                if distance > 0:
                    # Normalize and apply push
                    push_force = 50
                    player.x += (dx / distance) * push_force * 0.016  # Assuming 60 FPS
                    player.y += (dy / distance) * push_force * 0.016
                    
    def render(self, screen: pygame.Surface):
        """Render all monsters"""
        for monster in self.monsters:
            monster.render(screen)
            
    def get_wave_info(self) -> dict:
        """Get information about current wave"""
        return {
            "wave_number": self.wave_number,
            "monsters_killed": self.monsters_killed_this_wave,
            "monsters_needed": self.monsters_needed_for_wave,
            "active_monsters": len(self.monsters)
        }