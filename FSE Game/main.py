from pygame import *
import sys
from functions import *

init()
screenX, screenY = 1152, 704
screen=display.set_mode((screenX,screenY))
RED = (255,0,0)
GREY = (127,127,127)
BLACK = (0,0,0)
BLUE = (0,0,255)
GREEN = (0,255,0)
YELLOW = (255,255,0)

# load and store data
game_data = load_data()

# [image, cost, buffs/multipliers: (money, health), owned]
lawn_mowers = {
    "Basic": [transform.rotate(image.load("images/lawnmower-red.png"), 180), 0, (0, 0), True],
    "The Tank": [transform.rotate(image.load("images/lawnmower-blue.png"), 180), 500, (0, 0.5), False],
    "The Money Maker": [transform.rotate(image.load("images/lawnmower-yellow.png"), 180), 750, (0.5, 0), False],
    "Mega Mower": [transform.rotate(image.load("images/lawnmower-rainbow.png"), 180), 1500, (1, 1), False],
}

# the amount of damage it does
obstacles = {
    "large-rock": 50,
    "small-rock": 25
}

powerups = {
    "wrench": [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000], # [how much health is restored]
    "magnet": [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 20], # [duration]
    "doublemoney": [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 20] # [duration]
}

def main_menu():
    if game_data.music:
        # all bgm music by Arevin on Newgrounds
        mixer.music.load("sounds/menu-bgm.mp3")
        mixer.music.play(-1)
        mixer.music.set_volume(game_data.volume)

    title = transform.scale(image.load("images/title.png"), (1152, 704))

    buttons = {
        "start": [image.load("images/play-button.png"), image.load("images/play-button-hover.png"), False, (800, 50)],
        "shop": [image.load("images/shop-button.png"), image.load("images/shop-button-hover.png"), False, (800, 200)],
        "upgrades": [image.load("images/upgrades-button.png"), image.load("images/upgrades-button-hover.png"), False, (800, 350)],
        "settings": [image.load("images/settings-button.png"), image.load("images/settings-button-hover.png"), False, (800, 500)],
        "credits": [image.load("images/credits-button.png"), image.load("images/credits-button-hover.png"), False, (25, 500)],
    }

    displacement = 0

    buttonclickedevent = USEREVENT + 1
    buttonclicked = ""

    # create the starting part for the background
    level = [["grass" for _ in range(screenX//128 + 1)] for _ in range(screenY//128)]

    # generate level 10 times, to make it seem like the level has been running for a while
    for _ in range(10): level = generate_level(level)
    
    running = True
    while running:
        for evt in event.get():
            if evt.type == QUIT:
                save_data(game_data)
                running = False
                sys.exit()
            if evt.type == MOUSEBUTTONDOWN:
                for button in buttons:
                    if buttons[button][0].get_rect(topleft=buttons[button][3]).collidepoint(mx, my):
                        buttonclicked = button
                        if game_data.music:
                            mixer.music.unload()
                            mixer.music.load("sounds/click1.wav")
                            mixer.music.set_volume(1)
                            mixer.music.play()
                        time.set_timer(buttonclickedevent, 100, 1)
            if evt.type == buttonclickedevent:
                if game_data.music: mixer.music.unload()
                if buttonclicked == "start": game()
                if buttonclicked == "settings": settings()
                if buttonclicked == "shop": shop()
                if buttonclicked == "upgrades": upgrades()

        mx, my = mouse.get_pos()
        # generate level for main menu background
        if displacement >= 128:
            level = generate_level(level)
            displacement = 0
        displacement += 4

        for button in buttons:
            if buttons[button][0].get_rect(topleft=buttons[button][3]).collidepoint(mx, my):
                if not buttons[button][2]:
                    buttons[button][2] = True
            else:
                buttons[button][2] = False

        # draw stuff
        screen.fill((0, 150, 50))
        draw_level(screen, level, displacement, (0, 32))
        screen.blit(title, (0, 32))
        for button in buttons:
            if not buttons[button][2]:
                screen.blit(buttons[button][0], buttons[button][3])
            else:
                screen.blit(buttons[button][1], buttons[button][3])
        display.flip()

myClock = time.Clock()
running = True

def game():
    if game_data.music:
        mixer.music.load("sounds/game-bgm.mp3")
        mixer.music.play(-1)
        mixer.music.set_volume(game_data.volume)
    

    # player variables
    player_pos = 2*128

    displacement = 0

    # reset values to base before applying multipliers
    game_data.maxhealth = 100 + 25 * game_data.maxhealthlevel
    game_data.health = 100

    game_data.moneymultiplier = 1
    game_data.healthmultiplier = 1

    # move this to shop function so this only happens whe you buy lawn mower and at the very beginning of the game
    game_data.moneymultiplier += lawn_mowers[game_data.mower][2][0]
    game_data.healthmultiplier += lawn_mowers[game_data.mower][2][1]

    game_data.maxhealth *= game_data.healthmultiplier
    game_data.health = game_data.maxhealth

    score = 0

    use_magnet = False
    magnet_time = 0
    magnet_timer = 0

    doublemoney = False
    doublemoney_time = 0
    doublemoney_timer = 0
    default_moneymultiplier = game_data.moneymultiplier

    # create the starting map, which will always be plain grass
    level = [["grass" for _ in range(screenX//128 + 1)] for _ in range(screenY//128)]

    # game loop
    # draw start of level
    draw_level(screen, level, displacement)

    running = True
    while running:
        for evt in event.get():
            if evt.type == QUIT:
                save_data(game_data)
                running = False
                if game_data.music: mixer.music.unload()
                if score > game_data.highscore:
                    game_data.highscore = score
                    # to do: display new highscore screen
                main_menu()
            if evt.type == KEYDOWN:
                k = key.get_pressed()
                if k[K_UP] and player_pos > 0:
                    player_pos -= 128
                elif k[K_DOWN] and player_pos < 512:
                    player_pos += 128
                        
        mx, my = mouse.get_pos()
        mb = mouse.get_pressed()

        if game_data.health <= 0: time.set_timer(QUIT, 10, 1)

        # generate level
        if displacement >= 128:
            level = generate_level(level)
            score += 1
            displacement = 0
        
        # change speed depending on score
        # slowly gets faster as time score increases
        if score/60 + 4 < 32:
            speed = score/60 + 4
            displacement += speed
        else:
            speed = 32
            displacement += speed


        collided_object = level[player_pos//128][1]

        if collided_object == "tall-grass":
            level[player_pos//128][1] = "grass"
            game_data.money += 1 * game_data.moneymultiplier
        if collided_object in obstacles:
            level[player_pos//128][1] = "grass"
            game_data.health -= obstacles[collided_object]
        if collided_object in powerups:
            if collided_object == "wrench":
                level[player_pos//128][1] = "grass"
                game_data.health += powerups["wrench"][game_data.wrenchlevel]
                if game_data.health > game_data.maxhealth:
                    game_data.health = game_data.maxhealth
            if collided_object == "magnet":
                level[player_pos//128][1] = "grass"
                use_magnet = True
                magnet_time += powerups["magnet"][game_data.magnetlevel] * 60
            if collided_object == "doublemoney":
                level[player_pos//128][1] = "grass"
                doublemoney = True
                doublemoney_time += powerups["doublemoney"][game_data.doublemoneylevel] * 60

        # run this if magnet has been equipped
        if use_magnet and magnet_timer < magnet_time:
            for row in range(len(level)):
                if level[row][1] == "tall-grass":
                    level[row][1] = "grass"
                    game_data.money += 1 * game_data.moneymultiplier
            magnet_timer += 1
        else:
            use_magnet = False
            magnet_timer = 0

        # run this if doublemoney has been collected
        if doublemoney and doublemoney_timer < doublemoney_time:
            game_data.moneymultiplier = default_moneymultiplier * 2
            doublemoney_timer += 1
        else:
            game_data.moneymultiplier = default_moneymultiplier
            doublemoney = False
            doublemoney_timer = 0

        # draw
        draw_level(screen, level, displacement)
        draw_ui(screen, game_data, score, speed)
        screen.blit(lawn_mowers[game_data.mower][0], (0, player_pos + 16))

        myClock.tick(60)
        display.flip()

def shop():
    if game_data.music:
        # all bgm music by Arevin on Newgrounds
        mixer.music.load("sounds/other-menu-bgm.mp3")
        mixer.music.play(-1)
        mixer.music.set_volume(game_data.volume)

    for i in lawn_mowers: lawn_mowers[i][3] = True if i in game_data.ownedmowers else False

    dilofont_large = font.Font("fonts/dilofont.ttf", 100)
    dilofont_medium = font.Font("fonts/dilofont.ttf", 50)
    dilofont_small = font.Font("fonts/dilofont.ttf", 25)

    shop_title_text = dilofont_large.render("Shop", True, (255, 255, 255))
    equipped_text = dilofont_small.render("Equipped", True, GREEN)

    selected = game_data.mower

    mower_rect_pos = []

    can_buy = False
    buy_button = Rect(0, 0, 0, 0)
    equip_button = Rect(0, 0, 0, 0)

    buff_texts = []

    for i in lawn_mowers.values():
        buff_texts.append([
            dilofont_small.render(f"{str(int(i[2][0]*100 + 100))}% Money", True, GREEN),
            dilofont_small.render(f"{str(int(i[2][1]*100 + 100))}% Health", True, GREEN)
        ])

    running = True
    while running:
        for evt in event.get():
            if evt.type == QUIT:
                if game_data.music: mixer.music.unload()
                running = False
                main_menu()
            if evt.type == MOUSEBUTTONDOWN:
                for i in mower_rect_pos:
                    if i[0].collidepoint(mx, my):
                        selected = i[1]
                if back_rect.collidepoint(mx, my):
                    time.set_timer(QUIT, 10, 1)
                if buy_button.collidepoint(mx, my) and can_buy:
                    lawn_mowers[selected][3] = True
                    game_data.mower = selected
                    game_data.ownedmowers.append(selected)
                    game_data.money -= lawn_mowers[selected][1]
                if equip_button.collidepoint(mx, my):
                    game_data.mower = selected
                
        mx, my = mouse.get_pos()

        mower_name = dilofont_medium.render(selected, True, (255, 255, 255))
        money_text = dilofont_medium.render("Balance: #"+str(game_data.money), True, (255, 255, 255))
        displacement_factor = 0
        
        screen.fill((0, 100, 100))
        screen.blit(shop_title_text, (15, 10))
        screen.blit(mower_name, (1152/2 - (mower_name.get_width()/2), 500))
        screen.blit(money_text, (30, 630))

        back_rect = draw_button(screen, (950, 30), 120, 64, (0, 155, 0), dilofont_medium.render("Back", True, (255, 255, 255)))

        for k in buff_texts:
            screen.blit(k[0], (270 * displacement_factor + 80, 120))
            screen.blit(k[1], (270 * displacement_factor + 80, 150))
            displacement_factor += 1

        displacement_factor = 0
        for i, j in lawn_mowers.items():
            mower_image = transform.rotate(j[0], 90)
            border_rect = Rect(0, 0, 150, 300)

            border_rect.center = mower_image.get_rect(topleft = (270 * displacement_factor + 100, 200)).center
            mower_rect_pos.append([border_rect, i])

            screen.blit(mower_image, (270 * displacement_factor + 100, 200))
            if j[3] and game_data.mower == i:
                draw.rect(screen, GREEN, border_rect, 10, 10)
                screen.blit(equipped_text, (270 * displacement_factor + 105, 480))
            elif j[3] and selected == i:
                draw.rect(screen, GREEN, border_rect, 10, 10)
                if  game_data.mower != i:
                    equip_button = draw_button(screen, (1152/2 - 80, 560), 160, 64, (0, 110, 0), dilofont_medium.render("Equip", True, (255, 255, 255)))
            elif j[3]:
                draw.rect(screen, GREEN, border_rect, 5, 10)
            elif selected == i:
                draw.rect(screen, RED, border_rect, 10, 10)
                if j[1] > game_data.money:
                    price_text = dilofont_medium.render("#"+str(j[1]), True, RED)
                    can_buy = False
                    buy_button = draw_button(screen, (950, 600), 120, 64, (255, 0, 0), dilofont_medium.render("BUY", True, (255, 255, 255)))
                else:
                    price_text = dilofont_medium.render("#"+str(j[1]), True, GREEN)
                    can_buy = True
                    buy_button = draw_button(screen, (950, 600), 120, 64, (0, 155, 0), dilofont_medium.render("BUY", True, (255, 255, 255)))

                screen.blit(price_text, (1152/2 - (price_text.get_width()/2), 550))
            else:
                draw.rect(screen, RED, border_rect, 5, 10)
            displacement_factor += 1

        display.flip()

def upgrades():
    if game_data.music:
        # all bgm music by Arevin on Newgrounds
        mixer.music.load("sounds/other-menu-bgm.mp3")
        mixer.music.play(-1)
        mixer.music.set_volume(game_data.volume)

    dilofont_large = font.Font("fonts/dilofont.ttf", 100)
    dilofont_medium = font.Font("fonts/dilofont.ttf", 50)
    dilofont_small = font.Font("fonts/dilofont.ttf", 25)

    upgrades_title_text = dilofont_large.render("Upgrades", True, (255, 255, 255))

    wrench_maxlevel = len(powerups["wrench"]) - 1
    magnet_maxlevel = len(powerups["magnet"]) - 1
    doublemoney_maxlevel = len(powerups["doublemoney"]) - 1

    running = True
    while running:
        for evt in event.get():
            if evt.type == QUIT:
                if game_data.music: mixer.music.unload()
                running = False
                main_menu()
            if evt.type == MOUSEBUTTONDOWN:
                if upgrade_wrench_button.collidepoint(mx, my):
                    if game_data.money >= wrench_price and game_data.wrenchlevel < wrench_maxlevel:
                        game_data.wrenchlevel += 1
                        game_data.money -= wrench_price
                if upgrade_magnet_button.collidepoint(mx, my):
                    if game_data.money >= magnet_price and game_data.magnetlevel < magnet_maxlevel:
                        game_data.magnetlevel += 1
                        game_data.money -= magnet_price
                if upgrade_doublemoney_button.collidepoint(mx, my):
                    if game_data.money >= doublemoney_price and game_data.doublemoneylevel < doublemoney_maxlevel:
                        game_data.doublemoneylevel += 1
                        game_data.money -= doublemoney_price
                if upgrade_health_button.collidepoint(mx, my):
                    if game_data.money >= health_price:
                        game_data.maxhealthlevel += 1
                        game_data.maxhealth += game_data.maxhealthlevel * 25
                        game_data.money -= health_price
                
        mx, my = mouse.get_pos()

        wrench_price = game_data.wrenchlevel * (50 + game_data.wrenchlevel*3) + 200
        magnet_price = game_data.magnetlevel * (50 + game_data.magnetlevel*5) + 300
        doublemoney_price = game_data.doublemoneylevel * (50 + game_data.doublemoneylevel*5) + 300
        health_price = game_data.maxhealthlevel * (50 + game_data.maxhealthlevel*3) + 400

        wrench_upgrade_text = dilofont_medium.render("Wrench: {} (#{}) - Restores {}".format(game_data.wrenchlevel, wrench_price, powerups["wrench"][game_data.wrenchlevel]), True, (255, 255, 255))
        magnet_upgrade_text = dilofont_medium.render("Magnet: {} (#{}) (Lasts {}s)".format(game_data.magnetlevel, magnet_price, powerups["magnet"][game_data.magnetlevel]), True, (255, 255, 255))
        doublemoney_upgrade_text = dilofont_medium.render("Double Money: {} (#{}) (Lasts {}s)".format(game_data.doublemoneylevel, doublemoney_price, powerups["doublemoney"][game_data.doublemoneylevel]), True, (255, 255, 255))
        maxhealth_upgrade_text = dilofont_medium.render("Max Health: {} (#{}) - {} Health".format(game_data.maxhealthlevel, health_price, game_data.maxhealth), True, (255, 255, 255))
        

        screen.fill((0, 100, 100))
        screen.blit(upgrades_title_text, (15, 10))

        screen.blit(wrench_upgrade_text, (15, 150))
        screen.blit(magnet_upgrade_text, (15, 225))
        screen.blit(doublemoney_upgrade_text, (15, 300))
        screen.blit(maxhealth_upgrade_text, (15, 375))

        wrench_button_col = GREEN if game_data.money >= wrench_price and game_data.wrenchlevel < wrench_maxlevel else RED
        magnet_button_col = GREEN if game_data.money >= magnet_price and game_data.magnetlevel < magnet_maxlevel else RED
        doublemoney_button_col = GREEN if game_data.money >= doublemoney_price and game_data.doublemoneylevel < doublemoney_maxlevel else RED
        health_button_col = GREEN if game_data.money >= health_price else RED

        upgrade_wrench_button = draw_button(screen, (1000, 150), 100, 50, wrench_button_col, dilofont_small.render("UPGRADE" if game_data.wrenchlevel < wrench_maxlevel else "MAX LEVEL", True, (255, 255, 255)))
        upgrade_magnet_button = draw_button(screen, (1000, 225), 100, 50, magnet_button_col, dilofont_small.render("UPGRADE" if game_data.magnetlevel < magnet_maxlevel else "MAX LEVEL", True, (255, 255, 255)))
        upgrade_doublemoney_button = draw_button(screen, (1000, 300), 100, 50, doublemoney_button_col, dilofont_small.render("UPGRADE"  if game_data.doublemoneylevel < doublemoney_maxlevel else "MAX LEVEL", True, (255, 255, 255)))
        upgrade_health_button = draw_button(screen, (1000, 375), 100, 50, health_button_col, dilofont_small.render("UPGRADE", True, (255, 255, 255)))

        display.flip()


def settings():
    global game_data
    if game_data.music:
        # all bgm music by Arevin on Newgrounds
        mixer.music.load("sounds/other-menu-bgm.mp3")
        mixer.music.play(-1)
        mixer.music.set_volume(game_data.volume)

    empty_box = transform.scale(image.load("images/empty-box.png"), (64, 48))
    filled_box = transform.scale(image.load("images/filled-box.png"), (64, 48))

    checkbox = transform.scale(image.load("images/checkbox.png"), (64, 48))
    uncheckedbox = transform.scale(image.load("images/uncheckbox.png"), (64, 48))

    plus = transform.scale(image.load("images/plus.png"), (64, 64))
    minus = transform.scale(image.load("images/minus.png"), (64, 64))

    dilofont_large = font.Font("fonts/dilofont.ttf", 100)
    dilofont_medium = font.Font("fonts/dilofont.ttf", 50)
    settings_title_text = dilofont_large.render("Settings", True, (255, 255, 255))

     
    running = True
    while running:
        for evt in event.get():
            if evt.type == QUIT:
                if game_data.music: mixer.music.unload()
                running = False
                main_menu()
            if evt.type == MOUSEBUTTONDOWN:
                if minus.get_rect(topleft=(965,240)).collidepoint(mx, my):
                    if game_data.volume > 0:
                        game_data.volume = round((game_data.volume * 10 - 1) / 10, 1)
                elif plus.get_rect(topleft=(965+64,240)).collidepoint(mx, my):
                    if game_data.volume < 1:
                        game_data.volume = round((game_data.volume * 10 + 1) / 10, 1)
                        
                if filled_box.get_rect(topleft=(225,150)).collidepoint(mx, my):
                    game_data.music = not game_data.music

                if reset_rect.collidepoint(mx, my):
                    game_data = reset_data()
                if back_rect.collidepoint(mx, my):
                    time.set_timer(QUIT, 10, 1)
                
        mx, my = mouse.get_pos()

        screen.fill((0, 100, 100))
        screen.blit(settings_title_text, (15, 10))

        screen.blit(dilofont_medium.render("Volume:", True, (255, 255, 255)), (20, 250))
        for j in range(10):
            if j < game_data.volume * 10:
                screen.blit(filled_box, (j * (filled_box.get_width() + 10) + 225, 250))
            else:
                screen.blit(empty_box, (j * (empty_box.get_width() + 10) + 225, 250))
        screen.blit(minus, (10 * (empty_box.get_width() + 10) + 225, 240))
        screen.blit(plus, ((10 + 1) * (empty_box.get_width() + 10) + 225, 240))

        screen.blit(dilofont_medium.render("Music:", True, (255, 255, 255)), (20, 150))
        if game_data.music:
            screen.blit(checkbox, (225, 150))
        else:
            screen.blit(uncheckedbox, (225, 150))

        reset_rect = draw_button(screen, (420, 500), 320, 64, (255, 0, 0), dilofont_medium.render("reset all data", True, (255, 255, 255)))
        back_rect = draw_button(screen, (520, 600), 120, 64, (0, 155, 0), dilofont_medium.render("Back", True, (255, 255, 255)))

        display.flip()


if __name__ == "__main__":
    main_menu()