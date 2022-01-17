from pygame import *
from random import *
import pickle

init()

images = {
    "grass": transform.scale(image.load("images/regular-grass.png"), (128, 128)),
    "tall-grass": transform.scale(image.load("images/tall-grass.png"), (128, 128)),
    "large-rock": image.load("images/large-rock.png"),
    "small-rock": image.load("images/small-rock.png"),
    "wrench": transform.scale(image.load("images/wrench.png"), (128, 128)),
    "magnet": transform.scale(image.load("images/magnet.png"), (128, 128)),
    "doublemoney": transform.scale(image.load("images/doublemoney.png"), (128, 128)),
}

dilofont = font.Font("fonts/dilofont.ttf", 30)

def generate_level(level):
    for row in level:
        row.remove(row[0])
        randnum = randint(1, 10000)
        if randnum >= 6500: row.append("tall-grass") # 35% chance
        elif randnum >= 6350: row.append("large-rock") # 1.5% chance
        elif randnum >= 6200: row.append("small-rock") # 1.5% chance
        elif randnum >= 6100: row.append("wrench") # 1% chance
        elif randnum >= 6080: row.append("magnet") # 0.2% chance
        elif randnum >= 6060: row.append("doublemoney") # 0.2% chance
        else: row.append("grass")
    return level

def draw_level(screen, level, displacement, startpos = (0, 0)):
    for row in range(len(level)):
        for col in range(len(level[row])):
            if level[row][col] != "tall-grass": screen.blit(images["grass"], (col * 128 - displacement + startpos[0], row * 128 + startpos[1]))
            screen.blit(images[level[row][col]], (col * 128 - displacement + startpos[0], row * 128 + startpos[1]))
    
def draw_ui(screen, pd, score, speed):
    health = pd.health
    max_health = pd.maxhealth
    money = pd.money
    highscore = pd.highscore

    health_text = dilofont.render(f"{int(health)}/{int(max_health)}", True, (255, 255, 255))
    money_text = dilofont.render(f"#{money:.2f}", True, (255, 255, 255))
    score_text = dilofont.render(f"Score: {score}", True, (255, 255, 255))
    hscore_text = dilofont.render(f"Highscore: {highscore}", True, (255, 255, 255))
    speed_text = dilofont.render(f"Speed: {round(speed, 1)}", True, (255, 255, 255))

    # ui bar bg
    draw.rect(screen, (39, 255, 50), (0, 640, 1152, 62))
    #

    # health bar
    draw.rect(screen, (255, 0, 0), (20, 655, 300, 30))
    draw.rect(screen, (0, 110, 0), (20, 655, health/max_health*300, 30))
    screen.blit(health_text, (20, 655))
    #

    # money
    money_bg_width = money_text.get_width() + 10
    draw.rect(screen, (0, 110, 0), (330, 655, money_bg_width, 30))
    screen.blit(money_text, (335, 655))
    #

    # score
    score_bg_width = score_text.get_width() + 10
    draw.rect(screen, (0, 110, 0), (340 + money_bg_width, 655, score_bg_width, 30))
    screen.blit(score_text, (340 + money_bg_width + 5, 655))
    #

    # highscore
    hscore_bg_width = hscore_text.get_width() + 10
    draw.rect(screen, (0, 110, 0), (350 + money_bg_width + score_bg_width, 655, hscore_bg_width, 30))
    screen.blit(hscore_text, (350 + money_bg_width + score_bg_width + 5, 655))
    #

    # speed
    speed_bg_width = speed_text.get_width() + 10
    draw.rect(screen, (0, 110, 0), (350 + money_bg_width + score_bg_width + hscore_bg_width, 655, speed_bg_width, 30))
    screen.blit(speed_text, (350 + money_bg_width + score_bg_width + hscore_bg_width + 5, 655))

def draw_button(screen, pos, width, height, col, text):
    draw.rect(screen, col, Rect(pos[0], pos[1], width, height))
    draw.circle(screen, col, (pos[0], pos[1]+height/2), height/2)
    draw.circle(screen, col, (pos[0]+width, pos[1]+height/2), height/2)
    screen.blit(text, (pos[0] + width/2 - text.get_width()/2, pos[1] + height/2 - text.get_height()/2))

    # return a hitbox for clicking
    return Rect(pos[0] - height/2, pos[1], width + height, height)


# load_data, save_data are from https://www.askpython.com/python/examples/save-data-in-python
def load_data():
    try:
        player_data = 'player_data.pickle'
        with open(player_data, 'rb') as pd:
            return pickle.load(pd)
    except:
        save_data(GameData())
        load_data()

def save_data(data):
    # this code is from the internet
    player_data = 'player_data.pickle'
    with open(player_data, 'wb') as pd:
        pickle.dump(data, pd)

# resets the data to inital values
def reset_data():
    save_data(GameData())
    return load_data()

class GameData():
    def __init__(self):
        # game and player attributes
        self.mower = "Basic"
        self.money = 6969696969669696969
        self.health = 100
        self.maxhealth = 100
        self.highscore = 0
        self.moneymultiplier = 1
        self.healthmultiplier = 1

        # mowers
        self.ownedmowers = ["Basic"]

        # powerup levels
        self.wrenchlevel = 0
        self.magnetlevel = 0
        self.doublemoneylevel = 0

        # attribute level
        self.maxhealthlevel = 0

        # settings attributes
        self.music = True
        self.volume = 0.5