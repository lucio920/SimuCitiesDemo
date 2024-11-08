from enum import Enum

import pygame
import sys
from datetime import timedelta
import pygame.mixer

from game.cell import Water, Construction, Road, Land, House
from game.game import Game

############################################################
#                       UI setup                           #
############################################################
pygame.init()
pygame.display.set_caption('SimuCities 2000')

# Audio
pygame.mixer.init()

# Window and cell size
window_size = width, height = 800, 900
cell_size = 80

# Colores
black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
blue = (0, 0, 255)
green = (0, 255,0)
light_blue = (2, 147, 250)
grey = (43, 56, 77)

# Screen
screen = pygame.display.set_mode(window_size)
screen.fill(white)
font = pygame.font.Font(None, 74)
font2 = pygame.font.Font(None, 30)
title = font.render("SimuCities 2000", True, black)
subtitle = font2.render("Presiona cualquier tecla para comenzar", True, black)
screen.blit(title, (width//4.5, height//2 - 40))
screen.blit(subtitle, (width//4.4, height//1.9))
pygame.display.flip()

# Frames load
frames_land = [pygame.image.load(f'frames/tierra_frame_{i}.png') for i in range(1, 6)]
frames_water = [pygame.image.load(f'frames/agua_frame_{i}.png') for i in range(1, 6)]
frames_house = [pygame.image.load(f'frames/casa_frame_{i}.png') for i in range(1, 6)]
frames_road = [pygame.image.load(f'frames/calle_frame_{i}.png') for i in range(1, 6)]
frames_construction = [pygame.image.load(f'frames/obra_frame_{i}.png') for i in range(1, 11)]

# Sound effects load
sound_house = pygame.mixer.Sound('sounds/construir_casa.wav')
sound_road = pygame.mixer.Sound('sounds/construir_calle.wav')
sound_tornado = pygame.mixer.Sound('sounds/tornado.wav')
sound_game_over = pygame.mixer.Sound('sounds/game_over.wav')
sound_earthquake = pygame.mixer.Sound('sounds/terremoto.wav')
sound_win = pygame.mixer.Sound('sounds/win.wav')

# Music load
pygame.mixer.music.load('sounds/theme.mp3')
pygame.mixer.music.set_volume(0.2)
pygame.mixer.music.play(-1)

# Frames resize
frames_land = [pygame.transform.scale(img, (cell_size, cell_size)) for img in frames_land]
frames_water = [pygame.transform.scale(img, (cell_size, cell_size)) for img in frames_water]
frames_house = [pygame.transform.scale(img, (cell_size, cell_size)) for img in frames_house]
frames_road = [pygame.transform.scale(img, (cell_size, cell_size)) for img in frames_road]
frames_construction = [pygame.transform.scale(img, (cell_size, cell_size)) for img in frames_construction]

# Game window drawing function
def draw_game(screen, grid, money, date, current_time, constructions, message):
    global general_frame_index, last_general_frame_change

    if current_time - last_general_frame_change > 1000:
        general_frame_index = (general_frame_index + 1) % len(frames_land)
        last_general_frame_change = current_time

    for i, fila in enumerate(grid):
        for j, celda in enumerate(fila):
            rect = pygame.Rect(j * cell_size, i * cell_size, cell_size, cell_size)
            if isinstance(celda, Water):
                screen.blit(frames_water[general_frame_index], rect.topleft)
            elif isinstance(celda, Land):
                screen.blit(frames_land[general_frame_index], rect.topleft)
            elif isinstance(celda, House):
                screen.blit(frames_house[general_frame_index], rect.topleft)
            elif isinstance(celda, Road):
                screen.blit(frames_road[general_frame_index], rect.topleft)
            elif isinstance(celda, Construction):
                start_date = constructions.get((i, j), date)
                frame_index_obra = min(int((date - start_date).total_seconds()/3600), len(frames_construction) - 1)
                screen.blit(frames_construction[frame_index_obra], rect.topleft)
            pygame.draw.rect(screen, black, rect, 1)

    font = pygame.font.Font(None, 36)
    dinero_text = font.render(f"Dinero: ${money}", True, green)
    screen.blit(dinero_text, (10, height - 100))


    if message and current_time <= show_message_until:
        alpha = int(255 * (show_message_until - current_time) / 5000)
        message_text = font.render(message, True, (light_blue[0], light_blue[1], light_blue[2], alpha),grey)
        screen.blit(message_text, (10, height - 130))

    controles_text = font.render("[1]-Casa($50)     [2]-Calle($30)      [3]-Demoler($100)   [R]-Reiniciar", True, white)
    screen.blit(controles_text, (10, height - 70))

    fecha_text = font.render(date.strftime("OBJETIVO: $2000    Fecha: %d/%m/%Y Hora: %H:%M"), True, white)
    screen.blit(fecha_text, (10, height - 40))

# End game window function
def game_end(color, hang_time, message):
    screen.fill(color)
    font = pygame.font.Font(None, 74)

    pygame.mixer.music.stop()
    sound_house.stop()
    
    
    if color == red: #GAME OVER
        sound_game_over.play()
    else: #WIN
        sound_win.play()
        sound_tornado.stop()
        sound_earthquake.stop()

    game_over_text = font.render(message, True, white)
    screen.blit(game_over_text, (width // 4, height // 2 - 40))
    pygame.display.flip()
    pygame.time.wait(hang_time)
    pygame.quit()
    sys.exit()

############################################################
#                       Game setup                         #
############################################################
game = Game()

# Build modes
BuildMode = Enum('BuildMode', ['HOUSE', 'ROAD', 'DEMOLISH'])
build_mode = BuildMode.HOUSE # Default mode

# UI Message and frame change helper variables
message = ''
show_message_until = 0
general_frame_index = 0
last_general_frame_change = pygame.time.get_ticks()


############################################################
#                    Main game loop                        #
############################################################
clk = pygame.time.Clock()
while True:
    ################# UPDATES GAME DATE #####################
    # The loop ticks at about 60 times per second. So it's 1 hour in game time per second in real time.
    game.updateGameState(timedelta(minutes=1))

    current_time = pygame.time.get_ticks()

    ################### NATURAL DISASTERS CHECK ##############################
    if game.hasTornadoPassed():
        sound_tornado.play()
        message = "¡Un tornado ha pasado y algunas casas han vuelto a ser obras!"
        show_message_until = current_time + 5000

    if game.hasEarthquakePassed():
        sound_earthquake.play()
        message = "¡Terremoto! ¡Las casas vuelven a ser tierra!"
        show_message_until = current_time + 5000

    ##################  UPDATES SCREEEEN ##########################
    screen.fill(grey)
    (grid, money, date, constructions) = game.getGameData()
    draw_game(screen, grid, money, date, current_time, constructions, message)
    pygame.display.flip()

    ######################## GAME FINISH CHECKS ############################
    if game.isGameOver():
        game_end(red, 3000, "  GAME OVER")

    if game.isGameWin():
        game_end(blue, 5000, "    ¡GANASTE!")

    for event in pygame.event.get():
        #################  CLOSE WINDOW WITH X BUTTON #####################
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        ########################   CHANGE BUILD MODES   ##################################
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                build_mode = BuildMode.HOUSE
                message = "CASA"
                show_message_until = current_time + 1000
            elif event.key == pygame.K_2:
                build_mode = BuildMode.ROAD
                message = "CALLE"
                show_message_until = current_time + 1000
            elif event.key == pygame.K_3:
                build_mode = BuildMode.DEMOLISH
                message = "DEMOLER"
                show_message_until = current_time + 1000
            elif event.key == pygame.K_r:  # Reset game with "R" key.
                game = Game()
                show_message_until = 0
                general_frame_index = 0
                last_general_frame_change = pygame.time.get_ticks()
                pygame.mixer.music.play(-1)

        ########################   CHANGE BUILD MODES   ##################################
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            row = y // cell_size
            col = x // cell_size
            """
            if col >= 10 or row >= 10:
                continue
            """



            if build_mode == BuildMode.HOUSE:
                if game.buildHouse(row, col):
                    sound_house.stop()
                    sound_house.play()
                else:
                    message = "¡Debe haber una calle adyacente para construir una casa!"
                    show_message_until = current_time + 3000

            elif build_mode == BuildMode.ROAD:
                if game.buildRoad(row, col):
                    sound_road.stop()
                    sound_road.play()
                else:
                    message = "¡La calle debe construirse sobre tierra!"
                    show_message_until = current_time + 3000

            elif build_mode == BuildMode.DEMOLISH:
                if game.demolish(row, col):
                    sound_road.stop()
                    sound_road.play()
                else:
                    message = "¡Solo se puede demoler casas terminadas!"
                    show_message_until = current_time + 3000

    ####################### ADDS TICKS TO GAME CLOCK ############################
    clk.tick(60) # VER QUE SI
