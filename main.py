import os
import sys
import json
import math
from dataclasses import dataclass

# Headless fallback for CI/servers without display/audio
if not os.environ.get("DISPLAY") and os.environ.get("SDL_VIDEODRIVER") is None:
	os.environ["SDL_VIDEODRIVER"] = "dummy"
	os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame as pg

# ---------- Settings ----------
WIDTH, HEIGHT = 1280, 720
TITLE = "Rent Quest"
FPS = 60
BG_COLOR = (20, 20, 24)

# Gameplay settings
PLAYER_SPEED = 260.0
PLAYER_MAX_HEALTH = 100
BULLET_SPEED = 700.0
BULLET_LIFETIME = 0.9
BULLET_COOLDOWN = 0.18
MONSTER_SPEED = 120.0
MONSTER_DAMAGE = 10
SPAWN_INTERVAL = 2.0
RENT_AMOUNT = 500
RENT_DEADLINE_DAYS = 5

SAVE_PATH = os.path.join(os.path.dirname(__file__), "save.json")


@dataclass
class SaveData:
	money: int = 0
	day: int = 1
	rent_paid: bool = False
	player_max_health: int = PLAYER_MAX_HEALTH
	gun_level: int = 1


class Scene:
	def __init__(self, game):
		self.game = game

	def handle_event(self, event: pg.event.Event):
		pass

	def update(self, dt: float):
		pass

	def draw(self, surface: pg.Surface):
		pass


class SceneManager:
	def __init__(self, start_scene: 'Scene'):
		self.scene = start_scene

	def set(self, scene: 'Scene'):
		self.scene = scene

	def handle_event(self, event):
		self.scene.handle_event(event)

	def update(self, dt):
		self.scene.update(dt)

	def draw(self, surface):
		self.scene.draw(surface)


class Player(pg.sprite.Sprite):
	def __init__(self, pos):
		super().__init__()
		self.base_image = pg.Surface((32, 32), pg.SRCALPHA)
		pg.draw.circle(self.base_image, (80, 200, 255), (16, 16), 16)
		self.image = self.base_image.copy()
		self.rect = self.image.get_rect(center=pos)
		self.pos = pg.Vector2(pos)
		self.vel = pg.Vector2()
		self.health = PLAYER_MAX_HEALTH
		self.max_health = PLAYER_MAX_HEALTH
		self.last_shot_time = 0.0
		self.gun_level = 1

	def handle_input(self, dt):
		keys = pg.key.get_pressed()
		move = pg.Vector2(
			(keys[pg.K_d] or keys[pg.K_RIGHT]) - (keys[pg.K_a] or keys[pg.K_LEFT]),
			(keys[pg.K_s] or keys[pg.K_DOWN]) - (keys[pg.K_w] or keys[pg.K_UP]),
		)
		if move.length_squared() > 0:
			move = move.normalize()
		self.vel = move * PLAYER_SPEED
		self.pos += self.vel * dt
		self.rect.center = self.pos

	def try_shoot(self, bullets, now, target_pos):
		if now - self.last_shot_time < BULLET_COOLDOWN:
			return
		self.last_shot_time = now
		direction = pg.Vector2(target_pos) - self.pos
		if direction.length_squared() == 0:
			return
		direction = direction.normalize()
		spread = max(0, 6 - self.gun_level)
		num = 1 if self.gun_level < 3 else 2
		for i in range(num):
			angle_offset = (i - (num - 1) / 2.0) * math.radians(spread)
			dir_rot = pg.Vector2(
				direction.x * math.cos(angle_offset) - direction.y * math.sin(angle_offset),
				direction.x * math.sin(angle_offset) + direction.y * math.cos(angle_offset),
			)
			bullets.add(Bullet(self.pos + dir_rot * 20, dir_rot))

	def damage(self, amount):
		self.health = max(0, self.health - amount)

	def heal_full(self):
		self.health = self.max_health


class Bullet(pg.sprite.Sprite):
	def __init__(self, pos, direction):
		super().__init__()
		self.image = pg.Surface((8, 8), pg.SRCALPHA)
		pg.draw.circle(self.image, (255, 240, 120), (4, 4), 4)
		self.rect = self.image.get_rect(center=pos)
		self.pos = pg.Vector2(pos)
		self.vel = pg.Vector2(direction) * BULLET_SPEED
		self.spawn_time = 0.0

	def update(self, dt, now):
		if self.spawn_time == 0.0:
			self.spawn_time = now
		if now - self.spawn_time > BULLET_LIFETIME:
			self.kill()
			return
		self.pos += self.vel * dt
		self.rect.center = self.pos
		if not (0 <= self.rect.centerx <= WIDTH and 0 <= self.rect.centery <= HEIGHT):
			self.kill()


