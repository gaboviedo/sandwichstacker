import time
import pygame
from pygame import font
from pygame.locals import *
import sys
import random




# Globals
HEIGHT = 450
WIDTH = 400
ACC = 0.5
FRIC = -0.12
FPS = 60
SPEEDINCREASER=1
GOODIMAGELIST=['assets/egg.png','assets/ham.png','assets/lettuce.png','assets/cheese.png','assets/tomato.png']
BADIMAGELIST=['assets/badEgg.png','assets/badHam.png','assets/dirtysock.png']
ENDCAP='assets/bread.png'

#initializers
pygame.init()
vec = pygame.math.Vector2  # 2 for two dimensional
FramePerSec = pygame.time.Clock()
displaysurface = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game")




# Player class controls the bottom slice of bread
# the goal of the game is to stack as tasty of a sandwich as if possible:
#     The game ends when a second slice of bread is added (this is the win condition); when the score falls below zero (lose condition);
#     when the damage (this is an invisible to the player attribute), reaches above three.
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.surf = pygame.transform.scale(pygame.image.load("assets/bread.png"),(30,30))
        self.rect = self.surf.get_rect()
        self.pos = vec((5, 430))
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.jumping = False
        self.score = 0
        self.damage=0


# this is the movement logic for the player character, it allows for screen warping, drag, and acceleration
    def move(self):
        self.acc = vec(0, 0)

        pressed_keys = pygame.key.get_pressed()

        if pressed_keys[K_LEFT]:
            self.acc.x = -ACC
        if pressed_keys[K_RIGHT]:
            self.acc.x = ACC

        self.acc.x += self.vel.x * FRIC
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc

        if self.pos.x > WIDTH:
            self.pos.x = 0
        if self.pos.x < 0:
            self.pos.x = WIDTH

        self.rect.midbottom = self.pos


