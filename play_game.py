#!/usr/bin/env python3
"""
Rent Quest - Game Launcher
Comprehensive survival RPG where you hunt monsters to pay rent
"""

import sys
import os

def check_requirements():
    """Check if all requirements are met"""
    try:
        import pygame
        print("✓ Pygame is installed")
        return True
    except ImportError:
        print("✗ Pygame is not installed")
        print("Please install pygame:")
        print("  pip install pygame")
        print("  OR")
        print("  sudo apt install python3-pygame")
        return False

def main():
    """Main launcher function"""
    print("=" * 50)
    print("RENT QUEST - Survival RPG")
    print("=" * 50)
    print()
    print("Game Overview:")
    print("- Hunt monsters to earn money")
    print("- Pay rent to avoid eviction")
    print("- Upgrade weapons and abilities")
    print("- Complete quests and survive waves")
    print()
    
    if not check_requirements():
        print("\nCannot start game due to missing requirements.")
        return
        
    print("Starting game...")
    print()
    
    # Import and run the game
    try:
        from main import main as game_main
        game_main()
    except Exception as e:
        print(f"Error starting game: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()