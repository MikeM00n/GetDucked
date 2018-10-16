'''
Get Ducked! is a game in which the player assumes the roll of the duck.
The general idea of the game is to survive the ever increasing difficulty
and growing onslaught of hunters, boats with hunters and airplanes.
The player is rewarded every so often with a large bump in score.
Hearts will occasionally be found to increase the players health
and provide a bump in the players score.
The longer the player stays alive the higher the score.
The score is saved to a text file and updated as the high score is beaten.
'''

# Import all the essential modules
import pygame as pg
import sys
import os
from os import path
from pygame.locals import *
from settings import *
from sprites import *

# The game object containing all the initialization and variable assignments
class Game(object):
    def __init__(self):
        # initialize game window
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        pg.init()
        pg.display.init()
        pg.mixer.init()
        pg.joystick.init()
        pg.mixer.set_num_channels(500)
        self.avail_res = pg.display.list_modes()
        self.mouse_pos = pg.mouse.get_pos()
        self.joysticks = []
        self.joystick_names = []
        self.screen_width = self.avail_res[0][0]
        self.screen_height = self.avail_res[0][1]

        for js in range(0, pg.joystick.get_count()):
            self.joysticks.append(pg.joystick.Joystick(js))
            self.joystick_names.append(pg.joystick.Joystick(js).get_name())
            self.joysticks[-1].init()

        pg.display.set_caption("Get Ducked!")
        self.screen = pg.display.set_mode([self.screen_width, self.screen_height], SRCALPHA | DOUBLEBUF | HWSURFACE | FULLSCREEN)
        self.screen_alpha = pg.Surface((self.screen_width, self.screen_height), SRCALPHA)
        self.clock = pg.time.Clock()
        self.running = True
        self.load_data()

