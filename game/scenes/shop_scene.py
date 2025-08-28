"""
Enhanced Shop Scene for Rent Quest
Full weapon shop with upgrades and purchases
"""

import pygame
from typing import List, Dict, Any, Optional, TYPE_CHECKING
from game.scenes.base_scene import Scene
from game.constants import *
from game.ui.button import Button
from game.systems.upgrade_system import UpgradeSystem
from game.weapons.rifle import AssaultRifle
from game.weapons.shotgun import Shotgun
from game.weapons.smg import SMG
from game.weapons.sniper import SniperRifle

if TYPE_CHECKING:
    from game.game_engine import GameEngine
    from game.entities.player import Player

class ShopScene(Scene):
    """Enhanced shop scene for buying weapons and upgrades"""
    
    def __init__(self, game_engine: 'GameEngine'):
        super().__init__(game_engine)
        self.font_large = None
        self.font_medium = None
        self.font_small = None
        self.player: Optional['Player'] = None
        self.upgrade_system = UpgradeSystem()
        
        # Shop categories
        self.current_category = "weapons"  # weapons, upgrades, consumables
        self.category_buttons: List[Button] = []
        self.item_buttons: List[Button] = []
        
        # Shop inventory
        self.weapons_for_sale = [
            {"weapon": AssaultRifle(), "price": 500},
            {"weapon": SMG(), "price": 400},
            {"weapon": Shotgun(), "price": 750},
            {"weapon": SniperRifle(), "price": 1200}
        ]
        
        self.selected_item_index = 0
        
    def enter(self):
        """Initialize shop scene"""
        self.font_large = pygame.font.Font(None, FONT_SIZE_LARGE)
        self.font_medium = pygame.font.Font(None, FONT_SIZE_MEDIUM)
        self.font_small = pygame.font.Font(None, FONT_SIZE_SMALL)
        
        # Get player reference from gameplay scene
        gameplay_scene = self.game_engine.scenes.get("gameplay")
        if gameplay_scene and hasattr(gameplay_scene, 'player'):
            self.player = gameplay_scene.player
            
        self._setup_ui()
        
    def exit(self):
        """Clean up shop scene"""
        pass
        
    def _setup_ui(self):
        """Set up shop UI elements"""
        # Category buttons
        button_width = 150
        button_height = 40
        button_y = 100
        
        self.category_buttons = [
            Button(50, button_y, button_width, button_height, "Weapons", 
                   lambda: self._set_category("weapons")),
            Button(220, button_y, button_width, button_height, "Upgrades", 
                   lambda: self._set_category("upgrades")),
            Button(390, button_y, button_width, button_height, "Player", 
                   lambda: self._set_category("player"))
        ]
        
        self._setup_item_buttons()
        
    def _set_category(self, category: str):
        """Set the current shop category"""
        self.current_category = category
        self.selected_item_index = 0
        self._setup_item_buttons()
        
    def _setup_item_buttons(self):
        """Set up buttons for current category"""
        self.item_buttons = []
        button_width = 400
        button_height = 60
        start_y = 180
        
        if self.current_category == "weapons":
            for i, weapon_data in enumerate(self.weapons_for_sale):
                weapon = weapon_data["weapon"]
                price = weapon_data["price"]
                text = f"{weapon.name} - ${price}"
                
                button = Button(50, start_y + i * 70, button_width, button_height, text,
                              lambda idx=i: self._buy_weapon(idx))
                self.item_buttons.append(button)
                
        elif self.current_category == "upgrades" and self.player and self.player.current_weapon:
            upgrades = self.upgrade_system.get_all_weapon_upgrades(self.player.current_weapon)
            for i, (upgrade_type, upgrade_info) in enumerate(upgrades.items()):
                text = f"{upgrade_info['description']} - ${upgrade_info['cost']}"
                
                button = Button(50, start_y + i * 70, button_width, button_height, text,
                              lambda utype=upgrade_type: self._buy_upgrade(utype))
                self.item_buttons.append(button)
                
        elif self.current_category == "player" and self.player:
            player_upgrades = self.upgrade_system.get_all_player_upgrades(self.player)
            for i, (upgrade_type, upgrade_info) in enumerate(player_upgrades.items()):
                text = f"{upgrade_info['description']} - ${upgrade_info['cost']}"
                
                button = Button(50, start_y + i * 70, button_width, button_height, text,
                              lambda utype=upgrade_type: self._buy_player_upgrade(utype))
                self.item_buttons.append(button)
                
    def _buy_weapon(self, weapon_index: int):
        """Buy a weapon"""
        if not self.player or weapon_index >= len(self.weapons_for_sale):
            return
            
        weapon_data = self.weapons_for_sale[weapon_index]
        price = weapon_data["price"]
        
        if self.player.spend_money(price):
            # Give player the weapon
            self.player.current_weapon = weapon_data["weapon"]
            print(f"Purchased {weapon_data['weapon'].name}!")
        else:
            print("Not enough money!")
            
    def _buy_upgrade(self, upgrade_type: str):
        """Buy a weapon upgrade"""
        if not self.player or not self.player.current_weapon:
            return
            
        weapon = self.player.current_weapon
        
        if upgrade_type == "damage":
            if self.upgrade_system.upgrade_weapon_damage(weapon, self.player):
                print("Weapon damage upgraded!")
            else:
                print("Not enough money!")
        elif upgrade_type == "fire_rate":
            if self.upgrade_system.upgrade_weapon_fire_rate(weapon, self.player):
                print("Weapon fire rate upgraded!")
            else:
                print("Not enough money!")
        elif upgrade_type == "magazine":
            if self.upgrade_system.upgrade_weapon_magazine(weapon, self.player):
                print("Magazine size upgraded!")
            else:
                print("Not enough money!")
                
        # Refresh buttons to show new prices
        self._setup_item_buttons()
        
    def _buy_player_upgrade(self, upgrade_type: str):
        """Buy a player upgrade"""
        if not self.player:
            return
            
        if upgrade_type == "player_health":
            if self.upgrade_system.upgrade_player_health(self.player):
                print("Health upgraded!")
            else:
                print("Not enough money!")
        elif upgrade_type == "player_speed":
            if self.upgrade_system.upgrade_player_speed(self.player):
                print("Speed upgraded!")
            else:
                print("Not enough money!")
                
        # Refresh buttons to show new prices
        self._setup_item_buttons()
        
    def handle_event(self, event: pygame.event.Event):
        """Handle shop events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_m:
                self.game_engine.change_scene("gameplay")
                
        # Handle button events
        for button in self.category_buttons + self.item_buttons:
            button.handle_event(event)
            
    def update(self, dt: float):
        """Update shop logic"""
        pass
        
    def render(self, screen: pygame.Surface):
        """Render the shop"""
        screen.fill(BACKGROUND_COLOR)
        
        # Shop title
        title_text = self.font_large.render("Gunther's Gun Shop", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 50))
        screen.blit(title_text, title_rect)
        
        # Player money
        if self.player:
            money_text = self.font_medium.render(f"Money: ${self.player.money}", True, MONEY_COLOR)
            screen.blit(money_text, (SCREEN_WIDTH - 200, 20))
            
        # Category buttons
        for button in self.category_buttons:
            button.is_selected = (button.text.lower() == self.current_category)
            button.render(screen)
            
        # Category title
        category_title = self.current_category.title()
        if self.current_category == "upgrades" and self.player and self.player.current_weapon:
            category_title += f" - {self.player.current_weapon.name}"
        elif self.current_category == "upgrades":
            category_title += " - No Weapon Selected"
            
        category_text = self.font_medium.render(category_title, True, WHITE)
        screen.blit(category_text, (50, 150))
        
        # Item buttons
        for button in self.item_buttons:
            # Check if player can afford this item
            if self.player:
                # Extract price from button text
                try:
                    price_str = button.text.split("$")[-1]
                    price = int(price_str)
                    button.enabled = self.player.money >= price
                except:
                    button.enabled = True
            button.render(screen)
            
        # Instructions
        instruction_text = self.font_small.render("ESC: Return to Game", True, GRAY)
        screen.blit(instruction_text, (50, SCREEN_HEIGHT - 50))
        
        # Weapon info (if applicable)
        if self.current_category == "weapons" and self.selected_item_index < len(self.weapons_for_sale):
            self._render_weapon_info(screen, self.selected_item_index)
            
    def _render_weapon_info(self, screen: pygame.Surface, weapon_index: int):
        """Render detailed weapon information"""
        weapon = self.weapons_for_sale[weapon_index]["weapon"]
        
        info_x = 500
        info_y = 200
        
        # Weapon stats
        stats = [
            f"Damage: {weapon.damage}",
            f"Fire Rate: {round(1.0 / weapon.fire_rate, 1)} shots/sec",
            f"Magazine: {weapon.magazine_size if weapon.magazine_size > 0 else 'Unlimited'}",
            f"Reload Time: {weapon.reload_time}s",
            "",
            weapon.description
        ]
        
        for i, stat in enumerate(stats):
            color = WHITE if stat else WHITE
            text_surface = self.font_small.render(stat, True, color)
            screen.blit(text_surface, (info_x, info_y + i * 20))