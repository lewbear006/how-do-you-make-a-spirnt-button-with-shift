from __future__ import annotations

import pygame

from .. import settings
from ..resources import get_font
from ..scene import Scene


class PauseMenuScene(Scene):
    def __init__(self, manager) -> None:
        super().__init__(manager)
        self.title_font = get_font(36)
        self.menu_font = get_font(24)
        self.selection_index = 0
        self.options = ["Resume", "Main Menu"]

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_DOWN, pygame.K_s):
                self.selection_index = (self.selection_index + 1) % len(self.options)
            elif event.key in (pygame.K_UP, pygame.K_w):
                self.selection_index = (self.selection_index - 1) % len(self.options)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                self._activate_option()

    def _activate_option(self) -> None:
        choice = self.options[self.selection_index]
        if choice == "Resume":
            self.manager.pop()
        elif choice == "Main Menu":
            from .main_menu import MainMenuScene
            self.manager.switch(MainMenuScene(self.manager))

    def draw(self, surface: pygame.Surface) -> None:
        # Dim background
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        surface.blit(overlay, (0, 0))

        title = self.title_font.render("Paused", True, settings.COLOR_WHITE)
        title_rect = title.get_rect(center=(surface.get_width() // 2, 200))
        surface.blit(title, title_rect)

        for i, text in enumerate(self.options):
            color = settings.COLOR_GREEN if i == self.selection_index else settings.COLOR_WHITE
            item = self.menu_font.render(text, True, color)
            rect = item.get_rect(center=(surface.get_width() // 2, 260 + i * 36))
            surface.blit(item, rect)