# platform class for the floor
class platform(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.surf = pygame.Surface((random.randint(50,100), 12))
        self.surf.fill((0, 255, 0))
        self.rect = self.surf.get_rect(center=(random.randint(0, WIDTH - 10),
                                               random.randint(0, HEIGHT - 30)))
        self.stacked=False
        self.moving = True
    def move(self):
        pass



# used to control the ingredients that fall from the top of the screen
class stackable(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image=pygame.image.load(self.choosefilename(GOODIMAGELIST))
        self.surf=pygame.transform.scale((self.image),(30,30))
        self.pos = vec((10, 360))
        self.rect = self.surf.get_rect()
        self.stacked = False
        self.moving = True
        self.speed = SPEEDINCREASER
    def set_surf(self,surf):
        self.surf = surf

    def animation(self):
        pass


    # controls movement
    def move(self):
        self.acc = vec(0, .5+SPEEDINCREASER)
        hits = (any(map(lambda x: x.stacked and self.rect.colliderect(x), stacks)) or self.rect.colliderect(
            (P1)))

        if self.moving == True:
            if not hits:
                self.animation()

            self.rect.move_ip(0, self.speed)

            if hits:
                self.updateScore()
                self.stacked = True
                self.rect.move_ip(P1.vel.x - .9*(self.rect.midtop[0]-P1.pos.x), -self.speed)
                # if hits the top of screen
                if self.rect.top<10:
                    gameover()


                # P1.pos += (self.speed, 0)
            if self.speed > 0 and self.rect.left > WIDTH:
                self.rect.right = 0
            if self.speed < 0 and self.rect.right < 0:
                self.rect.left = WIDTH
    # decides appearance of stackable item
    def choosefilename(self,filelist):
        chosenpngindex= random.randint(0, len(filelist)-1)
        return filelist[chosenpngindex]

    # updates score and plays sound effect
    def updateScore(self):
            if not self.stacked:
                pygame.mixer.Sound.play(crash_sound)
                P1.score += 1
                # if random.randint(0,4)==0:
                #     plat_gen() #1/5 chance


class badItem(stackable):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load(self.choosefilename(BADIMAGELIST))
        self.surf = pygame.transform.scale(self.image,(30,30))
        self.rect = self.surf.get_rect().inflate(-15,-15)

    def updateScore(self):
        pygame.mixer.Sound.play(err_sound)
        if not self.stacked:
            P1.damage+=1
            P1.score -= 3
            self.kill()
    def animation(self):
        if pygame.time.get_ticks() % 21 == 0:
            transformed = pygame.transform.scale(self.image, (20, 20))
            self.set_surf(transformed)
        elif pygame.time.get_ticks() % 21 == 7:
            transformed = pygame.transform.scale(self.image, (25, 25))
            self.set_surf(transformed)
        elif pygame.time.get_ticks() % 21 == 14:
            transformed = pygame.transform.scale(self.image, (30, 30))
            self.set_surf(transformed)

class endCap(stackable):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('assets/bread.png')
        self.surf = pygame.transform.scale(self.image, (30, 30))
        self.rect = self.surf.get_rect().inflate(-15,-15)

    def updateScore(self):
       if not self.stacked:
           win()
    def animation(self):
        if pygame.time.get_ticks() % 12 == 0:
            transformed = pygame.transform.rotate(self.image, 10)
            transformed = pygame.transform.scale(transformed, (30, 30))
            self.set_surf(transformed)
        elif pygame.time.get_ticks() % 12 == 6:
            transformed = pygame.transform.rotate(self.image, -10)
            transformed = pygame.transform.scale(transformed, (30, 30))
            self.set_surf(transformed)
        # elif pygame.time.get_ticks() % 12 == 8:
        #     transformed = pygame.transform.scale(self.image, (30, 30))
        #     self.set_surf(transformed)


def win():
    high_score = get_high_score()
    pygame.mixer.music.stop()
    pygame.mixer.Sound.play(win_sound)
    pressed_keys = pygame.key.get_pressed()

    f = pygame.font.SysFont("Verdana", 15)  ##

    if P1.score > high_score :
        save_high_score(P1.score)
        entity.kill()
        # time.sleep(10)
        if P1.damage == 0:
            g = f.render("Perfect score, King " + str(P1.score), True, (100, 100, 0))  ##
            background = pygame.transform.scale(pygame.image.load('assets/PerfectScore.png'), (400, 450))
        else:
            g = f.render("New high score " + str(P1.score), True, (100, 100, 0))  ##
            background = pygame.transform.scale(pygame.image.load('assets/Highscore.png'), (400, 450))



    else:
        g = f.render("You need more practice " + str(P1.score), True, (100, 100, 0))  ##
        # entity.kill()
        # time.sleep(1)
        background = pygame.transform.scale(pygame.image.load('assets/win.png'), (400, 450))
    displaysurface.blit(background, (0, 0))
    displaysurface.blit(g, (WIDTH / 2, 10))  ##
    pygame.display.update()

    time.sleep(5)
    pygame.quit()
    sys.exit()

def gameover():
    pygame.mixer.music.stop()
    pygame.mixer.Sound.play(gameover_sound)

    f = pygame.font.SysFont("Verdana", 15)  ##
    g = f.render("GAME OVER "+str(P1.score), True, (0, 255, 0))  ##
    entity.kill()
    time.sleep(1)
    # displaysurface.fill((250, 0, 0))
    displaysurface.blit(g, (WIDTH / 2, 10))  ##
    background = pygame.transform.scale(pygame.image.load('assets/gameover.png'), (400, 450))
    displaysurface.blit(background, (0, 0))
    pygame.display.update()
    time.sleep(4)
    pygame.quit()
    sys.exit()

# unused method for checking whether spawned ingredients are overlapping
# def check(stackable, groupies):
#     if pygame.sprite.spritecollideany(stackable, groupies):
#         return True
#     else:
#         for entity in groupies:
#             if entity == stackable:
#                 continue
#             if (abs(stackable.rect.top - entity.rect.bottom) < 40) and (
#                     abs(stackable.rect.bottom - entity.rect.top) < 40):
#                 return True
#         C = False


def get_high_score():
    # Default high score
    high_score = 0

    # Try to read the high score from a file
    try:
        high_score_file = open("assets/high_score.txt", "r")
        high_score = int(high_score_file.read())
        high_score_file.close()
        print("The high score is", high_score)
    except IOError:
        # Error reading file, no high score
        print("There is no high score yet.")
    except ValueError:
        # There's a file there, but we don't understand the number.
        print("I'm confused. Starting with no high score.")

    return high_score


def save_high_score(new_high_score):
    try:
        # Write the file to disk
        high_score_file = open("assets/high_score.txt", "w")
        high_score_file.write(str(new_high_score))
        high_score_file.close()
    except IOError:
        # Hm, can't write it.
        print("Unable to save the high score.")

def plat_gen():

    randomx = random.randint(2,390)
    generated = random.randint(0,2)
    if generated==0:
        p=stackable()
    elif generated==1:
        p=badItem()
    elif generated==2:
        p = endCap()

    p.rect.midbottom = vec(randomx,0)
    stacks.add(p)
    all_sprites.add(p)


PT1 = platform()
P1 = Player()
PT1.moving = False
PT1.point = False   ##

PT1.surf = pygame.Surface((WIDTH, 20))
PT1.surf.fill((176, 23, 50))
PT1.rect = PT1.surf.get_rect(center=(WIDTH / 2, HEIGHT - 10))

all_sprites = pygame.sprite.Group()
all_sprites.add(PT1)
all_sprites.add(P1)
stacks = pygame.sprite.Group()
stacks.add(PT1)

for x in range(random.randint(3, 10)):
    plat_gen()


pygame.display.set_caption("sandwich stacker")
background = pygame.transform.scale(pygame.image.load('assets/background.png'),(400,450))


soundtrack=pygame.mixer.music.load('assets/jungle.mp3')
pygame.mixer.music.play(-1)
crash_sound = pygame.mixer.Sound("assets/cartoonsplash.mp3")
gameover_sound= pygame.mixer.Sound("assets/spongebob-fail.mp3")
win_sound = pygame.mixer.Sound("assets/rizz-sounds.mp3")
err_sound = pygame.mixer.Sound("assets/error_CDOxCYm.mp3")

# game loop
while True:

    displaysurface.blit(background,(0,0))
    P1.update()
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    # unused, move the camera with player
    # if P1.rect.top <= HEIGHT / 3:
    #     P1.pos.y += abs(P1.vel.y)
    # delete stackables below the floor
    for plat in stacks:
        plat.rect.y += abs(P1.vel.y)
        if plat.rect.top >= HEIGHT:
            plat.kill()
            # plat_gen()
            if random.randint(0, 2)==0:
                plat_gen() # 1/3 chance spawn
                if random.randint(0, 2)==0:
                    plat_gen() # 1/9 chance




    if pygame.time.get_ticks()%2==0:
        SPEEDINCREASER +=.028*.01
    if pygame.time.get_ticks() % 110 == 0:
        plat_gen()

    # displaysurface.fill((0, 0, 0))
    f = pygame.font.SysFont("Verdana", 20)  ##
    g = f.render(str(P1.score), True, (123, 255, 0))  ##
    displaysurface.blit(g, (WIDTH / 2, 10))  ##

    for entity in all_sprites:
        displaysurface.blit(entity.surf, entity.rect)
        entity.move()


    pygame.display.update()
    FramePerSec.tick(FPS)

    if P1.damage >= 3 or P1.score <0:
        for entity in all_sprites:
            gameover()