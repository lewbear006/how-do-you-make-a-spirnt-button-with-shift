"""
Main Game Engine for Rent Quest
Handles the core game loop, scene management, and window operations
"""

import pygame
import sys
from typing import Dict, Optional
from game.constants import *
from game.scenes.main_menu import MainMenuScene
from game.scenes.gameplay import GameplayScene
from game.scenes.shop import ShopScene
from game.scenes.dialogue import DialogueScene
from game.audio_manager import AudioManager

class GameEngine:
    """Core game engine that manages the main game loop and scenes"""
    
    def __init__(self):
        """Initialize the game engine"""
        # Initialize display
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Rent Quest - Survival RPG")
        
        # Set up game clock for FPS control
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Initialize audio manager
        self.audio_manager = AudioManager()
        
        # Scene management
        self.scenes: Dict[str, 'Scene'] = {}
        self.current_scene: Optional['Scene'] = None
        self.scene_transition_requested = False
        self.next_scene_name = ""
        
        # Initialize scenes
        self._initialize_scenes()
        
        # Start with main menu
        self.change_scene("main_menu")
        
    def _initialize_scenes(self):
        """Initialize all game scenes"""
        from game.scenes.main_menu import MainMenuScene
        from game.scenes.gameplay import GameplayScene
        from game.scenes.shop_scene import ShopScene
        from game.scenes.dialogue import DialogueScene
        
        self.scenes["main_menu"] = MainMenuScene(self)
        self.scenes["gameplay"] = GameplayScene(self)
        self.scenes["shop"] = ShopScene(self)
        self.scenes["dialogue"] = DialogueScene(self)
        
    def change_scene(self, scene_name: str):
        """Request a scene change"""
        if scene_name in self.scenes:
            self.scene_transition_requested = True
            self.next_scene_name = scene_name
        else:
            print(f"Warning: Scene '{scene_name}' not found!")
            
    def _handle_scene_transition(self):
        """Handle scene transitions"""
        if self.scene_transition_requested:
            # Exit current scene
            if self.current_scene:
                self.current_scene.exit()
                
            # Enter new scene
            self.current_scene = self.scenes[self.next_scene_name]
            self.current_scene.enter()
            
            # Reset transition flag
            self.scene_transition_requested = False
            self.next_scene_name = ""
            
    def handle_event(self, event):
        """Handle global events"""
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:  # Toggle fullscreen
                self._toggle_fullscreen()
            elif event.key == pygame.K_ESCAPE:
                if self.current_scene and hasattr(self.current_scene, 'name'):
                    if self.current_scene.name == "gameplay":
                        self.change_scene("main_menu")
                    elif self.current_scene.name == "main_menu":
                        self.running = False
                        
        # Pass event to current scene
        if self.current_scene:
            self.current_scene.handle_event(event)
            
    def _toggle_fullscreen(self):
        """Toggle between fullscreen and windowed mode"""
        if self.screen.get_flags() & pygame.FULLSCREEN:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        else:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            
    def update(self, dt: float):
        """Update game state"""
        # Handle scene transitions
        self._handle_scene_transition()
        
        # Update current scene
        if self.current_scene:
            self.current_scene.update(dt)
            
        # Update audio
        self.audio_manager.update()
        
    def render(self):
        """Render the game"""
        # Clear screen
        self.screen.fill(BACKGROUND_COLOR)
        
        # Render current scene
        if self.current_scene:
            self.current_scene.render(self.screen)
            
        # Update display
        pygame.display.flip()
        
    def run(self):
        """Main game loop"""
        print("Starting Rent Quest...")
        
        while self.running:
            # Calculate delta time
            dt = self.clock.tick(FPS) / 1000.0  # Convert to seconds
            
            # Handle events
            for event in pygame.event.get():
                self.handle_event(event)
                
            # Update game state
            self.update(dt)
            
            # Render
            self.render()
            
        print("Game ended.")