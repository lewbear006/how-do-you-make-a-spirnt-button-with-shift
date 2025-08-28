"""
Dialogue Scene for Rent Quest
"""

import pygame
from typing import TYPE_CHECKING
from game.scenes.base_scene import Scene
from game.constants import *

if TYPE_CHECKING:
    from game.game_engine import GameEngine

class DialogueScene(Scene):
    """Dialogue scene for NPC conversations"""
    
    def __init__(self, game_engine: 'GameEngine'):
        super().__init__(game_engine)
        self.font = None
        
    def enter(self):
        """Initialize dialogue scene"""
        self.font = pygame.font.Font(None, FONT_SIZE_LARGE)
        
    def exit(self):
        """Clean up dialogue scene"""
        pass
        
    def handle_event(self, event: pygame.event.Event):
        """Handle dialogue events"""
        pass
        
    def update(self, dt: float):
        """Update dialogue logic"""
        pass
        
    def render(self, screen: pygame.Surface):
        """Render dialogue"""
        screen.fill(BACKGROUND_COLOR)
        
        text = self.font.render("DIALOGUE SCENE (Coming Soon)", True, WHITE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(text, text_rect)