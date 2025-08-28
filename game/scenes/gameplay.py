"""
Gameplay Scene for Rent Quest - Main game world
"""

import pygame
from typing import TYPE_CHECKING, List
from game.scenes.base_scene import Scene
from game.constants import *
from game.entities.player import Player
from game.ui.hud import HUD
from game.systems.monster_spawner import MonsterSpawner
from game.systems.rent_system import RentSystem
from game.entities.npc import NPCManager
from game.systems.quest_system import QuestSystem

if TYPE_CHECKING:
    from game.game_engine import GameEngine

class GameplayScene(Scene):
    """Main gameplay scene with player and world"""
    
    def __init__(self, game_engine: 'GameEngine'):
        super().__init__(game_engine)
        self.font = None
        self.player = None
        self.hud = None
        self.monster_spawner = None
        self.rent_system = None
        self.npc_manager = None
        self.quest_system = None
        self.camera_x = 0
        self.camera_y = 0
        
    def enter(self):
        """Initialize gameplay scene"""
        self.font = pygame.font.Font(None, FONT_SIZE_LARGE)
        
        # Create player at center of screen
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        
        # Create monster spawner
        self.monster_spawner = MonsterSpawner()
        
        # Create rent system
        self.rent_system = RentSystem(self.player)
        
        # Create NPCs
        self.npc_manager = NPCManager()
        self.npc_manager.setup_default_npcs()
        
        # Create quest system
        self.quest_system = QuestSystem()
        
        # Create HUD
        self.hud = HUD(self.player, self.monster_spawner, self.rent_system)
        
        print("Entered gameplay scene")
        
    def exit(self):
        """Clean up gameplay scene"""
        print("Exited gameplay scene")
        
    def handle_event(self, event: pygame.event.Event):
        """Handle gameplay events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                self.game_engine.change_scene("main_menu")
            elif event.key == pygame.K_r and self.player.current_weapon:
                self.player.current_weapon.reload()
            elif event.key == pygame.K_p:  # Pay rent
                if self.rent_system:
                    self.rent_system.attempt_rent_payment()
            elif event.key == pygame.K_e:  # Interact with NPCs
                if self.npc_manager:
                    interaction = self.npc_manager.handle_interaction(self.player)
                    if interaction:
                        print(f"Talking to {interaction['npc_name']}: {interaction['dialogue']}")
                        # Special handling for shop NPCs
                        if interaction.get('npc_name') == 'Gunther':
                            self.game_engine.change_scene("shop")
                
        # Pass events to player
        if self.player:
            self.player.handle_event(event)
                
    def update(self, dt: float):
        """Update gameplay logic"""
        if self.player:
            self.player.update(dt, SCREEN_WIDTH, SCREEN_HEIGHT)
            
            # Update weapon
            if self.player.current_weapon:
                self.player.current_weapon.update(dt)
                
        # Update monster spawner
        if self.monster_spawner:
            # Count monsters before update for quest tracking
            monsters_before = len(self.monster_spawner.monsters)
            
            self.monster_spawner.update(dt, self.player, SCREEN_WIDTH, SCREEN_HEIGHT)
            
            # Handle bullet-monster collisions
            self.monster_spawner.handle_bullet_collisions(self.player.bullets)
            
            # Handle player-monster collisions
            self.monster_spawner.handle_player_collisions(self.player)
            
            # Track monster kills for quests
            monsters_after = len(self.monster_spawner.monsters)
            monsters_killed = monsters_before - monsters_after
            if monsters_killed > 0 and self.quest_system:
                self.quest_system.update_quest_progress("kill_monsters", monsters_killed)
            
        # Update rent system
        if self.rent_system:
            self.rent_system.update(dt)
            
            # Check for game over due to eviction
            if self.rent_system.is_evicted:
                # Player evicted - could transition to game over scene
                pass
                
        # Update NPCs
        if self.npc_manager:
            self.npc_manager.update(dt, self.player)
            
        # Update quest system
        if self.quest_system:
            # Track various quest objectives
            if hasattr(self, '_last_money'):
                money_earned = self.player.money - self._last_money
                if money_earned > 0:
                    self.quest_system.update_quest_progress("earn_money", money_earned)
            self._last_money = self.player.money
            
            # Track wave progression
            if self.monster_spawner:
                wave_info = self.monster_spawner.get_wave_info()
                if hasattr(self, '_last_wave'):
                    if wave_info['wave_number'] > self._last_wave:
                        self.quest_system.update_quest_progress("reach_wave", 1)
                self._last_wave = wave_info.get('wave_number', 1)
                
        if self.hud:
            self.hud.update(dt)
        
    def render(self, screen: pygame.Surface):
        """Render gameplay"""
        # Clear screen with game background
        screen.fill((20, 30, 20))  # Dark green background
        
        # Draw simple grid pattern for ground
        self._draw_background_pattern(screen)
        
        # Render NPCs
        if self.npc_manager:
            self.npc_manager.render(screen)
            
        # Render monsters
        if self.monster_spawner:
            self.monster_spawner.render(screen)
            
        # Render player
        if self.player:
            self.player.render(screen)
            
        # Render HUD
        if self.hud:
            self.hud.render(screen)
            
        # Render rent notifications
        if self.rent_system:
            self.rent_system.render_notifications(screen)
            
        # Instructions
        instruction_font = pygame.font.Font(None, FONT_SIZE_SMALL)
        instructions = [
            "WASD: Move",
            "Mouse/Space: Shoot",
            "R: Reload",
            "E: Interact",
            "P: Pay Rent",
            "M: Main Menu"
        ]
        
        for i, instruction in enumerate(instructions):
            text = instruction_font.render(instruction, True, WHITE)
            screen.blit(text, (10, 10 + i * 20))
            
    def _draw_background_pattern(self, screen: pygame.Surface):
        """Draw a simple grid pattern for the ground"""
        grid_size = 32
        grid_color = (30, 40, 30)
        
        # Draw vertical lines
        for x in range(0, SCREEN_WIDTH, grid_size):
            pygame.draw.line(screen, grid_color, (x, 0), (x, SCREEN_HEIGHT))
            
        # Draw horizontal lines
        for y in range(0, SCREEN_HEIGHT, grid_size):
            pygame.draw.line(screen, grid_color, (0, y), (SCREEN_WIDTH, y))