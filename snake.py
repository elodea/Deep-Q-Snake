import numpy as np
import pygame
from random import randint

class vec2:
	def __init__(self, x, y):
		self.x = int(x)
		self.y = int(y)

	def add(self, x, y):
		self.x += x
		self.y += y

	def __str__(self):
		return f'({self.x},{self.y})'

	def __eq__(self, other):
		return self.x == other.x and self.y == other.y

def create_game(w, h, conf_g):
	pygame.init()
	pygame.font.init()
	pygame.display.set_caption("snake ai")

	screen = pygame.display.set_mode((w, h))
	game = snake(w, h, conf_g)

	return screen, game

class game:
	def __init__(self):
		self.round = 0
		self.score = 0

	def get_score(self):
		return self.score

	def get_round(self):
		return self.round

class snake(game):
	def __init__(self, w, h, conf_g):
		super(snake, self).__init__()

		self.h = h
		self.w = min(w, h)
		self.cols = int(conf_g['cols'])
		self.rows = int(conf_g['rows'])
		self.top_padding = h-w
		self.gs = (h-self.top_padding)/self.cols

		self.round = 0
		self.food_reward = float(conf_g['food_reward'])
		self.death_penalty = float(conf_g['death_penalty'])
		self.movement_penalty = float(conf_g['movement_penalty'])
		self.tail_size = int(conf_g['tail_size'])

		self.action_bindings = ['L', 'R', 'U', 'D']
		self.score_font = pygame.font.SysFont('Arial', int(self.top_padding * 0.7))
		self.reset()

	def reset(self):
		self.dir = vec2(0,-1)
		self.head = vec2(self.cols / 2 * self.gs, (self.rows / 2 * self.gs) + self.top_padding)
		self.body = [vec2(self.head.x, self.head.y+(self.gs*(self.tail_size-1)))]
		for i in range(1, self.tail_size-1):
			self.body.append(vec2(self.body[i-1].x, self.body[i-1].y-self.gs))
		self.food = self.create_food()
		self.score = 0
		self.delta_score = 0
		self.ended = False

	def is_ended(self):
		return self.ended

	def create_food(self):
		result = vec2(randint(0,self.cols-1) * self.gs, (randint(0, self.rows-1) * self.gs) + self.top_padding)
		while self.collided(result):
			result = vec2(randint(0,self.cols-1) * self.gs, (randint(0, self.rows-1) * self.gs) + self.top_padding)

		return result

	def eat(self):
		self.body.insert(0,vec2(self.body[0].x, self.body[0].y))
		self.food = self.create_food()

	def collided(self, pos):
		for v in self.body:
			if (pos == v):
				return True
		return False

	def move(self):
		self.body.pop(0)
		self.body.append(vec2(self.head.x, self.head.y))
		self.head.add(self.gs * self.dir.x, self.gs * self.dir.y)
		self.wrap()
		self.delta_score -= self.movement_penalty

	def wrap(self):
		if self.head.x < 0:
			self.head.x = (self.cols-1) * self.gs
		if self.head.x > (self.cols - 1) * self.gs:
			self.head.x = 0
		if self.head.y < self.top_padding:
			self.head.y = (self.rows-1) * self.gs + self.top_padding
		if self.head.y > (self.rows-1) * self.gs + self.top_padding:
			self.head.y = self.top_padding;

	def update(self):
		self.move()

		if (self.food == self.head):
			self.eat()
			self.score += 1
			self.delta_score += self.food_reward
		elif self.collided(self.head):
			self.ended = True
			self.round += 1
			self.delta_score = self.death_penalty
		
	def perform_action(self, action):
		if self.ended:
			return

		action = self.action_bindings[action]

		if action == 'L' and self.dir != vec2(1,0):
			self.dir = vec2(-1,0)
		elif action == 'R' and self.dir != vec2(-1,0):
			self.dir = vec2(1,0)
		elif action == 'U' and self.dir != vec2(0,1):
			self.dir = vec2(0,-1)
		elif action == 'D' and self.dir != vec2(0,-1):
			self.dir = vec2(0,1)

		self.update()

	def get_state(self, screen):
		pixels = pygame.surfarray.array3d(screen)
		pixels = np.fliplr(np.flip(np.rot90(pixels)))
		reward = self.delta_score
		self.delta_score = 0

		return pixels, reward

	def draw(self, surf):
		pygame.draw.rect(surf,(150,255,150),(self.food.x+1, self.food.y+1,self.gs-2,self.gs-2)) # food
		pygame.draw.rect(surf,(230,50,200),(self.head.x+1,self.head.y+1,self.gs-2,self.gs-2)) # head

		for v in self.body:
			pygame.draw.rect(surf,(220,20,20),(v.x+1,v.y+1,self.gs-2,self.gs-2)) # body

		#UI
		pygame.draw.line(surf,(255,255,255,),(0,self.top_padding),(self.w,self.top_padding))
		text = self.score_font.render(f'Score: {self.score}', False, (255, 255, 255))
		surf.blit(text, (0, 0))