# Function that loads all the data files used by the game for parsing
    def load_data(self):
        # Load high score text file
        if getattr(sys, 'frozen', False):
            # frozen
            self.dir = os.path.dirname(sys.executable)
        else:
            # unfrozen
            self.dir = os.path.dirname(os.path.realpath(__file__))

        # Load highscore file
        with open(path.join(self.dir, high_score_file), 'r') as f:
            try:
                self.highscore = int(f.read())
            except:
                self.highscore = 0

        img_dir = path.join(self.dir, 'img')

        # Load game icon
        self.icon = pg.image.load(path.join(img_dir, "GetDucked.ico"))
        pg.display.set_icon(self.icon)

        # Load spritesheet
        self.spritesheet = Spritesheet(path.join(img_dir, spritesheet))

        # Load menu background, mountains & trees & scale
        self.menu_bg = pg.image.load(path.join(img_dir, "menu_bg.png")).convert()
        self.menu_bg_width, self.menu_bg_height = self.menu_bg.get_size()
        self.mountains = pg.image.load(path.join(img_dir, "mountains.png")).convert()
        self.mountains_width, self.mountains_height = self.mountains.get_size()
        self.trees = pg.image.load(path.join(img_dir, "trees.png")).convert_alpha()
        self.trees_width, self.trees_height = self.trees.get_size()

        # Scale the images used in game to the appropriate native resolution of the users computer
        self.scaled_menu_bg = pg.transform.scale(self.menu_bg, (int(self.menu_bg_width * (self.screen_width / 1920)), int(self.menu_bg_height * (self.screen_height / 1080))))
        self.scaled_mountains = pg.transform.scale(self.mountains, (int(self.mountains_width * (self.screen_width / 1920)), int(self.mountains_height * (self.screen_height / 1080))))
        self.scaled_trees = pg.transform.scale(self.trees, (int(self.trees_width * (self.screen_width / 1920)), int(self.trees_height * (self.screen_height / 1080))))

        # Set the starting X position of the parallax background for scrolling
        self.mountains_x = 0
        self.trees_x = 0

        # Load sounds
        self.sound_dir = path.join(self.dir, 'sound')
        self.hit_sound = pg.mixer.Sound(path.join(self.sound_dir, "hit.ogg"))
        self.hit_sound.set_volume(1.0)
        self.shoot_sound = pg.mixer.Sound(path.join(self.sound_dir, "shoot.ogg"))
        self.shoot_sound.set_volume(0.075)
        self.crash_sound = pg.mixer.Sound(path.join(self.sound_dir, "crash.ogg"))
        self.crash_sound.set_volume(1.0)
        self.airplane_sound = pg.mixer.Sound(path.join(self.sound_dir, "airplane.ogg"))
        self.airplane_sound.set_volume(0.05)
        self.health_pickup_sound = pg.mixer.Sound(path.join(self.sound_dir, "healthpickup.ogg"))
        self.health_pickup_sound.set_volume(1.0)
        self.button_click_sound = pg.mixer.Sound(path.join(self.sound_dir, "buttonclick.ogg"))
        self.button_click_sound.set_volume(1.0)
        self.greeting_call = pg.mixer.Sound(path.join(self.sound_dir, "greeting_call.ogg"))
        self.greeting_call.set_volume(0.75)
        self.gameover = pg.mixer.Sound(path.join(self.sound_dir, "gameover.ogg"))
        self.gameover.set_volume(1)

    def new_game(self):
        # Start new game
        self.score = 0
        self.bullets = pg.sprite.RenderUpdates()
        self.enemies = pg.sprite.RenderUpdates()
        self.enemyboats = pg.sprite.RenderUpdates()
        self.planes = pg.sprite.RenderUpdates()
        self.clouds = pg.sprite.RenderUpdates()
        self.hearts = pg.sprite.RenderUpdates()
        self.all_sprites = pg.sprite.RenderUpdates()

        # SETUP ALL EVENTS
        # Hunters & boats shoot every 1 second
        self.shoot_event = USEREVENT + 1
        pg.time.set_timer(self.shoot_event, 1000)

        # Score timer - add 1pt every 50ms
        self.score_event = USEREVENT + 2
        pg.time.set_timer(self.score_event, 50)

        # Add 1 enemy and 1 cloud every 10 seconds
        self.progress_difficulty_event = USEREVENT + 3
        pg.time.set_timer(self.progress_difficulty_event, 10000)

        # Add 1 plane every 60 seconds
        self.add_airplane_event = USEREVENT + 4
        pg.time.set_timer(self.add_airplane_event, 60000)

        # Add 2000pts to score every 2 mins
        self.score_bonus_event = USEREVENT + 5
        pg.time.set_timer(self.score_bonus_event, 120000)

        # Add 1 heart every 45 seconds
        self.add_heart_event = USEREVENT + 6
        pg.time.set_timer(self.add_heart_event, 45000)

        # Add 1 enemy boat 45 seconds
        self.add_boat_event = USEREVENT + 7
        pg.time.set_timer(self.add_boat_event, 45000)

        # Add player sprite
        self.player = Player(self)
        self.all_sprites.add(self.player)

        # Load music
        pg.mixer.music.load(path.join(self.sound_dir, "playing.ogg"))
        
        # Enter run loop
        self.run()

    def run(self):
        # Game Loop
        self.greeting_call.play()
        pg.mixer.music.play(loops = -1)
        pg.mixer.music.set_volume(0.75)
        self.playing = True

        while self.playing:
            pg.mouse.set_visible(False)
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            self.update()
            self.draw()

        pg.mixer.music.fadeout(500)

    def events(self):
        # Game Loop Events
        if pg.event.get(self.shoot_event):
            for self.enemy in self.enemies:
                self.enemy.shoot()
            for self.enemyboat in self.enemyboats:
                self.enemyboat.shoot()
                self.enemyboat.shoot()
                self.enemyboat.shoot()

        if pg.event.get(self.score_event):
            self.score += 1

        if pg.event.get(self.progress_difficulty_event):
            self.cloud = Cloud(self)
            self.clouds.add(self.cloud)
            self.all_sprites.add(self.cloud)
            self.enemy = Enemy(self)
            self.enemies.add(self.enemy)
            self.all_sprites.add(self.enemy)

        if pg.event.get(self.add_boat_event):
            self.enemyboat = EnemyBoat(self)
            self.enemyboats.add(self.enemyboat)
            self.all_sprites.add(self.enemyboat)

        if pg.event.get(self.add_airplane_event):
            self.plane = Airplane(self)
            self.planes.add(self.plane)
            self.all_sprites.add(self.plane)

        if pg.event.get(self.score_bonus_event):
            self.score += 2000

        if pg.event.get(self.add_heart_event):
            self.heart = Heart(self)
            self.hearts.add(self.heart)
            self.all_sprites.add(self.heart)

        for e in pg.event.get():
            if e.type == pg.QUIT:
                self.playing = False
                self.running = False
                self.show_quit_screen()

            elif e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE:
                self.playing = False
                self.running = False
                self.show_quit_screen()

    def update(self):
        # Game Loop Update        
        self.all_sprites.update(self.dt)

        # Scrolling mountains and trees
        self.mountains_rel_x = self.mountains_x % self.scaled_mountains.get_rect().width
        self.screen.blit(self.scaled_mountains, (self.mountains_rel_x - self.scaled_mountains.get_rect().width, 0))
        if self.mountains_rel_x < self.screen_width:
            self.screen.blit(self.scaled_mountains, (self.mountains_rel_x, 0))
        self.mountains_x -= mountains_scroll_speed * self.dt

        self.trees_rel_x = self.trees_x % self.scaled_trees.get_rect().width
        self.screen.blit(self.scaled_trees, (self.trees_rel_x - self.scaled_trees.get_rect().width, self.screen_height * 19 / 32))
        if self.trees_rel_x < self.screen_width:
            self.screen.blit(self.scaled_trees, (self.trees_rel_x, self.screen_height * 19 / 32))
        self.trees_x -= trees_scroll_speed * self.dt

    def draw(self):
        # Game Loop Draw
        pg.display.set_caption("Get Ducked!")
        self.all_sprites.draw(self.screen)
        self.player.draw_health()
        self.draw_text('karmaticarcade', "Score: " + str(self.score), 22, black, self.screen_width / 2, 15)
        pg.display.update()

    def draw_text(self, font_name, text, size, color, x, y):
        # Render various fonts to images and draw them to the screen
        font = pg.font.Font("ka1.ttf", size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)
        return text_rect

    def show_start_screen(self):
        # Game start splash screen
        pg.mouse.set_visible(True)
        pg.mouse.set_cursor((8, 8), (4, 4), (24, 24, 24, 231, 231, 24, 24, 24), (0, 0, 0, 0, 0, 0, 0, 0))
        pg.mixer.music.load(path.join(self.sound_dir, "menumusic.ogg"))
        pg.mixer.music.play(loops = -1)
        pg.mixer.music.set_volume(0.75)
        mouse_pos = pg.mouse.get_pos()
        mouse_click = pg.mouse.get_pressed()

        self.screen.blit(self.scaled_menu_bg, (0, 0))
        self.draw_text('karmaticarcade', "Get Ducked!", 48, black, self.screen_width / 2, self.screen_height * 1 / 4)
        self.start = self.draw_text('karmaticarcade', "Start", 24, black, self.screen_width / 2, self.screen_height * 1 / 2)
        self.exit = self.draw_text('karmaticarcade', "Exit", 24, black, self.screen_width / 2, self.screen_height * 5 / 8)

        self.draw_text('karmaticarcade', "Current High Score - " + str(self.highscore), 24, red, self.screen_width / 2, self.screen_height * 3 / 8)

        if self.joysticks == []:
            self.draw_text('karmaticarcade', "No gamepads detected", 12, black, self.screen_width / 2, self.screen_height - 20)
        else:
            self.draw_text('karmaticarcade', "Gamepads detected - " + str(self.joystick_names), 12, black, self.screen_width / 2, self.screen_height - 20)

        pg.display.update()
        self.wait_for_player_start()
        pg.mixer.music.fadeout(500)

    def show_game_over_screen(self):
        # Game over/continue screen
        pg.mouse.set_visible(True)
        pg.mixer.music.stop()
        mouse_pos = pg.mouse.get_pos()
        mouse_click = pg.mouse.get_pressed()

        self.screen_alpha.fill(white)
        self.screen.blit(self.screen_alpha, (0, 0))
        self.draw_text('karmaticarcade', "Game Over!", 48, black, self.screen_width / 2, self.screen_height * 1 / 4)
        
        self.draw_text('karmaticarcade', "Score - " + str(self.score), 24, black, self.screen_width / 2, self.screen_height * 1 / 2)
        self.draw_text('karmaticarcade', "Hunters - " + str(len(self.enemies)) + "   Boats - " + str(len(self.enemyboats)) + "   Airplanes - " + str(len(self.planes)), 18, black, self.screen_width / 2, self.screen_height * 9 / 16)
        self.ng = self.draw_text('karmaticarcade', "New Game", 24, black, self.screen_width / 2, self.screen_height * 5 / 8)
        self.exit = self.draw_text('karmaticarcade', "Exit", 24, black, self.screen_width / 2, self.screen_height * 3 / 4)
        
        if self.score > self.highscore:
            self.highscore = self.score
            self.draw_text('karmaticarcade', "New High Score!", 36, red, self.screen_width / 2, self.screen_height * 3 / 8)
            with open(path.join(self.dir, high_score_file), 'w') as f:
                f.write(str(self.score))
        else:
            self.draw_text('karmaticarcade', "High Score - " + str(self.highscore), 24, black, self.screen_width / 2, self.screen_height * 3 / 8)
        self.gameover.play()
        pg.display.update()
        self.wait_for_player_gameover()
        self.new_game()

    def show_quit_screen(self):
        # Game quit splash screen
        pg.mouse.set_visible(True)
        pg.mixer.music.set_volume(0.25)
        mouse_pos = pg.mouse.get_pos()
        mouse_click = pg.mouse.get_pressed()

        self.screen_alpha.fill(white)
        self.screen.blit(self.screen_alpha, (0, 0))
        self.draw_text('karmaticarcade', "Quit to Menu?", 48, black, self.screen_width / 2, self.screen_height * 1 / 4)
        self.yes = self.draw_text('karmaticarcade', "Yes", 24, black, self.screen_width / 2, self.screen_height * 1 / 2)
        self.no = self.draw_text('karmaticarcade', "No", 24, black, self.screen_width / 2, self.screen_height * 5 / 8)
        pg.display.update()
        self.wait_for_player_quit()

    def wait_for_player_start(self):
        waiting = True
        
        while waiting:
            mouse_pos = pg.mouse.get_pos()

            pg.display.update()
            self.clock.tick(FPS)

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.running = False
                    pg.quit()
                    sys.exit()
                if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    waiting = False
                    self.running = False
                    pg.quit()
                    sys.exit()

                if self.start.left <= mouse_pos[0] <= self.start.right and self.start.top <= mouse_pos[1] <= self.start.bottom:
                    self.draw_text('karmaticarcade', "Start", 24, red, self.screen_width / 2, self.screen_height * 1 / 2)
                    self.draw_text('karmaticarcade', "-", 24, black, self.start.left - 15, self.start.top + 2)
                    self.draw_text('karmaticarcade', "-", 24, black, self.start.right + 15, self.start.top + 2)
                    if event.type == pg.MOUSEBUTTONUP:
                        pg.mixer.find_channel(True).play(self.button_click_sound)
                        waiting = False
                        self.new_game()
                else:
                    self.draw_text('karmaticarcade', "Start", 24, black, self.screen_width / 2, self.screen_height * 1 / 2)
                    self.draw_text('karmaticarcade', "-", 24, white, self.start.left - 15, self.start.top + 2)
                    self.draw_text('karmaticarcade', "-", 24, white, self.start.right + 15, self.start.top + 2)

                if self.exit.left <= mouse_pos[0] <= self.exit.right and self.exit.top <= mouse_pos[1] <= self.exit.bottom:
                    self.draw_text('karmaticarcade', "Exit", 24, red, self.screen_width / 2, self.screen_height * 5 / 8)
                    self.draw_text('karmaticarcade', "-", 24, black, self.exit.left - 15, self.exit.top + 2)
                    self.draw_text('karmaticarcade', "-", 24, black, self.exit.right + 15, self.exit.top + 2)
                    if event.type == pg.MOUSEBUTTONUP:
                        pg.mixer.find_channel(True).play(self.button_click_sound)
                        pg.quit()
                        sys.exit()
                else:
                    self.draw_text('karmaticarcade', "Exit", 24, black, self.screen_width / 2, self.screen_height * 5 / 8)
                    self.draw_text('karmaticarcade', "-", 24, white, self.exit.left - 15, self.exit.top + 2)
                    self.draw_text('karmaticarcade', "-", 24, white, self.exit.right + 15, self.exit.top + 2)

    def wait_for_player_gameover(self):
        waiting = True  

        while waiting:
            mouse_pos = pg.mouse.get_pos()
            pg.display.update()
            self.clock.tick(FPS)

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.running = False
                    pg.quit()
                    sys.exit()
                if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    waiting = False
                    self.running = False
                    self.show_start_screen()

                if self.ng.left <= mouse_pos[0] <= self.ng.right and self.ng.top <= mouse_pos[1] <= self.ng.bottom:
                    self.ng = self.draw_text('karmaticarcade', "New Game", 24, red, self.screen_width / 2, self.screen_height * 5 / 8)
                    self.draw_text('karmaticarcade', "-", 24, black, self.ng.left - 15, self.ng.top + 2)
                    self.draw_text('karmaticarcade', "-", 24, black, self.ng.right + 15, self.ng.top + 2)
                    if event.type == pg.MOUSEBUTTONUP:
                        pg.mixer.find_channel(True).play(self.button_click_sound)
                        waiting = False
                        self.new_game()
                else:
                    self.ng = self.draw_text('karmaticarcade', "New Game", 24, black, self.screen_width / 2, self.screen_height * 5 / 8)
                    self.draw_text('karmaticarcade', "-", 24, white, self.ng.left - 15, self.ng.top + 2)
                    self.draw_text('karmaticarcade', "-", 24, white, self.ng.right + 15, self.ng.top + 2)

                if self.exit.left <= mouse_pos[0] <= self.exit.right and self.exit.top <= mouse_pos[1] <= self.exit.bottom:
                    self.exit = self.draw_text('karmaticarcade', "Exit", 24, red, self.screen_width / 2, self.screen_height * 3 / 4)
                    self.draw_text('karmaticarcade', "-", 24, black, self.exit.left - 15, self.exit.top + 2)
                    self.draw_text('karmaticarcade', "-", 24, black, self.exit.right + 15, self.exit.top + 2)
                    if event.type == pg.MOUSEBUTTONUP:
                        pg.mixer.find_channel(True).play(self.button_click_sound)
                        waiting = False
                        self.running = False
                        self.show_start_screen()
                else:
                    self.exit = self.draw_text('karmaticarcade', "Exit", 24, black, self.screen_width / 2, self.screen_height * 3 / 4)
                    self.draw_text('karmaticarcade', "-", 24, white, self.exit.left - 15, self.exit.top + 2)
                    self.draw_text('karmaticarcade', "-", 24, white, self.exit.right + 15, self.exit.top + 2)

    def wait_for_player_quit(self):
        waiting = True  

        while waiting:
            mouse_pos = pg.mouse.get_pos()
            pg.display.update()
            self.clock.tick(FPS)

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.running = False
                    pg.quit()
                    sys.exit()
                if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    waiting = False
                    self.playing = True
                    pg.mixer.music.set_volume(0.75)   

                if self.yes.left <= mouse_pos[0] <= self.yes.right and self.yes.top <= mouse_pos[1] <= self.yes.bottom:
                    self.yes = self.draw_text('karmaticarcade', "Yes", 24, red, self.screen_width / 2, self.screen_height * 1 / 2)
                    self.draw_text('karmaticarcade', "-", 24, black, self.yes.left - 15, self.yes.top + 2)
                    self.draw_text('karmaticarcade', "-", 24, black, self.yes.right + 15, self.yes.top + 2)
                    if event.type == pg.MOUSEBUTTONUP:
                        pg.mixer.find_channel(True).play(self.button_click_sound)
                        waiting = False
                        self.show_start_screen()
                else:
                    self.yes = self.draw_text('karmaticarcade', "Yes", 24, black, self.screen_width / 2, self.screen_height * 1 / 2)
                    self.draw_text('karmaticarcade', "-", 24, white, self.yes.left - 15, self.yes.top + 2)
                    self.draw_text('karmaticarcade', "-", 24, white, self.yes.right + 15, self.yes.top + 2)

                if self.no.left <= mouse_pos[0] <= self.no.right and self.no.top <= mouse_pos[1] <= self.no.bottom:
                    self.no = self.draw_text('karmaticarcade', "No", 24, red, self.screen_width / 2, self.screen_height * 5 / 8)
                    self.draw_text('karmaticarcade', "-", 24, black, self.no.left - 15, self.no.top + 2)
                    self.draw_text('karmaticarcade', "-", 24, black, self.no.right + 15, self.no.top + 2)
                    if event.type == pg.MOUSEBUTTONUP:
                        pg.mixer.find_channel(True).play(self.button_click_sound)
                        waiting = False
                        self.playing = True
                        pg.mixer.music.set_volume(0.75)                      
                else:
                    self.no = self.draw_text('karmaticarcade', "No", 24, black, self.screen_width / 2, self.screen_height * 5 / 8)
                    self.draw_text('karmaticarcade', "-", 24, white, self.no.left - 15, self.no.top + 2)
                    self.draw_text('karmaticarcade', "-", 24, white, self.no.right + 15, self.no.top + 2)


game = Game()
game.show_start_screen()

while game.running:
    game.new_game()
    game.show_game_over_screen()

pg.quit()
sys.exit()
