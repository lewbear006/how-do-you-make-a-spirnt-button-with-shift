from __future__ import annotations

import math
import os
from typing import Optional

import pygame

from . import settings
from .utils import ensure_directory
from .scene import SceneManager
from .scenes.main_menu import MainMenuScene


class Game:
    """Main game application. Initializes pygame and runs the core loop.

    This scaffolding shows a moving rectangle and handles basic input so we
    can verify the window, timing, and event loop are healthy. Later tasks
    will replace this with the full scene system and gameplay.
    """

    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption(settings.WINDOW_TITLE)
        self.screen = pygame.display.set_mode((settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()

        # Ensure required directories exist
        ensure_directory(settings.SAVES_DIR)
        ensure_directory(settings.ASSETS_DIR)
        ensure_directory(settings.DATA_DIR)

        self.font = pygame.font.SysFont("arial", 18)
        self.running: bool = True
        self.elapsed_seconds: float = 0.0

        # Scene management
        self.scenes = SceneManager()
        self.scenes.push(MainMenuScene(self.scenes))

    def run(self) -> None:
        """Run the main loop. If RQ_SMOKETEST_FRAMES is set, limit frame count."""
        try:
            max_frames = int(os.environ.get("RQ_SMOKETEST_FRAMES", "0"))
        except ValueError:
            max_frames = 0

        frames = 0
        while self.running:
            dt = self.clock.tick(settings.FRAME_RATE) / 1000.0
            self._handle_events()
            self._update(dt)
            self._draw()
            frames += 1
            if max_frames > 0 and frames >= max_frames:
                self.running = False

        self._shutdown()

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            else:
                self.scenes.handle_event(event)

    def _update(self, dt: float) -> None:
        self.elapsed_seconds += dt
        self.scenes.update(dt)
        if self.scenes.should_quit() or self.scenes.is_empty:
            self.running = False

    def _draw(self) -> None:
        self.screen.fill(settings.COLOR_BG)
        self.scenes.draw(self.screen)
        pygame.display.flip()

    def _shutdown(self) -> None:
        pygame.quit()

