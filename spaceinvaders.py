#!/usr/bin/env python3
'''
	Name: Space Invaders
	Module: PyArcade
'''
import arcade, os, sys, random, time, timeit, collections

#Window properties
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Space Invaders"
#Sprite scaling
PLAYER_SCALING = 0.7
BULLET_SCALING = 1
ENEMY_SCALING = 0.3
#Physics and movement
MOVEMENT_SPEED = 3.5
BULLET_SPEED = 5
#Game status
GAME_RUNNING = 1
GAME_OVER = 2
GAME_WIN = 3
#Instruction page
INSTRUCTION_PAGE = 0

class MyGame(arcade.Window):
	def __init__(self, width, height, title):
		#Standard declarations and working folder
		super().__init__(width, height, title, fullscreen=False)
		file_path = os.path.dirname(os.path.abspath(__file__))
		os.chdir(file_path)
		
		#Inizialize Variables
		self.player_list = None
		self.enemy_list = None
		self.bullet_list = None
		self.enemy_bullet_list = None
		self.background = None
		self.player_sprite = None
		self.enemy_sprite = None

		#Fps counter 
		self.fps = FPSCounter()
		self.fps_counter_state = False

		#Set of current state and score
		self.current_state = INSTRUCTION_PAGE
		self.score = 0	

		#Movement variables
		self.left_pressed = False
		self.right_pressed = False
		self.down_pressed = False
		self.up_pressed = False	
		
		self.instructions = []
		texture = arcade.load_texture("sprites/instructions.png")
		self.instructions.append(texture)

	def setup(self):
		#Declarations of Sprite lists
		self.player_list = arcade.SpriteList()
		self.enemy_list = arcade.SpriteList()
		self.bullet_list = arcade.SpriteList()
		self.enemy_bullet_list = arcade.SpriteList()

		#Player score
		self.score = 0

		#Player spawn
		self.player_sprite = Player("sprites/ship.png", PLAYER_SCALING)
		self.player_sprite.center_x = (SCREEN_WIDTH/2)
		self.player_sprite.center_y = 50
		self.player_list.append(self.player_sprite)
		
		#Spacing for spawning enemies
		X_SPACING = 0
		Y_SPACING = 0

		#Enemy Spawn
		for col in range(2):
			for row in range(14):
				self.enemy_sprite = Enemy("sprites/enemy1_1.png", ENEMY_SCALING)
				self.enemy_sprite.center_x = 70 + X_SPACING
				self.enemy_sprite.center_y = 570 - Y_SPACING
				self.enemy_list.append(self.enemy_sprite)
				X_SPACING += 50
			Y_SPACING += 50
			X_SPACING = 0

		#Loads the background
		self.background = arcade.load_texture("sprites/background.jpg")

	def draw_instructions(self,page_number):
		#Draws instructions
		page_texture = self.instructions[page_number]
		arcade.draw_texture_rectangle(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, page_texture.width, page_texture.height, page_texture, 0)	

	def draw_game_win(self):
		#Draws game win screen
		output = "YOU WON"
		arcade.draw_text(output, 200, SCREEN_HEIGHT / 2, arcade.color.GREEN, 50)
		
		output = "Press R to restart"
		arcade.draw_text(output, 200, (SCREEN_HEIGHT / 2) - 35, arcade.color.WHITE, 18)

		output = "Press ESC to exit"
		arcade.draw_text(output, 200, (SCREEN_HEIGHT /2 )- 70, arcade.color.WHITE, 18)

	def draw_game_over(self):
		#Draws game over screen
		output = "GAME OVER"
		arcade.draw_text(output, 200, SCREEN_HEIGHT / 2, arcade.color.RED, 50)
		
		output = "Press R to restart"
		arcade.draw_text(output, 200, (SCREEN_HEIGHT / 2) - 35, arcade.color.WHITE, 18)

		output = "Press ESC to exit"
		arcade.draw_text(output, 200, (SCREEN_HEIGHT /2 )- 70, arcade.color.WHITE, 18)

	def draw_game(self):
		#Draws the game
		self.player_list.draw()
		self.enemy_list.draw()
		self.bullet_list.draw()
		self.enemy_bullet_list.draw()

		output = f"Score: {self.score}"
		arcade.draw_text(output, 10 , 20, arcade.color.WHITE, 14)

	def draw_fps(self):
		#Draws FPS on the screen
		fps = self.fps.get_fps()
		output = f"FPS:{fps:3.0f}"
		arcade.draw_text(output, 10, 10, arcade.color.WHITE, 7)

	def on_draw(self):
		#Starts a timer
		draw_start_timer = timeit.default_timer()

		arcade.start_render()

		#Draws the background
		arcade.draw_texture_rectangle(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, SCREEN_WIDTH, SCREEN_HEIGHT, self.background)
		
		#If the FPS toggle is on call the function
		if self.fps_counter_state == True:
			self.draw_fps()

		#Draw the game state layouts
		if self.current_state == INSTRUCTION_PAGE:
			self.draw_instructions(0)
		elif self.current_state == GAME_RUNNING:
			self.draw_game()
		elif self.current_state == GAME_OVER:
			self.draw_game_over()
		elif self.current_state == GAME_WIN:
			self.draw_game_win()

		self.draw_time = timeit.default_timer() - draw_start_timer
		self.fps.tick()
	
	def update(self, delta_time):
		if self.current_state == GAME_RUNNING:
			self.player_list.update()
			self.enemy_list.update()
			self.bullet_list.update()
			self.enemy_bullet_list.update()

			#Enemies randomly shoot bullets
			for enemy in self.enemy_list:
				if random.randrange(500) == 0:
					enemy_bullet = arcade.Sprite("sprites/enemylaser.png")
					enemy_bullet.center_x = enemy.center_x
					enemy_bullet.top = enemy.bottom
					enemy_bullet.change_y = -2
					self.enemy_bullet_list.append(enemy_bullet)

			#If a enemy bullet hits the player, delete the player and go to game over
			if arcade.check_for_collision_with_list(self.player_sprite, self.enemy_list):
				self.player_sprite.kill()
				self.current_state = GAME_OVER

			#Enemy bullet logic
			for enemy_bullet in self.enemy_bullet_list:
				enemy_hit_list = arcade.check_for_collision_with_list(enemy_bullet, self.player_list)
				if len(enemy_hit_list) > 0:
					enemy_bullet.kill()
				for player in enemy_hit_list:
					player.kill()
					self.current_state = GAME_OVER
				if enemy_bullet.bottom > SCREEN_HEIGHT:
					enemy_bullet.kill()	

			#Player bullet logic
			for bullet in self.bullet_list:
				hit_list = arcade.check_for_collision_with_list(bullet, self.enemy_list)
				if len(hit_list) > 0:
					bullet.kill()
				for enemy in hit_list:
					enemy.kill()
					self.score += 10
				if bullet.bottom > SCREEN_HEIGHT:
					bullet.kill()

			#Player Movement
			self.player_sprite.change_x = 0
			self.player_sprite.change_y = 0
			
			if self.up_pressed and not self.down_pressed:
				self.player_sprite.change_y = MOVEMENT_SPEED
			elif self.down_pressed and not self.up_pressed:
				self.player_sprite.change_y = -MOVEMENT_SPEED
			if self.left_pressed and not self.right_pressed:
				self.player_sprite.change_x = -MOVEMENT_SPEED
			elif self.right_pressed and not self.left_pressed:
				self.player_sprite.change_x = MOVEMENT_SPEED

			#If enemies touch the bottom of the screen go to game over
			if self.enemy_sprite.center_y < 50:
				self.current_state = GAME_OVER
			
			#If there aren't enemies the game stops
			if len(self.enemy_list) == 0:
				self.current_state = GAME_WIN

	def on_key_press(self, key, modifiers):
		#Fps toggle
		if key == arcade.key.F10:
			self.fps_counter_state = (not self.fps_counter_state)
		#Fullscreen toggle
		if key == arcade.key.F11:
			self.set_fullscreen(not self.fullscreen)
			self.set_viewport(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT)
		#Key map
		if self.current_state == INSTRUCTION_PAGE:
			if key == arcade.key.SPACE:
				self.current_state = GAME_RUNNING
		elif self.current_state == GAME_RUNNING:
			if key == arcade.key.UP or key == arcade.key.W:
				self.up_pressed = True
			elif key == arcade.key.DOWN or key == arcade.key.S:
				self.down_pressed = True
			if key == arcade.key.LEFT or key == arcade.key.A:
				self.left_pressed = True
			elif key == arcade.key.RIGHT or key == arcade.key.D:
				self.right_pressed = True
			if key == arcade.key.SPACE:
				bullet = arcade.Sprite("sprites/laser.png", BULLET_SCALING)
				bullet.change_y = BULLET_SPEED
				bullet.center_x = self.player_sprite.center_x
				bullet.bottom = self.player_sprite.top
				self.bullet_list.append(bullet)
		if self.current_state == GAME_OVER or self.current_state == GAME_WIN:
			if key == arcade.key.R:
				self.setup()
				self.current_state = GAME_RUNNING

		if key == arcade.key.ESCAPE:
			sys.exit()	

	def on_key_release(self, key, modifiers):
		#For better player movement
		if self.current_state == GAME_RUNNING:
			if key == arcade.key.UP or key == arcade.key.W:
				self.up_pressed = False
			elif key == arcade.key.DOWN or key == arcade.key.S:
				self.down_pressed = False
			if key == arcade.key.LEFT or key == arcade.key.A:
				self.left_pressed = False
			elif key == arcade.key.RIGHT or key == arcade.key.D:
				self.right_pressed = False

