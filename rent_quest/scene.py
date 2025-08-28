from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

import pygame


class Scene:
    """Base class for all scenes.

    Scenes manage a part of the game flow (menus, gameplay, shops, dialogs).
    """

    def __init__(self, manager: "SceneManager") -> None:
        self.manager = manager

    def on_enter(self) -> None:
        pass

    def on_exit(self) -> None:
        pass

    def handle_event(self, event: pygame.event.Event) -> None:
        pass

    def update(self, dt: float) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        pass


class SceneManager:
    """Manages a stack of scenes. Only the top scene receives input and updates."""

    def __init__(self) -> None:
        self._stack: List[Scene] = []
        self._request_quit: bool = False

    @property
    def current(self) -> Optional[Scene]:
        return self._stack[-1] if self._stack else None

    @property
    def is_empty(self) -> bool:
        return not self._stack

    def request_quit(self) -> None:
        self._request_quit = True

    def should_quit(self) -> bool:
        return self._request_quit

    def push(self, scene: Scene) -> None:
        self._stack.append(scene)
        scene.on_enter()

    def pop(self) -> None:
        if self._stack:
            scene = self._stack.pop()
            scene.on_exit()

    def switch(self, scene: Scene) -> None:
        if self._stack:
            self._stack[-1].on_exit()
            self._stack[-1] = scene
            scene.on_enter()
        else:
            self.push(scene)

    def handle_event(self, event: pygame.event.Event) -> None:
        if self._stack:
            self._stack[-1].handle_event(event)

    def update(self, dt: float) -> None:
        if self._stack:
            self._stack[-1].update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        if self._stack:
            self._stack[-1].draw(surface)

