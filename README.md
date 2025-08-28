# Rent Quest - Survival RPG

A Python pygame-based survival RPG where the main objective is to earn money to pay rent by hunting monsters.

## Game Overview

In Rent Quest, you play as a tenant who must survive by hunting monsters to earn money for rent payments. The game combines survival mechanics, RPG progression, and the real-world pressure of paying rent on time.

## Features

### Core Gameplay
- **Monster Hunting**: Fight various types of monsters (zombies, goblins, orcs, skeletons, boss trolls)
- **Weapon System**: Multiple weapon types with different stats:
  - Pistol (starting weapon)
  - Assault Rifle (balanced)
  - SMG (high fire rate, low damage)
  - Shotgun (high damage, slow fire rate)
  - Sniper Rifle (very high damage, very slow fire rate)
- **Wave-based Combat**: Increasingly difficult monster waves
- **Money Economy**: Earn money by killing monsters, spend it on rent and upgrades

### Rent System
- **Rent Deadlines**: Must pay rent every 7 in-game days
- **Escalating Costs**: Rent increases after each payment
- **Consequences**: Eviction warnings and game over if rent is unpaid
- **Time Pressure**: Real-time day/night cycle (1 minute = 1 day)

### RPG Elements
- **Player Progression**: Level up by gaining experience
- **Weapon Upgrades**: Improve damage, fire rate, and magazine size
- **Player Upgrades**: Increase health and movement speed
- **Inventory System**: Manage weapons and items

### NPCs and Story
- **Landlord**: Mr. Thornwick - handles rent collection
- **Weapon Shop**: Gunther's Gun Shop - buy weapons and upgrades
- **Quest Givers**: Various NPCs with monster hunting contracts
- **Merchants**: General goods and consumables

### Quest System
- **Story Progression**: Multiple interconnected quests
- **Objectives**: Kill monsters, earn money, survive waves
- **Rewards**: Money and experience points

## Controls

- **WASD**: Movement
- **Mouse/Space**: Shoot
- **R**: Reload weapon
- **E**: Interact with NPCs
- **P**: Pay rent (when you have enough money)
- **M**: Return to main menu
- **ESC**: Pause/back

## Installation and Setup

### Prerequisites
- Python 3.7+
- pygame library

### Installation
1. Clone or download the game files
2. Install pygame:
   ```bash
   pip install pygame
   ```
   Or on Ubuntu/Debian:
   ```bash
   sudo apt install python3-pygame
   ```

### Running the Game
```bash
python3 main.py
```

## Game Architecture

### Project Structure
```
/workspace/
├── main.py                 # Game entry point
├── game/
│   ├── __init__.py
│   ├── constants.py        # Game constants and enums
│   ├── game_engine.py      # Core game engine
│   ├── audio_manager.py    # Audio system
│   ├── entities/           # Game entities
│   │   ├── player.py       # Player character
│   │   ├── monster.py      # Monster classes
│   │   ├── bullet.py       # Projectiles
│   │   └── npc.py          # Non-player characters
│   ├── scenes/             # Game scenes
│   │   ├── main_menu.py    # Main menu
│   │   ├── gameplay.py     # Main game scene
│   │   ├── shop_scene.py   # Weapon shop
│   │   └── dialogue.py     # NPC conversations
│   ├── systems/            # Game systems
│   │   ├── monster_spawner.py  # Monster spawning
│   │   ├── rent_system.py      # Rent mechanics
│   │   ├── inventory.py        # Item management
│   │   ├── upgrade_system.py   # Upgrades
│   │   └── quest_system.py     # Quest management
│   ├── weapons/            # Weapon classes
│   │   ├── weapon.py       # Base weapon class
│   │   ├── pistol.py       # Starting weapon
│   │   ├── rifle.py        # Assault rifle
│   │   ├── shotgun.py      # Shotgun
│   │   ├── smg.py          # Submachine gun
│   │   └── sniper.py       # Sniper rifle
│   └── ui/                 # User interface
│       ├── button.py       # UI buttons
│       └── hud.py          # Heads-up display
```

### Key Systems

1. **Game Engine**: Manages scenes, game loop, and window operations
2. **Monster Spawner**: Handles enemy spawning and wave progression
3. **Rent System**: Core game mechanic for rent payments and deadlines
4. **Weapon System**: Modular weapon classes with upgrade capabilities
5. **Quest System**: Story progression and objective tracking
6. **Audio Manager**: Sound effects and music management

## Gameplay Tips

1. **Money Management**: Always keep enough money for rent - it's your top priority
2. **Weapon Upgrades**: Invest in weapon improvements to handle stronger monsters
3. **Wave Progression**: Each wave brings more and tougher monsters
4. **NPC Interaction**: Talk to NPCs for quests and equipment
5. **Time Awareness**: Keep track of days until rent is due

## Technical Features

- **Modular Architecture**: Clean separation of systems and components
- **Scene Management**: Easy switching between game states
- **Collision Detection**: Efficient bullet-monster and player-monster collision
- **Wave System**: Dynamic difficulty scaling
- **Save System Ready**: Architecture supports save/load functionality
- **Expandable**: Easy to add new weapons, monsters, and features

## Future Enhancements

- **Save/Load System**: Persistent game progress
- **More Weapons**: Additional weapon types and special abilities
- **Boss Battles**: Unique boss monsters with special mechanics
- **Multiple Areas**: Different hunting grounds with unique monsters
- **Multiplayer**: Co-op monster hunting
- **Achievement System**: Unlockable achievements and rewards
- **Sound Effects**: Enhanced audio experience
- **Particle Effects**: Visual improvements and animations

## License

This project is open source and available for educational and personal use.

## Credits

Developed as a comprehensive pygame example demonstrating:
- Game architecture and design patterns
- Real-time gameplay mechanics
- RPG progression systems
- Economic simulation (rent pressure)
- Monster AI and combat systems