"""Pay The Rent – a mini action-RPG made entirely in one file.
Run `python pay_the_rent.py` after installing pygame (pip install pygame).
This is a heavily-simplified, placeholder-art version that still demonstrates:
• Twin-stick style movement + shooting
• Monsters that drop cash
• Basic upgrades shop (damage / fire-rate / speed)
• NPC dialogue system
• Recurring rent due every N in-game days
The goal: keep paying rent as difficulty ramps up.  Have fun!
"""
from __future__ import annotations
import pygame, sys, math, random, json, os

# -----------------------------------------------------------------------------
# SETTINGS
# -----------------------------------------------------------------------------
WIDTH, HEIGHT = 960, 640
FPS = 60
TITLE = "Pay The Rent"
TILE = 32

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY  = (60, 60, 60)
GREEN = (0, 200, 0)
RED   = (200, 0, 0)
BLUE  = (40, 120, 255)
YELLOW= (255, 255, 0)

FONT_NAME = pygame.font.get_default_font()

# Game balance constants
PLAYER_MAX_HP = 100
BULLET_SPEED  = 600
ENEMY_HP      = 40
ENEMY_DMG     = 10
ENEMY_SPEED   = 80
CASH_PER_KILL = 20
BASE_RENT     = 200
RENT_INTERVAL_SEC = 120  # every 2 minutes
SHOP_ITEMS = {
    "Damage +1"   : (100, "dmg"),
    "FireRate +10%": (120, "firerate"),
    "Speed +10%"   : (120, "speed"),
    "MaxHP +20"    : (150, "maxhp"),
}
SAVE_FILE = "rent_save.json"

# -----------------------------------------------------------------------------
# HELPERS
# -----------------------------------------------------------------------------

def vec_from_angle(angle: float) -> pygame.Vector2:
    return pygame.Vector2(math.cos(angle), math.sin(angle))

def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)

# -----------------------------------------------------------------------------
# CORE SPRITES
# -----------------------------------------------------------------------------
class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, vel, dmg, *groups):
        super().__init__(*groups)
        self.image = pygame.Surface((6, 2))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect(center=pos)
        self.vel  = vel
        self.dmg  = dmg
    def update(self, dt, game):
        self.rect.centerx += self.vel.x * dt
        self.rect.centery += self.vel.y * dt
        if not game.screen.get_rect().colliderect(self.rect):
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, *groups):
        super().__init__(*groups)
        self.image = pygame.Surface((TILE, TILE))
        self.image.fill(RED)
        self.rect = self.image.get_rect(center=pos)
        self.hp   = ENEMY_HP
    def hit(self, dmg):
        self.hp -= dmg
        if self.hp <= 0:
            self.kill()
    def update(self, dt, game):
        # simple chase AI
        direction = pygame.Vector2(game.player.rect.center) - self.rect.center
        if direction.length_squared():
            direction = direction.normalize()
            self.rect.centerx += direction.x * ENEMY_SPEED * dt
            self.rect.centery += direction.y * ENEMY_SPEED * dt
        # attack if touching
        if self.rect.colliderect(game.player.rect):
            game.player.take_damage(ENEMY_DMG * dt)

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, *groups):
        super().__init__(*groups)
        self.base_image = pygame.Surface((TILE, TILE))
        self.base_image.fill(BLUE)
        self.image = self.base_image.copy()
        self.rect  = self.image.get_rect(center=pos)
        self.vel = pygame.Vector2(0,0)
        # stats
        self.max_hp = PLAYER_MAX_HP
        self.hp     = PLAYER_MAX_HP
        self.move_speed = 180
        self.damage     = 10
        self.fire_rate  = 6  # bullets per second
        self.last_shot  = 0
    def input(self, keys):
        self.vel.xy = 0,0
        if keys[pygame.K_w]: self.vel.y = -1
        if keys[pygame.K_s]: self.vel.y =  1
        if keys[pygame.K_a]: self.vel.x = -1
        if keys[pygame.K_d]: self.vel.x =  1
        if self.vel.length_squared():
            self.vel = self.vel.normalize() * self.move_speed
    def update(self, dt, game):
        keys = pygame.key.get_pressed()
        self.input(keys)
        self.rect.centerx += self.vel.x * dt
        self.rect.centery += self.vel.y * dt
        # clamp to screen
        self.rect.left   = clamp(self.rect.left, 0, WIDTH - self.rect.width)
        self.rect.top    = clamp(self.rect.top,  0, HEIGHT - self.rect.height)
        # shooting
        self.last_shot += dt
        if pygame.mouse.get_pressed()[0] and self.last_shot >= 1/self.fire_rate:
            self.last_shot = 0
            mx, my = pygame.mouse.get_pos()
            dir_v = pygame.Vector2(mx - self.rect.centerx, my - self.rect.centery)
            if dir_v.length_squared():
                dir_v = dir_v.normalize()
                vel = dir_v * BULLET_SPEED
                Bullet(self.rect.center, vel, self.damage, game.all_sprites, game.bullets)
    def draw_hp(self, surf):
        ratio = self.hp / self.max_hp
        pygame.draw.rect(surf, RED, (self.rect.left, self.rect.top-8, self.rect.width,4))
        pygame.draw.rect(surf, GREEN,(self.rect.left, self.rect.top-8, self.rect.width*ratio,4))
    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0
            # For simplicity, instant game over
            pygame.event.post(pygame.event.Event(pygame.USEREVENT, {"custom":"player_dead"}))

