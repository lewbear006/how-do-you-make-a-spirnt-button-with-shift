"""
Rent System for Rent Quest
The core game mechanic - player must pay rent to survive
"""

import pygame
from typing import TYPE_CHECKING
from game.constants import *

if TYPE_CHECKING:
    from game.entities.player import Player

class RentSystem:
    """Manages rent payments and deadlines"""
    
    def __init__(self, player: 'Player'):
        """Initialize rent system"""
        self.player = player
        self.rent_amount = RENT_AMOUNT
        self.days_between_rent = RENT_DUE_DAYS
        self.seconds_per_day = SECONDS_PER_DAY
        
        # Time tracking
        self.game_time = 0.0  # Total game time in seconds
        self.current_day = 1
        self.days_until_rent = self.days_between_rent
        self.last_rent_payment = 0
        
        # Rent escalation
        self.rent_increases = 0
        self.rent_increase_rate = 1.2  # 20% increase each time
        
        # Consequences
        self.eviction_warnings = 0
        self.max_warnings = 3
        self.grace_period = 2  # Days after rent due
        self.is_evicted = False
        
        # UI notifications
        self.show_rent_due_warning = False
        self.show_eviction_warning = False
        self.warning_timer = 0.0
        
    def update(self, dt: float):
        """Update rent system"""
        self.game_time += dt
        
        # Calculate current day
        new_day = int(self.game_time // self.seconds_per_day) + 1
        if new_day > self.current_day:
            self._advance_day(new_day)
            
        # Update timers
        if self.warning_timer > 0:
            self.warning_timer -= dt
            
        # Check for rent due
        self.days_until_rent = self.days_between_rent - ((self.current_day - 1) % self.days_between_rent)
        
        # Check if rent is overdue
        if self.days_until_rent <= 0 and not self._rent_paid_this_period():
            self._handle_overdue_rent()
            
        # Show warnings
        if self.days_until_rent <= 2 and not self._rent_paid_this_period():
            self.show_rent_due_warning = True
        else:
            self.show_rent_due_warning = False
            
    def _advance_day(self, new_day: int):
        """Handle advancing to a new day"""
        self.current_day = new_day
        print(f"Day {self.current_day} begins!")
        
    def _rent_paid_this_period(self) -> bool:
        """Check if rent has been paid for this period"""
        current_period = (self.current_day - 1) // self.days_between_rent
        last_payment_period = (self.last_rent_payment - 1) // self.days_between_rent
        return current_period <= last_payment_period
        
    def _handle_overdue_rent(self):
        """Handle overdue rent consequences"""
        days_overdue = abs(self.days_until_rent)
        
        if days_overdue > self.grace_period:
            self.eviction_warnings += 1
            self.show_eviction_warning = True
            self.warning_timer = 5.0  # Show warning for 5 seconds
            
            if self.eviction_warnings >= self.max_warnings:
                self.is_evicted = True
                
    def attempt_rent_payment(self) -> bool:
        """Attempt to pay rent, returns True if successful"""
        if self.player.money >= self.rent_amount:
            if self.player.spend_money(self.rent_amount):
                self.last_rent_payment = self.current_day
                self.eviction_warnings = 0  # Reset warnings
                self.show_eviction_warning = False
                
                # Increase rent for next time
                self.rent_increases += 1
                self.rent_amount = int(RENT_AMOUNT * (self.rent_increase_rate ** self.rent_increases))
                
                print(f"Rent paid! Next rent: ${self.rent_amount}")
                return True
                
        return False
        
    def can_pay_rent(self) -> bool:
        """Check if player can afford rent"""
        return self.player.money >= self.rent_amount
        
    def get_time_until_rent(self) -> str:
        """Get formatted time until rent is due"""
        if self.days_until_rent > 0:
            return f"{self.days_until_rent} days"
        elif self.days_until_rent == 0:
            return "Today!"
        else:
            return f"{abs(self.days_until_rent)} days overdue!"
            
    def get_rent_status(self) -> dict:
        """Get complete rent status information"""
        return {
            "current_day": self.current_day,
            "rent_amount": self.rent_amount,
            "days_until_rent": self.days_until_rent,
            "time_until_rent": self.get_time_until_rent(),
            "can_pay": self.can_pay_rent(),
            "overdue": self.days_until_rent < 0,
            "eviction_warnings": self.eviction_warnings,
            "max_warnings": self.max_warnings,
            "is_evicted": self.is_evicted,
            "show_rent_due_warning": self.show_rent_due_warning,
            "show_eviction_warning": self.show_eviction_warning and self.warning_timer > 0
        }
        
    def render_notifications(self, screen: pygame.Surface):
        """Render rent-related notifications"""
        font_large = pygame.font.Font(None, FONT_SIZE_LARGE)
        font_medium = pygame.font.Font(None, FONT_SIZE_MEDIUM)
        
        # Rent due warning
        if self.show_rent_due_warning:
            warning_text = f"RENT DUE IN {self.days_until_rent} DAYS!"
            color = ORANGE if self.days_until_rent > 1 else RED
            
            text_surface = font_large.render(warning_text, True, color)
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, 150))
            
            # Background for visibility
            bg_rect = text_rect.inflate(20, 10)
            pygame.draw.rect(screen, BLACK, bg_rect)
            pygame.draw.rect(screen, color, bg_rect, 2)
            
            screen.blit(text_surface, text_rect)
            
            # Show rent amount
            rent_text = f"Amount Due: ${self.rent_amount}"
            rent_surface = font_medium.render(rent_text, True, WHITE)
            rent_rect = rent_surface.get_rect(center=(SCREEN_WIDTH // 2, 180))
            screen.blit(rent_surface, rent_rect)
            
        # Eviction warning
        if self.show_eviction_warning and self.warning_timer > 0:
            warning_text = f"EVICTION WARNING {self.eviction_warnings}/{self.max_warnings}!"
            
            text_surface = font_large.render(warning_text, True, RED)
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, 200))
            
            # Flashing background
            flash_alpha = int(128 + 127 * pygame.time.get_ticks() / 200)
            bg_color = (*RED, flash_alpha)
            bg_rect = text_rect.inflate(40, 20)
            
            # Create surface with alpha for flashing effect
            flash_surface = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
            flash_surface.fill((*RED, flash_alpha // 4))
            screen.blit(flash_surface, bg_rect)
            
            pygame.draw.rect(screen, RED, bg_rect, 3)
            screen.blit(text_surface, text_rect)
            
        # Game over screen
        if self.is_evicted:
            self._render_eviction_screen(screen)
            
    def _render_eviction_screen(self, screen: pygame.Surface):
        """Render game over screen due to eviction"""
        # Dark overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        # Game over text
        font_huge = pygame.font.Font(None, FONT_SIZE_HUGE)
        font_large = pygame.font.Font(None, FONT_SIZE_LARGE)
        font_medium = pygame.font.Font(None, FONT_SIZE_MEDIUM)
        
        game_over_text = font_huge.render("EVICTED!", True, RED)
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
        screen.blit(game_over_text, game_over_rect)
        
        # Explanation
        explanation = [
            "You failed to pay rent too many times.",
            "The landlord has evicted you from the building.",
            "Game Over!",
            "",
            "Press ESC to return to main menu"
        ]
        
        for i, line in enumerate(explanation):
            color = WHITE if line != "Game Over!" else RED
            font = font_medium if line != "Game Over!" else font_large
            
            text_surface = font.render(line, True, color)
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + i * 30))
            screen.blit(text_surface, text_rect)