class Player(arcade.Sprite):
	#Properties of Player class
	def update(self):
		self.center_x += self.change_x
		self.center_y += self.change_y

		if self.left < 0:
			self.left = 0
		elif self.right > SCREEN_WIDTH - 1:
			self.right = SCREEN_WIDTH - 1

		if self.bottom < 0:
			self.bottom = 0
		elif self.top > SCREEN_HEIGHT - 1:
			self.top = SCREEN_HEIGHT - 1

class Enemy(arcade.Sprite):
	#Properties of Enemy class
	def update(self):
		self.center_x += self.change_x
		self.center_y += self.change_y 

		self.center_y -= 0.4

		if self.left < 0:
			self.left = 0
		elif self.right > SCREEN_WIDTH - 1:
			self.right = SCREEN_WIDTH - 1

		if self.bottom < 0:
			self.bottom = 0
		elif self.top > SCREEN_HEIGHT - 1:
			self.top = SCREEN_HEIGHT - 1

class FPSCounter:
	def __init__(self):
		self.time = time.perf_counter()
		self.frame_times = collections.deque(maxlen=60)

	def tick(self):
		t1 = time.perf_counter()
		dt = t1 - self.time
		self.time = t1
		self.frame_times.append(dt)

	def get_fps(self):
		total_time = sum(self.frame_times)
		if total_time == 0:
			return 0
		else:
			return len(self.frame_times) / sum(self.frame_times)

def main():
	#Setup and start the game
	game = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
	game.setup()
	arcade.run()

if __name__ == "__main__":
	main()