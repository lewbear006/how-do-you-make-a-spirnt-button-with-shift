from __future__ import annotations

import json
import os
from dataclasses import dataclass, field, asdict
from typing import Dict, Any

from . import settings


SAVE_FILE_PATH = os.path.join(settings.SAVES_DIR, "slot1.json")


@dataclass
class GameState:
    day: int = 1
    cash: int = settings.STARTING_CASH
    rent_amount: int = settings.INITIAL_RENT
    rent_due_seconds_remaining: float = float(settings.RENT_DUE_SECONDS)
    rent_paid: bool = False
    story_stage: int = 0
    upgrades: Dict[str, int] = field(default_factory=dict)

    def tick(self, dt: float) -> None:
        if not self.rent_paid:
            self.rent_due_seconds_remaining = max(0.0, self.rent_due_seconds_remaining - dt)

    def can_pay_rent(self) -> bool:
        return not self.rent_paid and self.cash >= self.rent_amount

    def pay_rent(self) -> bool:
        if self.can_pay_rent():
            self.cash -= self.rent_amount
            self.rent_paid = True
            return True
        return False

    def next_day(self) -> None:
        self.day += 1
        self.rent_paid = False
        self.rent_amount = int(self.rent_amount * settings.RENT_INCREASE_RATE)
        self.rent_due_seconds_remaining = float(settings.RENT_DUE_SECONDS)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GameState":
        return cls(**data)

    def save(self) -> None:
        os.makedirs(settings.SAVES_DIR, exist_ok=True)
        with open(SAVE_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls) -> "GameState":
        if not os.path.exists(SAVE_FILE_PATH):
            return cls()
        try:
            with open(SAVE_FILE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            return cls.from_dict(data)
        except Exception:
            # Fallback to a fresh state on error
            return cls()

