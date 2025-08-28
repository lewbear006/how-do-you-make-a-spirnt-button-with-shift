"""
Base Scene class for Rent Quest
All scenes inherit from this base class
"""

import pygame
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game.game_engine import GameEngine

class Scene(ABC):
    """Abstract base class for all game scenes"""
    
    def __init__(self, game_engine: 'GameEngine'):
        """Initialize the scene"""
        self.game_engine = game_engine
        self.name = self.__class__.__name__.lower().replace("scene", "")
        
    @abstractmethod
    def enter(self):
        """Called when entering this scene"""
        pass
        
    @abstractmethod
    def exit(self):
        """Called when exiting this scene"""
        pass
        
    @abstractmethod
    def handle_event(self, event: pygame.event.Event):
        """Handle pygame events"""
        pass
        
    @abstractmethod
    def update(self, dt: float):
        """Update scene logic"""
        pass
        
    @abstractmethod
    def render(self, screen: pygame.Surface):
        """Render the scene"""
        pass