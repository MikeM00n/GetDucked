# Sprite classes for GetDucked!

import pygame as pg
from pygame.locals import *
import random
from settings import *

vec = pg.math.Vector2

class Spritesheet(object):
    # parse sprite sheets
    def __init__(self, filename):
        self.spritesheet = pg.image.load(filename).convert()

    def get_image(self, x, y, width, height, multiplier):
        image = pg.Surface((width, height))
        image.blit(self.spritesheet, (0,0), (x, y, width, height))
        image = pg.transform.scale(image, (int(round(width * multiplier)), int(round(height * multiplier))))
        return image


class Player(pg.sprite.Sprite):
    def __init__(self, game):
        super().__init__()

        self.game = game
        self.dying = False
        self.flying = True
        self.current_frame = 0
        self.last_update = 0
        self.load_images()
        self.image = self.flying_frames[0]
        self.rect = self.image.get_rect()
        self.rect.center = (int(self.game.screen_width / 4), int(self.game.screen_height / 2))
        self.pos = vec(int(self.game.screen_width / 4), int(self.game.screen_height / 2))
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.health = health

    def load_images(self):
        self.flying_frames = [self.game.spritesheet.get_image(2, 4, 24, 13, player_multiplier),
                              self.game.spritesheet.get_image(28, 1, 25, 16, player_multiplier),
                              self.game.spritesheet.get_image(2, 4, 24, 13, player_multiplier),
                              self.game.spritesheet.get_image(55, 4, 23, 21, player_multiplier)]

        for frame in self.flying_frames:
            frame.set_colorkey(white)

        self.dying_frames = [self.game.spritesheet.get_image(80, 1, 27, 18, player_multiplier),
                             self.game.spritesheet.get_image(109, 2, 34, 18, player_multiplier),
                             self.game.spritesheet.get_image(146, 3, 32, 17, player_multiplier),
                             self.game.spritesheet.get_image(146, 3, 32, 17, player_multiplier)]
                              
        for frame in self.dying_frames:
            frame.set_colorkey(white)

    def update(self, dt):
        self.animate()
        self.acc = vec(0, 1) * self.game.dt
        self.friction = -0.01

        keys = pg.key.get_pressed()

        if keys[pg.K_d] or keys[pg.K_RIGHT]:
            self.acc.x = 0.15
        if keys[pg.K_a] or keys[pg.K_LEFT]:
            self.acc.x = -0.15
        if keys[pg.K_w] or keys[pg.K_UP]:
            self.acc.y = -0.15
        if keys[pg.K_s] or keys[pg.K_DOWN]:
            self.acc.y = 0.15

        try:
            right_left = pg.joystick.Joystick(0).get_axis(0)
            up_down = pg.joystick.Joystick(0).get_axis(1)

            if right_left >= 0.15:
                self.acc.x = 0.15
            if right_left <= -0.15:
                self.acc.x = -0.15
            if up_down <= -0.15:
                self.acc.y = -0.15
            if up_down >= 0.15:
                self.acc.y = 0.15
        except:
            pass

        self.acc.x += self.vel.x * self.friction
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc
        self.rect.center = self.pos

        if self.pos.x > self.game.screen_width - self.rect.width:
            self.pos.x = self.game.screen_width - self.rect.width
            self.vel.x = 0
        if self.pos.x < 0 + self.rect.width:
            self.pos.x = 0 + self.rect.width
            self.vel.x = 0
        if self.pos.y < 0 + self.rect.height:
            self.pos.y = 0 + self.rect.height
            self.vel.y = 0
        if self.pos.y > int(self.game.screen_height * 3 / 4):
            self.pos.y = int(self.game.screen_height * 3 / 4)
            self.vel.y = 0

    def animate(self):
        now = pg.time.get_ticks()

        if self.health <= 0:
            self.health = 0
            self.dying = True
            self.flying = False

        if self.dying:
            if now - self.last_update > 200:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.dying_frames)
                self.image = self.dying_frames[self.current_frame]

                if self.image == self.dying_frames[3]:
                    pg.time.delay(500)
                    self.game.all_sprites.remove(self)
                    self.game.show_game_over_screen()

        if not self.dying:
            self.flying = True
            if now - self.last_update > flap_speed:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.flying_frames)
                self.image = self.flying_frames[self.current_frame]

        self.mask = pg.mask.from_surface(self.image)

    def draw_health(self):
        if self.health > 60:
            col = green
        elif self.health > 30:
            col = yellow
        else:
            col = red
        length = int(200 * self.health / 100)
        self.health_bar = pg.Rect(110, 2, length, 18)
        self.bar_outline = pg.Rect(110, 2, 200, 18)
        pg.draw.rect(self.game.screen, col, self.health_bar)
        pg.draw.rect(self.game.screen, white, self.bar_outline, 2)
        self.game.draw_text('karmaticarcade', "Health:", 18, black, 55, 0)


