import pygame, sys
from settings import WIDTH, HEIGHT, FPS, TITLE, BLACK

pygame.init()

class GameState:
    MAIN_MENU = 'main_menu'
    PLAYING   = 'playing'
    GAME_OVER = 'game_over'

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.state = GameState.PLAYING
        self.running = True

    def run(self):
        while self.running:
            self.dt = self.clock.tick(FPS) / 1000  # delta time in seconds
            self.handle_events()
            self.update()
            self.draw()
            pygame.display.flip()
        pygame.quit()
        sys.exit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self):
        if self.state == GameState.PLAYING:
            pass  # TODO: update game objects

    def draw(self):
        self.screen.fill(BLACK)
        if self.state == GameState.PLAYING:
            # For now just text in center
            self.draw_center_text("Kill monsters, pay rent!")

    def draw_center_text(self, text):
        font = pygame.font.SysFont(None, 36)
        surf = font.render(text, True, (255,255,255))
        rect = surf.get_rect(center=(WIDTH//2, HEIGHT//2))
        self.screen.blit(surf, rect)

if __name__ == "__main__":
    Game().run()