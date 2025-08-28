import os


def main() -> None:
    # Allow users to set SDL_VIDEODRIVER externally for headless runs
    # e.g., SDL_VIDEODRIVER=dummy python run.py
    from rent_quest.game import Game
    game = Game()
    game.run()


if __name__ == "__main__":
    main()

