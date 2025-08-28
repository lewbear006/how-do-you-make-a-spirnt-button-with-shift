from __future__ import annotations

import math
import pygame

from . import settings
from .resources import get_font


class HUD:
    def __init__(self) -> None:
        self.font_small = get_font(16)
        self.font_large = get_font(22)

    def draw_top_bar(self, surface: pygame.Surface, day: int, cash: int, rent_amount: int, rent_due_seconds: float) -> None:
        bar_rect = pygame.Rect(0, 0, surface.get_width(), 32)
        pygame.draw.rect(surface, (0, 0, 0, 0), bar_rect)

        # Left: Day and Cash
        left_text = self.font_large.render(f"Day {day}   $ {cash}", True, settings.COLOR_YELLOW)
        surface.blit(left_text, (12, 6))

        # Right: Rent timer and cost
        timer_seconds = int(math.ceil(rent_due_seconds))
        right_text = self.font_large.render(f"Rent: $ {rent_amount}  Due: {timer_seconds}s", True, settings.COLOR_WHITE)
        right_rect = right_text.get_rect(topright=(surface.get_width() - 12, 6))
        surface.blit(right_text, right_rect)

