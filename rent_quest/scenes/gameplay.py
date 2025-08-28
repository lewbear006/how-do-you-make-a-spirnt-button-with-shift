from __future__ import annotations

import pygame

from .. import settings
from ..hud import HUD
from ..scene import Scene
from ..state import GameState


class GameplayScene(Scene):
    def __init__(self, manager, new_game: bool) -> None:
        super().__init__(manager)
        self.hud = HUD()
        self.state = GameState() if new_game else GameState.load()
        # Placeholder player rect
        self.player = pygame.Rect(settings.WINDOW_WIDTH // 2 - 16, settings.WINDOW_HEIGHT // 2 - 16, 32, 32)
        self.player_speed = settings.PLAYER_MOVE_SPEED

    def on_exit(self) -> None:
        self.state.save()

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            from .pause_menu import PauseMenuScene
            self.manager.push(PauseMenuScene(self.manager))

    def update(self, dt: float) -> None:
        keys = pygame.key.get_pressed()
        dx = (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_a] or keys[pygame.K_LEFT])
        dy = (keys[pygame.K_s] or keys[pygame.K_DOWN]) - (keys[pygame.K_w] or keys[pygame.K_UP])
        if dx:
            self.player.x += int(self.player_speed * dt * (1 if dx else -1)) if dx else 0
        if dy:
            self.player.y += int(self.player_speed * dt * (1 if dy else -1)) if dy else 0
        self.player.clamp_ip(pygame.Rect(0, 32, settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT - 32))

        self.state.tick(dt)

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill((25, 30, 36))
        pygame.draw.rect(surface, (60, 160, 240), self.player)
        self.hud.draw_top_bar(surface, self.state.day, self.state.cash, self.state.rent_amount, self.state.rent_due_seconds_remaining)

