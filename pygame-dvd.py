import pygame
import random
import time
import math
from Twitch_Connection import Twitch

TWITCH_CHANNEL = 'mr_cheese_22'

pygame.init()
pygame.mixer.init()
winner_sound = pygame.mixer.Sound("winner_sound.mp3")
DISPLAY_WIDTH = 1920
DISPLAY_HEIGHT = 1080
DVD_SIZE = 100
MOVE_SPEED = 10
screen = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
clock = pygame.time.Clock()
name_text = pygame.font.Font(None, 28)
end_screen_text = pygame.font.Font(None, 100)
running = True
DVD_LIST = []
CHEESE = (255, 223, 102)
DVD_IMG = pygame.image.load('dvd-logo.png')
DVD_COUNT = 1
DVD_MAX = 20

class COORD:
    def __init__(self):
        self.x = random.randint(DVD_SIZE, DISPLAY_WIDTH - DVD_SIZE)
        self.y = random.randint(DVD_SIZE, DISPLAY_HEIGHT - DVD_SIZE)

class DVD:
    def __init__(self, name, color, coord: COORD):
        self.name = name
        self.color = color
        self.coord = coord
        self.speed_right = random.choice([-MOVE_SPEED, MOVE_SPEED])
        self.speed_down = random.choice([-MOVE_SPEED, MOVE_SPEED])
        self.attack = ""

    def move_dvd(self):
        if not (0 < self.coord.x < DISPLAY_WIDTH - DVD_SIZE) and not (0 < (self.coord.y) < DISPLAY_HEIGHT - DVD_SIZE):
            return True
        if not (0 < self.coord.x < DISPLAY_WIDTH - DVD_SIZE):
            self.speed_right = -self.speed_right
        if not (0 < (self.coord.y) < DISPLAY_HEIGHT - DVD_SIZE):
            self.speed_down = -self.speed_down
        self.coord.x += self.speed_right
        self.coord.y += self.speed_down
        return False
   
    def tint_image(self, image):
        tinted = image.copy()
        tinted.fill((0, 0, 0, 255), special_flags=pygame.BLEND_RGBA_MULT)
        color = self.color + (255,)
        tinted.fill(color[:3] + (0,), special_flags=pygame.BLEND_RGBA_ADD)
        return tinted

    def draw_dvd(self):
        dvd_image = pygame.transform.scale(DVD_IMG, (DVD_SIZE, DVD_SIZE))
        dvd_image = self.tint_image(dvd_image)
        text = name_text.render(self.name, True, self.color)
        text_rect = text.get_rect()
        text_rect.center = ((self.coord.x + DVD_SIZE/2), (self.coord.y))
        screen.blit(text, text_rect)
        screen.blit(dvd_image, (self.coord.x, self.coord.y))

t = Twitch()
t.twitch_connect(TWITCH_CHANNEL)
players = []

while running:
    received_messages = t.twitch_receive_messages()
    for message in received_messages:
        if message.get('message').startswith('!play') and DVD_COUNT <= DVD_MAX:
            username = message.get('username').lower()
            if not any(dvd.name == username for dvd in DVD_LIST):
                color = (random.randrange(0,255), random.randrange(0,255), random.randrange(0,255))
                user_dvd = DVD(username, color, COORD())
                DVD_LIST.append(user_dvd)
                DVD_COUNT += 1
                print(f"\033[32mDVD created --> {username}\033[0m")
        if message.get('message').startswith('!attack '):
            attacker = message.get('username').lower()
            username = message.get('message')[9:].lower()
            if any(dvd.name == username for dvd in DVD_LIST):
                for dvd in DVD_LIST:
                    if dvd.name == attacker:
                        dvd.attack = username
                        print(f"{attacker} is trying to attack {username}!")
                        break
                        
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE and pygame.K_LSHIFT:
                running = False
            if event.key == pygame.K_SPACE:
                color = (random.randrange(0,255), random.randrange(0,255), random.randrange(0,255))
                temp_DVD = DVD("DVD" + str(DVD_COUNT), color, COORD())
                DVD_LIST.append(temp_DVD)
                DVD_COUNT += 1

    screen.fill(CHEESE)
    for item in DVD_LIST:
        item.draw_dvd()
        if (item.move_dvd()):
            screen.fill(CHEESE)
            text = end_screen_text.render(item.name, True, item.color)
            print(f"Winner ---> {item.name}")
            DVD_LIST = []
            text_rect = text.get_rect()
            text_rect.center = ((DISPLAY_WIDTH/2), (DISPLAY_HEIGHT/2))
            screen.blit(text, text_rect)
            pygame.display.flip()
            winner_sound.play()
            time.sleep(5)
            exit()
        if not (item.attack == ""):
            for dvd in DVD_LIST:
                if (dvd.name == item.attack):
                    x1 = (dvd.coord.x + DVD_SIZE/2)
                    x2 = (item.coord.x + DVD_SIZE/2)
                    y1 = (dvd.coord.y + DVD_SIZE/2)
                    y2 = (item.coord.y + DVD_SIZE/2)
                    x_diff = x1 - x2
                    y_diff = y1 - y2
                    x_diff = x_diff**2
                    y_diff = y_diff**2
                    distence = math.sqrt(x_diff + y_diff)
                    if (distence <= (DVD_SIZE * 0.9)):
                        if (dvd.attack == item.name):
                            print(f"\033[31m{item.name} has stubbed their toe...\033[0m")
                            DVD_LIST = [dvd2 for dvd2 in DVD_LIST if dvd2.name != item.name]
                        print(f"\033[31m{dvd.name} tripped...\033[0m")
                        DVD_LIST = [dvd2 for dvd2 in DVD_LIST if dvd2.name != dvd.name]
                        item.attack = ""
 
    pygame.display.flip()

    clock.tick(60)

pygame.quit()