class Monster(pg.sprite.Sprite):
	def __init__(self, pos):
		super().__init__()
		self.image = pg.Surface((28, 28), pg.SRCALPHA)
		pg.draw.rect(self.image, (255, 90, 90), (0, 0, 28, 28), border_radius=6)
		self.rect = self.image.get_rect(center=pos)
		self.pos = pg.Vector2(pos)
		self.health = 30

	def update(self, dt, player_pos):
		direction = (player_pos - self.pos)
		if direction.length_squared() > 0:
			direction = direction.normalize()
		self.pos += direction * MONSTER_SPEED * dt
		self.rect.center = self.pos


class FloatingText:
	def __init__(self, text, pos, color=(255, 255, 255)):
		self.text = text
		self.pos = pg.Vector2(pos)
		self.color = color
		self.lifetime = 0.8
		self.age = 0.0

	def update(self, dt):
		self.age += dt
		self.pos.y -= 40 * dt

	def is_alive(self):
		return self.age < self.lifetime

	def draw(self, surface, font):
		alpha = max(0, 255 * (1 - self.age / self.lifetime))
		surf = font.render(self.text, True, self.color)
		surf.set_alpha(alpha)
		surface.blit(surf, surf.get_rect(center=self.pos))


class HUD:
	def __init__(self, game):
		self.game = game
		self.font = pg.font.SysFont("consolas", 20)

	def draw_bar(self, surface, x, y, w, h, pct, color):
		pg.draw.rect(surface, (40, 40, 44), (x, y, w, h))
		inner_w = max(0, int(w * max(0.0, min(1.0, pct))))
		pg.draw.rect(surface, color, (x, y, inner_w, h))
		pg.draw.rect(surface, (16, 16, 18), (x, y, w, h), 2)

	def draw(self, surface):
		player = self.game.player
		money = self.game.money
		day = self.game.day
		rent_due = RENT_AMOUNT
		health_pct = player.health / player.max_health

		self.draw_bar(surface, 20, 20, 200, 18, health_pct, (60, 210, 90))
		surface.blit(self.font.render(f"HP {player.health}/{player.max_health}", True, (230, 230, 230)), (24, 20))
		surface.blit(self.font.render(f"$ {money}", True, (240, 230, 150)), (20, 44))
		surface.blit(self.font.render(f"Day {day}/{RENT_DEADLINE_DAYS}", True, (180, 200, 240)), (20, 68))
		surface.blit(self.font.render(f"Rent: ${rent_due}", True, (220, 180, 200)), (20, 92))


class TownScene(Scene):
	def __init__(self, game):
		super().__init__(game)
		self.player = game.player
		self.hud = HUD(game)
		self.font = pg.font.SysFont("consolas", 22)
		self.prompt_font = pg.font.SysFont("consolas", 18)
		# Simple NPCs
		self.npcs = [
			(pg.Vector2(400, 360), "Landlord: Rent due in 5 days. Pay at the desk."),
			(pg.Vector2(800, 360), "Shopkeeper: Upgrades for cash! Press E to browse."),
		]

	def handle_event(self, event):
		if event.type == pg.KEYDOWN and event.key == pg.K_e:
			# Interact depending on proximity
			for pos, text in self.npcs:
				if self.player.pos.distance_to(pos) < 70:
					if "Landlord" in text:
						self.game.try_pay_rent()
					else:
						self.game.open_shop()

		if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
			# Enter combat by clicking the gate area
			mx, my = pg.mouse.get_pos()
			if WIDTH - 140 <= mx <= WIDTH - 20 and HEIGHT/2 - 60 <= my <= HEIGHT/2 + 60:
				self.game.scene_manager.set(CombatScene(self.game))

	def update(self, dt):
		self.player.handle_input(dt)

	def draw(self, surface):
		surface.fill((34, 40, 48))
		# simple buildings and gate
		pg.draw.rect(surface, (60, 60, 90), (300, 280, 200, 160))
		pg.draw.rect(surface, (90, 60, 60), (780, 280, 200, 160))
		pg.draw.rect(surface, (70, 100, 70), (WIDTH - 160, HEIGHT/2 - 80, 140, 160))
		surface.blit(self.font.render("LANDLORD", True, (230, 230, 250)), (330, 290))
		surface.blit(self.font.render("SHOP", True, (250, 230, 230)), (835, 290))
		surface.blit(self.font.render("Gate ->", True, (210, 240, 210)), (WIDTH - 150, HEIGHT/2 - 100))

		# NPCs
		for pos, text in self.npcs:
			pg.draw.circle(surface, (200, 200, 220), pos, 14)
			if self.player.pos.distance_to(pos) < 100:
				prompt = self.prompt_font.render("Press E to interact", True, (240, 240, 240))
				surface.blit(prompt, prompt.get_rect(midbottom=(pos.x, pos.y - 20)))
				bubble = self.prompt_font.render(text, True, (230, 230, 230))
				surface.blit(bubble, bubble.get_rect(midtop=(pos.x, pos.y + 20)))

		# Player
		surface.blit(self.player.image, self.player.rect)

		# HUD
		self.hud.draw(surface)


