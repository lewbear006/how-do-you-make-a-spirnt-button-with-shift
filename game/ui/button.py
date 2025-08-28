"""
Button UI component for Rent Quest
"""

import pygame
from typing import Callable, Optional
from game.constants import *

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
        # Choose colors based on state
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
            
        # Draw button background
        pygame.draw.rect(screen, bg_color, self.rect)
        pygame.draw.rect(screen, border_color, self.rect, 2)
        
        # Draw button text
        text_surface = self.font.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)