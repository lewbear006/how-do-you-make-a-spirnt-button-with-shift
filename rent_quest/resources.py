from __future__ import annotations

from functools import lru_cache
from typing import Tuple

import pygame

from . import settings


@lru_cache(maxsize=64)
def get_font(size: int) -> pygame.font.Font:
    return pygame.font.SysFont("arial", size)


@lru_cache(maxsize=256)
def get_placeholder_surface(size: Tuple[int, int], color: Tuple[int, int, int], label: str | None = None) -> pygame.Surface:
    surface = pygame.Surface(size, pygame.SRCALPHA)
    surface.fill(color)
    if label:
        font = get_font(14)
        text = font.render(label, True, settings.COLOR_WHITE)
        rect = text.get_rect(center=(size[0] // 2, size[1] // 2))
        surface.blit(text, rect)
    return surface