class Heart(pg.sprite.Sprite):
    def __init__(self, game):
        super().__init__()

        self.game = game
        self.current_frame = 0
        self.last_update = 0
        self.load_images()
        self.image = self.heart_frames[0]
        self.rect = self.image.get_rect()

        self.rect.y = random.randrange(0, int(self.game.screen_height / 2))
        self.rect.x = random.randrange(self.game.screen_width + 250, self.game.screen_width * 5)
        self.speedx = random.randrange(heart_speed[0], heart_speed[1]) * self.game.dt

    def load_images(self):
        self.heart_frames = [self.game.spritesheet.get_image(28, 64, 9, 8, heart_multiplier),
                             self.game.spritesheet.get_image(39, 64, 11, 10, heart_multiplier)]

        for frame in self.heart_frames:
            frame.set_colorkey(white)

    def animate(self):
        now = pg.time.get_ticks()
        if now - self.last_update > random.randrange(heart_beat[0], heart_beat[1]):
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.heart_frames)
            self.image = self.heart_frames[self.current_frame]

    def update(self, dt):
        self.animate()
        self.rect.x -= self.speedx

        if self.rect.right < 0:
            self.rect.x = random.randrange(self.game.screen_width + 250, self.game.screen_width * 5)
            self.speedx = random.randrange(heart_speed[0], heart_speed[1]) * self.game.dt

        self.player_hit = pg.sprite.spritecollide(self.game.player, self.game.hearts, True)
        if self.player_hit:
            self.game.player.health += heart_health
            if self.game.player.health >= 100:
                self.game.player.health = 100
            pg.mixer.find_channel(True).play(self.game.health_pickup_sound)
            self.game.score += heart_points
            self.game.all_sprites.remove(self.game.heart)


class Enemy(pg.sprite.Sprite):
    def __init__(self, game):
        super().__init__()

        self.game = game
        self.current_frame = 0
        self.last_update = 0
        self.load_images()
        self.image = self.hunter_frames[0]
        self.rect = self.image.get_rect()
        self.rect.bottom = random.randrange(self.game.screen_height - 75, self.game.screen_height - 15)
        self.rect.x = random.randrange(self.game.screen_width + 250, self.game.screen_width + 500)
        self.speedx = random.randrange(drift_speed[0], drift_speed[1]) * self.game.dt

    def load_images(self):
        self.hunter_frames = [self.game.spritesheet.get_image(2, 31, 18, 23, enemy_multiplier),
                              self.game.spritesheet.get_image(18, 28, 15, 26, enemy_multiplier), 
                              self.game.spritesheet.get_image(31, 28, 15, 26, enemy_multiplier),
                              self.game.spritesheet.get_image(44, 31, 18, 23, enemy_multiplier),
                              self.game.spritesheet.get_image(31, 28, 15, 26, enemy_multiplier),
                              self.game.spritesheet.get_image(18, 28, 15, 26, enemy_multiplier)]

        for frame in self.hunter_frames:
            frame.set_colorkey(white)

    def animate(self):
        now = pg.time.get_ticks()
        if now - self.last_update > random.randrange(aim_speed[0], aim_speed[1]):
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.hunter_frames)
            self.image = self.hunter_frames[self.current_frame]

    def update(self, dt):
        self.animate()
        self.rect.x -= self.speedx
        if self.rect.right < 0:
            self.rect.bottom = random.randrange(self.game.screen_height - 75, self.game.screen_height - 15)
            self.rect.x = random.randrange(self.game.screen_width, self.game.screen_width * 5)
            self.speedx = random.randrange(drift_speed[0], drift_speed[1]) * self.game.dt

        self.player_hit = pg.sprite.spritecollide(self.game.player, self.game.bullets, True)
        if self.player_hit:
            pg.mixer.find_channel(True).play(self.game.hit_sound)
            self.game.player.pos[1] -= 10
            self.game.player.health -= bullet_damage
            self.game.all_sprites.remove(self.game.bullet)

    def shoot(self):
        now = pg.time.get_ticks()
        if now - self.last_update > random.randrange(200, 500):
            self.last_update = now
            pg.mixer.find_channel(True).play(self.game.shoot_sound)
            self.game.bullet = Bullet(self.game.enemy.rect.centerx, self.game.enemy.rect.top, self)
            self.game.bullets.add(self.game.bullet)
            self.game.all_sprites.add(self.game.bullet)


