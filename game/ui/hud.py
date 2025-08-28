"""
HUD (Heads Up Display) for Rent Quest
Shows player stats, health, money, etc.
"""

import pygame
from typing import TYPE_CHECKING, Optional
from game.constants import *

if TYPE_CHECKING:
    from game.entities.player import Player
    from game.systems.monster_spawner import MonsterSpawner
    from game.systems.rent_system import RentSystem

class HUD:
    """Heads up display for gameplay"""
    
    def __init__(self, player: 'Player', monster_spawner: Optional['MonsterSpawner'] = None, 
                 rent_system: Optional['RentSystem'] = None):
        """Initialize HUD"""
        self.player = player
        self.monster_spawner = monster_spawner
        self.rent_system = rent_system
        self.font_small = pygame.font.Font(None, FONT_SIZE_SMALL)
        self.font_medium = pygame.font.Font(None, FONT_SIZE_MEDIUM)
        
    def update(self, dt: float):
        """Update HUD elements"""
        pass
        
    def render(self, screen: pygame.Surface):
        """Render the HUD"""
        self._render_health_bar(screen)
        self._render_money(screen)
        self._render_level(screen)
        self._render_weapon_info(screen)
        self._render_wave_info(screen)
        self._render_rent_info(screen)
        
    def _render_health_bar(self, screen: pygame.Surface):
        """Render player health bar"""
        bar_width = 200
        bar_height = 20
        bar_x = 20
        bar_y = SCREEN_HEIGHT - 80
        
        # Background
        pygame.draw.rect(screen, DARK_GRAY, (bar_x, bar_y, bar_width, bar_height))
        
        # Health fill
        health_percentage = self.player.health / self.player.max_health
        fill_width = int(bar_width * health_percentage)
        health_color = HEALTH_COLOR if health_percentage > 0.3 else RED
        pygame.draw.rect(screen, health_color, (bar_x, bar_y, fill_width, bar_height))
        
        # Border
        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 2)
        
        # Health text
        health_text = f"HP: {self.player.health}/{self.player.max_health}"
        text_surface = self.font_small.render(health_text, True, WHITE)
        screen.blit(text_surface, (bar_x, bar_y - 20))
        
    def _render_money(self, screen: pygame.Surface):
        """Render player money"""
        money_text = f"Money: ${self.player.money}"
        text_surface = self.font_medium.render(money_text, True, MONEY_COLOR)
        screen.blit(text_surface, (SCREEN_WIDTH - 200, 20))
        
    def _render_level(self, screen: pygame.Surface):
        """Render player level and experience"""
        level_text = f"Level: {self.player.level}"
        text_surface = self.font_medium.render(level_text, True, WHITE)
        screen.blit(text_surface, (SCREEN_WIDTH - 200, 50))
        
        # Experience bar
        bar_width = 150
        bar_height = 10
        bar_x = SCREEN_WIDTH - 200
        bar_y = 80
        
        # Background
        pygame.draw.rect(screen, DARK_GRAY, (bar_x, bar_y, bar_width, bar_height))
        
        # Experience fill
        xp_percentage = self.player.experience / self.player.experience_to_next_level
        fill_width = int(bar_width * xp_percentage)
        pygame.draw.rect(screen, XP_COLOR, (bar_x, bar_y, fill_width, bar_height))
        
        # Border
        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 1)
        
        # XP text
        xp_text = f"XP: {self.player.experience}/{self.player.experience_to_next_level}"
        text_surface = self.font_small.render(xp_text, True, WHITE)
        screen.blit(text_surface, (bar_x, bar_y + 15))
        
    def _render_weapon_info(self, screen: pygame.Surface):
        """Render current weapon information"""
        if not self.player.current_weapon:
            return
            
        weapon = self.player.current_weapon
        
        # Weapon name
        weapon_text = weapon.name
        text_surface = self.font_medium.render(weapon_text, True, WHITE)
        screen.blit(text_surface, (20, 20))
        
        # Ammo counter
        if weapon.magazine_size > 0:
            if weapon.is_reloading:
                ammo_text = "Reloading..."
                text_color = ORANGE
            else:
                ammo_text = f"Ammo: {weapon.current_ammo}/{weapon.magazine_size}"
                text_color = WHITE if weapon.current_ammo > 0 else RED
                
            text_surface = self.font_small.render(ammo_text, True, text_color)
            screen.blit(text_surface, (20, 50))
            
        # Weapon stats
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
        """Render wave information"""
        if not self.monster_spawner:
            return
            
        wave_info = self.monster_spawner.get_wave_info()
        
        # Wave number
        wave_text = f"Wave: {wave_info['wave_number']}"
        text_surface = self.font_medium.render(wave_text, True, WHITE)
        screen.blit(text_surface, (SCREEN_WIDTH // 2 - 100, 20))
        
        # Wave progress
        progress_text = f"Progress: {wave_info['monsters_killed']}/{wave_info['monsters_needed']}"
        text_surface = self.font_small.render(progress_text, True, LIGHT_GRAY)
        screen.blit(text_surface, (SCREEN_WIDTH // 2 - 100, 50))
        
        # Active monsters
        active_text = f"Active Monsters: {wave_info['active_monsters']}"
        text_surface = self.font_small.render(active_text, True, LIGHT_GRAY)
        screen.blit(text_surface, (SCREEN_WIDTH // 2 - 100, 70))
        
    def _render_rent_info(self, screen: pygame.Surface):
        """Render rent information"""
        if not self.rent_system:
            return
            
        rent_status = self.rent_system.get_rent_status()
        
        # Rent amount and deadline
        rent_text = f"Rent: ${rent_status['rent_amount']}"
        color = RED if not rent_status['can_pay'] else WHITE
        text_surface = self.font_medium.render(rent_text, True, color)
        screen.blit(text_surface, (SCREEN_WIDTH - 200, 100))
        
        # Time until rent
        time_text = f"Due: {rent_status['time_until_rent']}"
        color = RED if rent_status['overdue'] else (ORANGE if rent_status['days_until_rent'] <= 2 else WHITE)
        text_surface = self.font_small.render(time_text, True, color)
        screen.blit(text_surface, (SCREEN_WIDTH - 200, 130))
        
        # Day counter
        day_text = f"Day: {rent_status['current_day']}"
        text_surface = self.font_small.render(day_text, True, WHITE)
        screen.blit(text_surface, (SCREEN_WIDTH - 200, 150))
        
        # Payment instruction
        if rent_status['can_pay'] and rent_status['days_until_rent'] <= 2:
            instruction_text = "Press P to pay rent"
            text_surface = self.font_small.render(instruction_text, True, GREEN)
            screen.blit(text_surface, (SCREEN_WIDTH - 200, 170))