class CombatScene(Scene):
	def __init__(self, game):
		super().__init__(game)
		self.player = game.player
		self.bullets = pg.sprite.Group()
		self.monsters = pg.sprite.Group()
		self.spawn_timer = 0.0
		self.floaters = []
		self.hud = HUD(game)
		self.font = pg.font.SysFont("consolas", 18)

	def handle_event(self, event):
		if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
			self.game.scene_manager.set(TownScene(self.game))
		if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
			now = pg.time.get_ticks() / 1000.0
			self.player.try_shoot(self.bullets, now, pg.mouse.get_pos())

	def update(self, dt):
		# input
		self.player.handle_input(dt)
		now = pg.time.get_ticks() / 1000.0
		if pg.mouse.get_pressed()[0]:
			self.player.try_shoot(self.bullets, now, pg.mouse.get_pos())

		# spawn monsters
		self.spawn_timer += dt
		if self.spawn_timer >= SPAWN_INTERVAL:
			self.spawn_timer = 0.0
			spawn_pos = pg.Vector2(
				40 if pg.time.get_ticks() % 2 == 0 else WIDTH - 40,
				40 if (pg.time.get_ticks() // 2) % 2 == 0 else HEIGHT - 40,
			)
			self.monsters.add(Monster(spawn_pos))

		# updates
		self.bullets.update(dt, now)
		for m in list(self.monsters):
			m.update(dt, self.player.pos)
			if m.rect.colliderect(self.player.rect):
				self.player.damage(MONSTER_DAMAGE * dt)
				if self.player.health <= 0:
					self.game.on_player_down()

		# bullet hits
		for m in list(self.monsters):
			for b in list(self.bullets):
				if m.rect.colliderect(b.rect):
					m.health -= 25 + 5 * (self.game.gun_level - 1)
					b.kill()
					if m.health <= 0:
						self.monsters.remove(m)
						self.floaters.append(FloatingText("+$20", m.pos, (120, 255, 120)))
						self.game.money += 20
						break

		# floaters
		self.floaters = [f for f in self.floaters if f.is_alive()]
		for f in self.floaters:
			f.update(dt)

	def draw(self, surface):
		surface.fill((24, 26, 30))
		# arena bounds
		pg.draw.rect(surface, (70, 70, 80), (40, 40, WIDTH - 80, HEIGHT - 80), 2)

		surface.blit(self.player.image, self.player.rect)
		for m in self.monsters:
			surface.blit(m.image, m.rect)
		for b in self.bullets:
			surface.blit(b.image, b.rect)

		# floaters
		font = pg.font.SysFont("consolas", 18)
		for f in self.floaters:
			f.draw(surface, font)

		self.hud.draw(surface)


class ShopMenu:
	def __init__(self, game):
		self.game = game
		self.font = pg.font.SysFont("consolas", 20)
		self.big_font = pg.font.SysFont("consolas", 28)
		self.visible = False

	def open(self):
		self.visible = True

	def close(self):
		self.visible = False

	def handle_event(self, event):
		if not self.visible:
			return
		if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
			self.close()
		if event.type == pg.KEYDOWN and event.key == pg.K_1:
			self.game.buy_heal()
		if event.type == pg.KEYDOWN and event.key == pg.K_2:
			self.game.buy_max_health()
		if event.type == pg.KEYDOWN and event.key == pg.K_3:
			self.game.buy_gun_upgrade()

	def draw(self, surface):
		if not self.visible:
			return
		overlay = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
		overlay.fill((0, 0, 0, 180))
		surface.blit(overlay, (0, 0))
		y = 160
		surface.blit(self.big_font.render("Shop", True, (250, 250, 250)), (WIDTH/2 - 40, y))
		y += 50
		surface.blit(self.font.render("[1] Medkit $30 (restore to full)", True, (230, 230, 230)), (WIDTH/2 - 180, y)); y += 30
		surface.blit(self.font.render("[2] Max HP +20 $80", True, (230, 230, 230)), (WIDTH/2 - 180, y)); y += 30
		surface.blit(self.font.render("[3] Gun Upgrade $120", True, (230, 230, 230)), (WIDTH/2 - 180, y)); y += 30
		surface.blit(self.font.render("Esc to close", True, (180, 180, 180)), (WIDTH/2 - 180, y))


class Game:
	def __init__(self):
		pg.init()
		self.headless = False
		try:
			self.screen = pg.display.set_mode((WIDTH, HEIGHT))
		except pg.error:
			# Headless fallback using offscreen surface
			self.headless = True
			self.screen = pg.Surface((WIDTH, HEIGHT))
		else:
			pg.display.set_caption(TITLE)
		self.clock = pg.time.Clock()
		self.running = True

		# state
		self.player = Player((WIDTH/2, HEIGHT/2))
		self.money = 0
		self.day = 1
		self.rent_paid = False
		self.gun_level = 1
		self.shop = ShopMenu(self)

		self.load()

		self.scene_manager = SceneManager(TownScene(self))

	def open_shop(self):
		self.shop.open()

	def try_pay_rent(self):
		if self.rent_paid:
			return
		if self.money >= RENT_AMOUNT:
			self.money -= RENT_AMOUNT
			self.rent_paid = True
		else:
			pass

	def buy_heal(self):
		if self.money >= 30:
			self.money -= 30
			self.player.heal_full()

	def buy_max_health(self):
		if self.money >= 80:
			self.money -= 80
			self.player.max_health += 20
			self.player.heal_full()

	def buy_gun_upgrade(self):
		if self.money >= 120 and self.gun_level < 5:
			self.money -= 120
			self.gun_level += 1
			self.player.gun_level = self.gun_level

	def on_player_down(self):
		# Simple penalty and reset to town
		self.money = max(0, self.money - 50)
		self.player.heal_full()
		self.player.pos = pg.Vector2(WIDTH/2, HEIGHT/2)
		self.player.rect.center = self.player.pos
		self.scene_manager.set(TownScene(self))

	def advance_day(self):
		if self.rent_paid:
			self.day = 1
			self.rent_paid = False
		else:
			self.day += 1
			if self.day > RENT_DEADLINE_DAYS:
				# game over state; reset minimal
				self.day = 1
				self.money = 0
				self.rent_paid = False

	def save(self):
		data = SaveData(
			money=self.money,
			day=self.day,
			rent_paid=self.rent_paid,
			player_max_health=self.player.max_health,
			gun_level=self.gun_level,
		).__dict__
		with open(SAVE_PATH, "w") as f:
			json.dump(data, f)

	def load(self):
		if not os.path.exists(SAVE_PATH):
			return
		try:
			with open(SAVE_PATH, "r") as f:
				data = json.load(f)
			self.money = int(data.get("money", 0))
			self.day = int(data.get("day", 1))
			self.rent_paid = bool(data.get("rent_paid", False))
			self.player.max_health = int(data.get("player_max_health", PLAYER_MAX_HEALTH))
			self.player.heal_full()
			self.gun_level = int(data.get("gun_level", 1))
			self.player.gun_level = self.gun_level
		except Exception:
			pass

	def run(self):
		day_timer = 0.0
		while self.running:
			dt = self.clock.tick(FPS) / 1000.0
			for event in pg.event.get():
				if event.type == pg.QUIT:
					self.running = False
				elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE and isinstance(self.scene_manager.scene, TownScene) and not self.shop.visible:
					# pause in town toggles shop for simplicity
					self.shop.open()
				self.shop.handle_event(event)
				if not self.shop.visible:
					self.scene_manager.handle_event(event)

			if not self.shop.visible:
				self.scene_manager.update(dt)

			# day progression every ~60 seconds
			day_timer += dt
			if day_timer >= 60.0:
				day_timer = 0.0
				self.advance_day()

			# draw
			self.scene_manager.draw(self.screen)
			if self.shop.visible:
				self.shop.draw(self.screen)

			if not self.headless:
				pg.display.flip()

		self.save()
		pg.quit()
		sys.exit(0)


if __name__ == "__main__":
	Game().run()