class EnemyBoat(pg.sprite.Sprite):
    def __init__(self, game):
        super().__init__()

        self.game = game
        self.current_frame = 0
        self.last_update = 0
        self.load_images()
        self.image = self.boat_frames[0]
        self.rect = self.image.get_rect()
        self.rect.bottom = random.randrange(self.game.screen_height - 75, self.game.screen_height - 15)
        self.rect.x = random.randrange(self.game.screen_width + 250, self.game.screen_width + 500)
        self.speedx = random.randrange(boat_speed[0], boat_speed[1]) * self.game.dt

    def load_images(self):
        self.boat_frames = [self.game.spritesheet.get_image(68, 28, 63, 25, boat_multiplier)]

        for frame in self.boat_frames:
            frame.set_colorkey(white)

    def update(self, dt):
        self.rect.x -= self.speedx
        if self.rect.right < 0:
            self.rect.bottom = random.randrange(self.game.screen_height - 75, self.game.screen_height - 15)
            self.rect.x = random.randrange(self.game.screen_width, self.game.screen_width * 5)
            self.speedx = random.randrange(boat_speed[0], boat_speed[1]) * self.game.dt

        self.player_hit = pg.sprite.spritecollide(self.game.player, self.game.bullets, True)
        if self.player_hit:
            pg.mixer.find_channel(True).play(self.game.hit_sound)
            self.game.player.pos[1] -= 10
            self.game.player.health -= 1
            self.game.all_sprites.remove(self.game.bullet)

    def shoot(self):
        pg.mixer.find_channel(True).play(self.game.shoot_sound)
        self.game.bullet = Bullet(self.game.enemyboat.rect.centerx, self.game.enemyboat.rect.top, self)
        self.game.bullets.add(self.game.bullet)
        self.game.all_sprites.add(self.game.bullet)
        self.game.bullet2 = Bullet(self.game.enemyboat.rect.centerx-50, self.game.enemyboat.rect.top, self)
        self.game.bullets.add(self.game.bullet2)
        self.game.all_sprites.add(self.game.bullet2)


class Bullet(pg.sprite.Sprite):
    def __init__(self, x, y, game):
        super().__init__()

        self.game = game
        self.image = pg.Surface(bullet_size)
        self.image.fill(red)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.bullet_angle = random.randrange(bullet_angle[0], bullet_angle[1])
        self.bullet_speed = random.randrange(bullet_speed[0], bullet_speed[1])

    def update(self, dt):
        self.rect.x += self.bullet_angle
        self.rect.y += self.bullet_speed * dt

        if self.rect.bottom <= 0:
            self.kill()


class Airplane(pg.sprite.Sprite):
    def __init__(self, game):
        super().__init__()

        self.game = game
        self.current_frame = 0
        self.last_update = 0
        self.load_images()
        self.image = self.airplane_frames[0]
        self.rect = self.image.get_rect()

        self.rect.y = random.randrange(0, int(self.game.screen_height * 3 / 4))
        self.rect.x = random.randrange(self.game.screen_width + 250, self.game.screen_width * 5)
        self.speedx = random.randrange(airplane_speed[0], airplane_speed[1]) * self.game.dt

    def load_images(self):
        self.airplane_frames = [self.game.spritesheet.get_image(2, 77, 75, 26, airplane_multiplier),
                                self.game.spritesheet.get_image(2, 75, 75, 28, airplane_multiplier)]

        for frame in self.airplane_frames:
            frame.set_colorkey(white)

    def animate(self):
        now = pg.time.get_ticks()
        if now - self.last_update > random.randrange(airplane_bounce[0], airplane_bounce[1]):
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.airplane_frames)
            self.image = self.airplane_frames[self.current_frame]
        self.mask = pg.mask.from_surface(self.image)

    def update(self, dt):
        self.animate()
        self.rect.x -= self.speedx

        if self.game.screen_width > self.rect.x < self.game.screen_width:
            pg.mixer.find_channel(True).play(self.game.airplane_sound)

        if self.rect.right < 0:
            self.rect.x = random.randrange(self.game.screen_width + 250, self.game.screen_width * 5)
            self.speedx = random.randrange(airplane_speed[0], airplane_speed[1]) * self.game.dt

        self.player_hit = pg.sprite.spritecollide(self.game.player, self.game.planes, False, pg.sprite.collide_mask)
        if self.player_hit:
            pg.mixer.find_channel(True).play(self.game.crash_sound)
            self.game.player.pos[1] += 250
            self.game.player.health -= 25


class Cloud(pg.sprite.Sprite):
    def __init__(self, game):
        super().__init__()

        self.game = game
        self.current_frame = 0
        self.last_update = 0
        self.load_images()
        self.image = self.cloud_frames[0]
        self.rect = self.image.get_rect()

        self.rect.y = random.randrange(0, int(self.game.screen_height / 2))
        self.rect.x = random.randrange(self.game.screen_width + 250, self.game.screen_width * 5)
        self.speedx = random.randrange(cloud_speed[0], cloud_speed[1]) * self.game.dt

    def load_images(self):
        self.cloud_frames = [self.game.spritesheet.get_image(52, 58, 44, 16, random.randrange(cloud_multiplier[0], cloud_multiplier[1]))]

        for frame in self.cloud_frames:
            frame.set_colorkey(white)

    def update(self, dt):
        self.rect.x -= self.speedx

        if self.rect.right < 0:
            self.rect.x = random.randrange(self.game.screen_width + 250, self.game.screen_width * 5)
            self.speedx = random.randrange(cloud_speed[0], cloud_speed[1]) * self.game.dt