# -----------------------------------------------------------------------------
# NPC & Dialogue
# -----------------------------------------------------------------------------
class NPC(pygame.sprite.Sprite):
    def __init__(self, pos, text, shop=False, *groups):
        super().__init__(*groups)
        self.image = pygame.Surface((TILE, TILE))
        self.image.fill(GREEN if shop else GREY)
        self.rect = self.image.get_rect(center=pos)
        self.text = text
        self.shop = shop
    def interact(self, game):
        if self.shop:
            game.open_shop()
        else:
            game.dialogue = self.text

# -----------------------------------------------------------------------------
# GAME CLASS
# -----------------------------------------------------------------------------
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        # sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.enemies     = pygame.sprite.Group()
        self.bullets     = pygame.sprite.Group()
        self.npcs        = pygame.sprite.Group()
        # player
        self.player = Player((WIDTH//2, HEIGHT//2), self.all_sprites)
        # landlord & shopkeeper
        landlord = NPC((WIDTH//2, 60), "Don't forget – rent is due soon!", False, self.all_sprites, self.npcs)
        shopkeep = NPC((100, HEIGHT-60), "Need an upgrade?", True, self.all_sprites, self.npcs)
        # HUD & dialogue
        self.dialogue = ""
        # economy
        self.cash   = 100
        self.rent_due = BASE_RENT
        self.next_rent_timer = RENT_INTERVAL_SEC
        # spawning
        self.spawn_cd = 0
        # shop state
        self.shop_open = False
        # load
        self.load()
    # ------------- SAVE / LOAD -------------
    def save(self):
        data = {
            "cash": self.cash,
            "rent_due": self.rent_due,
            "player_stats": {
                "max_hp": self.player.max_hp,
                "damage": self.player.damage,
                "fire_rate": self.player.fire_rate,
                "move_speed": self.player.move_speed
            }
        }
        with open(SAVE_FILE, 'w') as f:
            json.dump(data, f)
    def load(self):
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE) as f:
                    data = json.load(f)
                self.cash      = data.get("cash", self.cash)
                self.rent_due  = data.get("rent_due", self.rent_due)
                stats = data.get("player_stats", {})
                self.player.max_hp   = stats.get("max_hp", self.player.max_hp)
                self.player.damage   = stats.get("damage", self.player.damage)
                self.player.fire_rate= stats.get("fire_rate", self.player.fire_rate)
                self.player.move_speed=stats.get("move_speed", self.player.move_speed)
            except Exception:
                print("Save file corrupt – starting fresh")
    # ------------- SHOP -------------
    def open_shop(self):
        self.shop_open = True
    def buy_item(self, item_name, cost, effect):
        if self.cash >= cost:
            self.cash -= cost
            if effect == "dmg":
                self.player.damage += 1
            elif effect == "firerate":
                self.player.fire_rate *= 1.1
            elif effect == "speed":
                self.player.move_speed *= 1.1
            elif effect == "maxhp":
                self.player.max_hp += 20
                self.player.hp += 20
    # ------------- MAIN LOOP -------------
    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000
            self.handle_events()
            self.update(dt)
            self.draw()
            pygame.display.flip()
    # ------------- EVENTS -------------
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.save(); pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if self.shop_open:
                    self.shop_open = False
                else:
                    self.save(); pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # interaction
                if self.shop_open:
                    self.handle_shop_click(event.pos)
                else:
                    for npc in self.npcs:
                        if npc.rect.collidepoint(event.pos):
                            npc.interact(self)
            if event.type == pygame.USEREVENT and event.dict.get("custom") == "player_dead":
                self.game_over()
    # ------------- UPDATE -------------
    def update(self, dt):
        if self.shop_open:
            # freeze world
            pass
        else:
            self.all_sprites.update(dt, self)
            # bullets vs enemies
            hits = pygame.sprite.groupcollide(self.enemies, self.bullets, False, True)
            for enemy, bullets in hits.items():
                for b in bullets:
                    enemy.hit(b.dmg)
                if not enemy.alive():
                    self.cash += CASH_PER_KILL
            # spawn logic
            self.spawn_cd -= dt
            if self.spawn_cd <= 0:
                self.spawn_cd = random.uniform(1,3)
                side = random.choice(["top","bottom","left","right"])
                if side == "top":
                    pos = (random.randint(0,WIDTH), -TILE)
                elif side == "bottom":
                    pos = (random.randint(0,WIDTH), HEIGHT+TILE)
                elif side == "left":
                    pos = (-TILE, random.randint(0,HEIGHT))
                else:
                    pos = (WIDTH+TILE, random.randint(0,HEIGHT))
                Enemy(pos, self.all_sprites, self.enemies)
            # rent timer
            self.next_rent_timer -= dt
            if self.next_rent_timer <= 0:
                self.pay_rent()
                self.next_rent_timer = RENT_INTERVAL_SEC
    def pay_rent(self):
        if self.cash >= self.rent_due:
            self.cash -= self.rent_due
            self.dialogue = f"Rent paid: ${self.rent_due}!"
            self.rent_due = int(self.rent_due * 1.25)
        else:
            self.game_over(evicted=True)
    # ------------- DRAW -------------
    def draw(self):
        self.screen.fill((20,20,30))
        self.all_sprites.draw(self.screen)
        # hp bars
        self.player.draw_hp(self.screen)
        for enemy in self.enemies:
            pass  # could add hp bars
        # HUD
        hud_font = pygame.font.SysFont(FONT_NAME, 24)
        cash_surf = hud_font.render(f"$ {int(self.cash)}", True, YELLOW)
        rent_surf = hud_font.render(f"Rent: {self.rent_due}", True, WHITE)
        timer_surf= hud_font.render(f"Due in: {int(self.next_rent_timer)}s", True, WHITE)
        self.screen.blit(cash_surf, (10,10))
        self.screen.blit(rent_surf,(10,34))
        self.screen.blit(timer_surf,(10,58))
        # dialogue
        if self.dialogue:
            dlg_font = pygame.font.SysFont(FONT_NAME, 20)
            txt = dlg_font.render(self.dialogue, True, WHITE)
            rect = txt.get_rect(center=(WIDTH//2, HEIGHT-30))
            pygame.draw.rect(self.screen, (0,0,0), rect.inflate(20,10))
            self.screen.blit(txt, rect)
        # shop overlay
        if self.shop_open:
            self.draw_shop()
    # ------------- SHOP UI -------------
    def draw_shop(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0,0,0, 180))
        self.screen.blit(overlay,(0,0))
        font = pygame.font.SysFont(FONT_NAME, 28)
        header = font.render("Shop – Click item to buy (Esc to close)", True, WHITE)
        self.screen.blit(header, (WIDTH//2 - header.get_width()//2, 60))
        # item list
        item_font = pygame.font.SysFont(FONT_NAME, 24)
        self.item_rects = []
        y = 120
        for i,(name,(cost,effect)) in enumerate(SHOP_ITEMS.items()):
            txt = item_font.render(f"{name} – ${cost}", True, WHITE)
            rect = txt.get_rect(center=(WIDTH//2, y))
            pygame.draw.rect(self.screen, GREY, rect.inflate(20,10))
            self.screen.blit(txt, rect)
            self.item_rects.append((rect, name, cost, effect))
            y += 50
        # player cash
        cash_surf = font.render(f"$ {int(self.cash)}", True, YELLOW)
        self.screen.blit(cash_surf, (WIDTH//2 - cash_surf.get_width()//2, y+20))
    def handle_shop_click(self, pos):
        for rect, name, cost, effect in self.item_rects:
            if rect.collidepoint(pos):
                self.buy_item(name, cost, effect)
    # ------------- GAME OVER -------------
    def game_over(self, evicted=False):
        font = pygame.font.SysFont(FONT_NAME, 48)
        text = "Evicted!" if evicted else "You Died!"
        txt = font.render(text, True, RED)
        rect = txt.get_rect(center=(WIDTH//2, HEIGHT//2))
        self.screen.blit(txt, rect)
        pygame.display.flip()
        pygame.time.delay(3000)
        # reset save and restart
        if os.path.exists(SAVE_FILE):
            os.remove(SAVE_FILE)
        self.__init__()

# -----------------------------------------------------------------------------
if __name__ == "__main__":
    Game().run()