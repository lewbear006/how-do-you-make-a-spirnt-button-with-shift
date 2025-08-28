## Rent Quest: Pay The Rent

Top-down shooter built with pygame. The goal: earn cash by defeating monsters so you can pay your rent before the timer expires. Buy upgrades, talk to NPCs, and follow a short story centered on surviving your landlord.

### Quick Start

1. Create a virtual environment (optional but recommended)
2. Install dependencies
   - `pip install -r requirements.txt`
3. Run the game
   - `python run.py`

### Headless Smoketest (CI-friendly)

`SDL_VIDEODRIVER=dummy python tools/smoketest.py`

### Controls

- Move: WASD
- Aim: Mouse
- Shoot: Left Mouse Button
- Reload: R
- Interact: E
- Open Shop: Interact near the Shop NPC
- Go to Rent Office: Interact at the office door
- Pause: Esc

### Save/Load

Automatic save on quit and at key checkpoints. A `saves` folder will be created in the project root.

### Notes

This project is structured for clarity and extensibility. Art and audio are placeholders. You can replace them under `assets/`.
hey can i get some help on my code, i want to make it so when u press wasd u walk but when u hold shift and press wasd u run/sprint
