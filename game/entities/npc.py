"""
NPC (Non-Player Character) entities for Rent Quest
"""

import pygame
from typing import List, Dict, Any, Optional, TYPE_CHECKING
from game.constants import *

if TYPE_CHECKING:
    from game.entities.player import Player

class NPC:
    """Base NPC class"""
    
    def __init__(self, x: float, y: float, name: str, npc_type: str):
        """Initialize NPC"""
        self.x = x
        self.y = y
        self.name = name
        self.npc_type = npc_type
        
        # Visual properties
        self.size = 40
        self.color = GRAY
        self.rect = pygame.Rect(x - self.size//2, y - self.size//2, self.size, self.size)
        
        # Interaction
        self.interaction_range = 60.0
        self.is_interactable = True
        self.dialogue_lines: List[str] = []
        self.current_dialogue_index = 0
        
        # Quest/shop data
        self.has_quest = False
        self.quest_completed = False
        self.shop_items: List[Dict[str, Any]] = []
        
    def update(self, dt: float):
        """Update NPC"""
        pass
        
    def can_interact(self, player: 'Player') -> bool:
        """Check if player can interact with this NPC"""
        if not self.is_interactable:
            return False
            
        dx = player.x - self.x
        dy = player.y - self.y
        distance = (dx**2 + dy**2)**0.5
        return distance <= self.interaction_range
        
    def interact(self, player: 'Player') -> Dict[str, Any]:
        """Interact with the NPC, returns interaction data"""
        return {
            "type": "dialogue",
            "npc_name": self.name,
            "dialogue": self.get_current_dialogue(),
            "has_more": self.has_more_dialogue(),
            "shop_items": self.shop_items if self.npc_type == "shop" else None
        }
        
    def get_current_dialogue(self) -> str:
        """Get current dialogue line"""
        if self.dialogue_lines and self.current_dialogue_index < len(self.dialogue_lines):
            return self.dialogue_lines[self.current_dialogue_index]
        return "..."
        
    def advance_dialogue(self) -> bool:
        """Advance to next dialogue line, returns True if more dialogue available"""
        if self.current_dialogue_index < len(self.dialogue_lines) - 1:
            self.current_dialogue_index += 1
            return True
        return False
        
    def has_more_dialogue(self) -> bool:
        """Check if there's more dialogue"""
        return self.current_dialogue_index < len(self.dialogue_lines) - 1
        
    def reset_dialogue(self):
        """Reset dialogue to beginning"""
        self.current_dialogue_index = 0
        
    def render(self, screen: pygame.Surface):
        """Render the NPC"""
        # Draw NPC as a square
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, WHITE, self.rect, 2)
        
        # Draw name above NPC
        font = pygame.font.Font(None, FONT_SIZE_SMALL)
        name_surface = font.render(self.name, True, WHITE)
        name_rect = name_surface.get_rect(center=(self.x, self.y - self.size//2 - 15))
        screen.blit(name_surface, name_rect)
        
        # Draw interaction indicator
        if self.is_interactable:
            # Draw "E" to interact
            interact_surface = font.render("E", True, YELLOW)
            interact_rect = interact_surface.get_rect(center=(self.x, self.y + self.size//2 + 15))
            screen.blit(interact_surface, interact_rect)
            
    def get_rect(self) -> pygame.Rect:
        """Get NPC collision rectangle"""
        return self.rect

class Landlord(NPC):
    """Landlord NPC - handles rent collection and evictions"""
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y, "Mr. Thornwick", "landlord")
        self.color = (100, 50, 150)  # Purple
        
        self.dialogue_lines = [
            "Ah, tenant. I trust you have my rent money?",
            "This building doesn't pay for itself, you know.",
            "Late payments will not be tolerated.",
            "Pay up or pack up, as they say.",
            "The rent is due precisely on schedule."
        ]
        
    def interact(self, player: 'Player') -> Dict[str, Any]:
        """Special landlord interaction"""
        base_interaction = super().interact(player)
        
        # Add rent-specific dialogue based on player's status
        if hasattr(player, 'money'):
            if player.money < 500:  # Assuming base rent is 500
                self.dialogue_lines[0] = "I see you're short on funds. Find work, quickly."
            else:
                self.dialogue_lines[0] = "Good to see you have the means to pay."
                
        return base_interaction

class WeaponShopkeeper(NPC):
    """Weapon shop NPC - sells weapons and upgrades"""
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y, "Gunther", "shop")
        self.color = (150, 100, 50)  # Brown
        
        self.dialogue_lines = [
            "Welcome to Gunther's Gun Shop!",
            "Need something with a bit more firepower?",
            "All my weapons are guaranteed to kill... monsters.",
            "Upgrades available for existing weapons too.",
            "Stay armed, stay alive out there."
        ]
        
        # Shop inventory
        from game.weapons.rifle import AssaultRifle
        from game.weapons.shotgun import Shotgun
        from game.weapons.smg import SMG
        from game.weapons.sniper import SniperRifle
        
        self.shop_items = [
            {"type": "weapon", "item": AssaultRifle(), "price": 500},
            {"type": "weapon", "item": SMG(), "price": 400},
            {"type": "weapon", "item": Shotgun(), "price": 750},
            {"type": "weapon", "item": SniperRifle(), "price": 1200},
            {"type": "upgrade", "name": "Damage Upgrade", "price": 200},
            {"type": "upgrade", "name": "Fire Rate Upgrade", "price": 150},
            {"type": "upgrade", "name": "Magazine Upgrade", "price": 100}
        ]

class QuestGiver(NPC):
    """Generic quest giver NPC"""
    
    def __init__(self, x: float, y: float, name: str):
        super().__init__(x, y, name, "quest")
        self.color = (50, 150, 100)  # Green
        self.has_quest = True
        
        self.dialogue_lines = [
            f"Greetings, I am {name}.",
            "I have work for someone skilled with weapons.",
            "Clear out the monster nests, and I'll pay well.",
            "Every monster killed makes this place safer.",
            "Good hunting!"
        ]

class Merchant(NPC):
    """General merchant NPC - sells consumables and items"""
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y, "Bella", "shop")
        self.color = (150, 150, 50)  # Yellow-brown
        
        self.dialogue_lines = [
            "Welcome to my shop, traveler!",
            "I've got supplies for the monster hunting business.",
            "Health potions, armor, all sorts of useful things.",
            "Fair prices for quality goods!",
            "Come back anytime!"
        ]
        
        # TODO: Add consumable items
        self.shop_items = [
            {"type": "consumable", "name": "Health Potion", "price": 50, "effect": "heal_25"},
            {"type": "consumable", "name": "Energy Drink", "price": 30, "effect": "speed_boost"},
            {"type": "consumable", "name": "Lucky Charm", "price": 100, "effect": "money_bonus"}
        ]

class NPCManager:
    """Manages all NPCs in the game"""
    
    def __init__(self):
        """Initialize NPC manager"""
        self.npcs: List[NPC] = []
        self.active_interaction: Optional[NPC] = None
        
    def add_npc(self, npc: NPC):
        """Add an NPC to the manager"""
        self.npcs.append(npc)
        
    def setup_default_npcs(self):
        """Set up default NPCs for the game"""
        # Place NPCs around the edges of the screen
        self.add_npc(Landlord(100, 100))
        self.add_npc(WeaponShopkeeper(SCREEN_WIDTH - 100, 100))
        self.add_npc(QuestGiver(100, SCREEN_HEIGHT - 100, "Captain Hayes"))
        self.add_npc(Merchant(SCREEN_WIDTH - 100, SCREEN_HEIGHT - 100))
        
    def update(self, dt: float, player: 'Player'):
        """Update all NPCs"""
        for npc in self.npcs:
            npc.update(dt)
            
        # Check for interactions
        self.active_interaction = None
        for npc in self.npcs:
            if npc.can_interact(player):
                self.active_interaction = npc
                break
                
    def handle_interaction(self, player: 'Player') -> Optional[Dict[str, Any]]:
        """Handle NPC interaction"""
        if self.active_interaction:
            return self.active_interaction.interact(player)
        return None
        
    def render(self, screen: pygame.Surface):
        """Render all NPCs"""
        for npc in self.npcs:
            npc.render(screen)
            
        # Render interaction prompt
        if self.active_interaction:
            font = pygame.font.Font(None, FONT_SIZE_MEDIUM)
            prompt_text = f"Press E to talk to {self.active_interaction.name}"
            text_surface = font.render(prompt_text, True, YELLOW)
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
            
            # Background for visibility
            bg_rect = text_rect.inflate(20, 10)
            pygame.draw.rect(screen, BLACK, bg_rect)
            pygame.draw.rect(screen, YELLOW, bg_rect, 2)
            
            screen.blit(text_surface, text_rect)
            
    def get_npc_by_name(self, name: str) -> Optional[NPC]:
        """Get NPC by name"""
        for npc in self.npcs:
            if npc.name == name:
                return npc
        return None