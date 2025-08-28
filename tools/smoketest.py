import os


def main() -> None:
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("RQ_SMOKETEST_FRAMES", "10")

    from rent_quest.game import Game

    game = Game()
    game.run()
    print("SMOKETEST_OK")


if __name__ == "__main__":
    main()

