"""
Game Constants for Rent Quest
All constant values used throughout the game
"""

import pygame
from enum import Enum

# Screen dimensions
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# Colors (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
LIGHT_GRAY = (192, 192, 192)
BACKGROUND_COLOR = (32, 32, 48)  # Dark blue-gray
UI_COLOR = (48, 48, 64)
HEALTH_COLOR = (220, 20, 20)
MONEY_COLOR = (255, 215, 0)  # Gold
XP_COLOR = (0, 255, 128)

# Player constants
PLAYER_SPEED = 200  # pixels per second
PLAYER_MAX_HEALTH = 100
PLAYER_START_MONEY = 50
PLAYER_SIZE = 32

# Weapon constants
BULLET_SPEED = 400
BULLET_DAMAGE_BASE = 25
BULLET_SIZE = 4

# Monster constants
MONSTER_SPAWN_RATE = 2.0  # seconds between spawns
MONSTER_SPEED_BASE = 80
MONSTER_HEALTH_BASE = 50
MONSTER_DAMAGE_BASE = 10
MONSTER_MONEY_DROP_BASE = 10
MONSTER_SIZE = 24

# Rent system constants
RENT_AMOUNT = 500  # Base rent amount
RENT_DUE_DAYS = 7  # Days between rent payments
SECONDS_PER_DAY = 60  # Game time: 1 minute = 1 day

# UI constants
FONT_SIZE_SMALL = 16
FONT_SIZE_MEDIUM = 24
FONT_SIZE_LARGE = 32
FONT_SIZE_HUGE = 48

# Game states
class GameState(Enum):
    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    SHOP = "shop"
    DIALOGUE = "dialogue"
    GAME_OVER = "game_over"

# Weapon types
class WeaponType(Enum):
    PISTOL = "pistol"
    RIFLE = "rifle"
    SHOTGUN = "shotgun"
    SMG = "smg"
    SNIPER = "sniper"

# Monster types
class MonsterType(Enum):
    ZOMBIE = "zombie"
    GOBLIN = "goblin"
    ORC = "orc"
    SKELETON = "skeleton"
    BOSS_TROLL = "boss_troll"

# Directions
class Direction(Enum):
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"

# Input keys
MOVE_UP = pygame.K_w
MOVE_DOWN = pygame.K_s
MOVE_LEFT = pygame.K_a
MOVE_RIGHT = pygame.K_d
SHOOT = pygame.K_SPACE
INTERACT = pygame.K_e
INVENTORY = pygame.K_i
PAUSE = pygame.K_ESCAPE