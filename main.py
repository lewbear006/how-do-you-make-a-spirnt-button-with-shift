#!/usr/bin/env python3
"""
Rent Quest - A survival RPG where you must earn money to pay rent by hunting monsters
Main entry point for the game
"""

import pygame
import sys
import os
from game.game_engine import GameEngine

def main():
    """Main function to start the game"""
    try:
        # Initialize pygame
        pygame.init()
        
        # Create and run the game
        game = GameEngine()
        game.run()
        
    except KeyboardInterrupt:
        print("\nGame interrupted by user")
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up pygame
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()