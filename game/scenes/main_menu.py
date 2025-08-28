"""
Main Menu Scene for Rent Quest
"""

import pygame
from typing import List, TYPE_CHECKING
from game.scenes.base_scene import Scene
from game.constants import *
from game.ui.button import Button

if TYPE_CHECKING:
    from game.game_engine import GameEngine

class MainMenuScene(Scene):
    """Main menu scene with game options"""
    
    def __init__(self, game_engine: 'GameEngine'):
        super().__init__(game_engine)
        self.font_title = None
        self.font_menu = None
        self.buttons: List[Button] = []
        self.selected_button = 0
        
    def enter(self):
        """Initialize menu when entering"""
        # Initialize fonts
        self.font_title = pygame.font.Font(None, FONT_SIZE_HUGE)
        self.font_menu = pygame.font.Font(None, FONT_SIZE_LARGE)
        
        # Create menu buttons
        button_width = 200
        button_height = 50
        button_x = SCREEN_WIDTH // 2 - button_width // 2
        start_y = SCREEN_HEIGHT // 2
        
        self.buttons = [
            Button(button_x, start_y, button_width, button_height, "New Game", self._start_new_game),
            Button(button_x, start_y + 70, button_width, button_height, "Continue", self._continue_game),
            Button(button_x, start_y + 140, button_width, button_height, "Options", self._show_options),
            Button(button_x, start_y + 210, button_width, button_height, "Quit", self._quit_game)
        ]
        
        # Check if save file exists for continue button
        self.buttons[1].enabled = False  # For now, disable continue
        
    def exit(self):
        """Clean up when exiting"""
        pass
        
    def handle_event(self, event: pygame.event.Event):
        """Handle menu events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_button = max(0, self.selected_button - 1)
            elif event.key == pygame.K_DOWN:
                self.selected_button = min(len(self.buttons) - 1, self.selected_button + 1)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                if self.buttons[self.selected_button].enabled:
                    self.buttons[self.selected_button].click()
                    
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                for button in self.buttons:
                    if button.rect.collidepoint(event.pos) and button.enabled:
                        button.click()
                        
        elif event.type == pygame.MOUSEMOTION:
            # Update selected button based on mouse position
            for i, button in enumerate(self.buttons):
                if button.rect.collidepoint(event.pos):
                    self.selected_button = i
                    
    def update(self, dt: float):
        """Update menu logic"""
        # Update button selection visuals
        for i, button in enumerate(self.buttons):
            button.is_selected = (i == self.selected_button)
            
    def render(self, screen: pygame.Surface):
        """Render the main menu"""
        # Clear background with gradient effect
        self._render_background(screen)
        
        # Render title
        title_text = self.font_title.render("RENT QUEST", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 150))
        screen.blit(title_text, title_rect)
        
        # Render subtitle
        subtitle_text = self.font_menu.render("Survive. Hunt. Pay Rent.", True, LIGHT_GRAY)
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, 200))
        screen.blit(subtitle_text, subtitle_rect)
        
        # Render buttons
        for button in self.buttons:
            button.render(screen)
            
        # Render controls hint
        controls_font = pygame.font.Font(None, FONT_SIZE_SMALL)
        controls_text = controls_font.render("Use ARROW KEYS and ENTER to navigate, or use MOUSE", True, GRAY)
        controls_rect = controls_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        screen.blit(controls_text, controls_rect)
        
    def _render_background(self, screen: pygame.Surface):
        """Render animated background"""
        # Simple animated background with moving particles
        import random
        import math
        
        # Static background
        screen.fill(BACKGROUND_COLOR)
        
        # Add some "stars" or particles
        for i in range(50):
            x = (i * 37 + pygame.time.get_ticks() // 50) % SCREEN_WIDTH
            y = (i * 73) % SCREEN_HEIGHT
            alpha = int(128 + 127 * math.sin(pygame.time.get_ticks() / 1000 + i))
            color = (*GRAY, alpha)
            
            # Create a surface for the particle with alpha
            particle_surf = pygame.Surface((2, 2), pygame.SRCALPHA)
            particle_surf.fill((*GRAY, alpha))
            screen.blit(particle_surf, (x, y))
            
    def _start_new_game(self):
        """Start a new game"""
        self.game_engine.change_scene("gameplay")
        
    def _continue_game(self):
        """Continue existing game"""
        # TODO: Implement save/load system
        self.game_engine.change_scene("gameplay")
        
    def _show_options(self):
        """Show options menu"""
        # TODO: Implement options menu
        pass
        
    def _quit_game(self):
        """Quit the game"""
        self.game_engine.running = False