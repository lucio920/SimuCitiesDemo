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
cell_size = 80 # TODO: ajustar cell_size para redimensionar ventana.

# TODO: pasar a constantes
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

## TODO MEJORAR
# Game window drawing function
def draw_game(screen, grid, money, date, current_time, constructions, message):
    global frame_index_general, ultimo_cambio_frame_general

    if current_time - ultimo_cambio_frame_general > 1000:
        frame_index_general = (frame_index_general + 1) % len(frames_land)
        ultimo_cambio_frame_general = current_time

    for i, fila in enumerate(grid):
        for j, celda in enumerate(fila):
            rect = pygame.Rect(j * cell_size, i * cell_size, cell_size, cell_size)
            if isinstance(celda, Water):
                screen.blit(frames_water[frame_index_general], rect.topleft)
            elif isinstance(celda, Land):
                screen.blit(frames_land[frame_index_general], rect.topleft)
            elif isinstance(celda, House):
                screen.blit(frames_house[frame_index_general], rect.topleft)
            elif isinstance(celda, Road):
                screen.blit(frames_road[frame_index_general], rect.topleft)
            elif isinstance(celda, Construction):
                # TODO: fix the bug, only 8 frames are showed.
                # This func gets executed 60 times per second. Each second in real life is 1 hour in game time.
                # This means that each time this function gets called, one minute has passed
                # There are 10 frames for a construction site. For simplicity, the sites turn into houses in 10 hours.
                start_date = constructions.get((i, j), date)
                frame_index_obra = min(int((date - start_date).total_seconds()/3600), len(frames_construction) - 1)
                print(frame_index_obra)
                screen.blit(frames_construction[frame_index_obra], rect.topleft)
            pygame.draw.rect(screen, black, rect, 1)

    font = pygame.font.Font(None, 36)
    dinero_text = font.render(f"Dinero: ${money}", True, green)
    screen.blit(dinero_text, (10, height - 100))


    if mensaje and current_time <= mensaje_mostrar_hasta:
        alpha = int(255 * (mensaje_mostrar_hasta - current_time) / 5000)
        mensaje_text = font.render(mensaje, True, (light_blue[0], light_blue[1], light_blue[2], alpha),grey)
        screen.blit(mensaje_text, (10, height - 130))

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
    sound_tornado.stop()
    sound_earthquake.stop()
    sound_game_over.play()

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

# Mantener un registro del tiempo de construcción y ganancias
ultimo_tornado = pygame.time.get_ticks()
mensaje_mostrar_hasta = 0
frame_index_general = 0
mensaje = ''
ultimo_cambio_frame_general = pygame.time.get_ticks()


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
        mensaje = "¡Un tornado ha pasado y algunas casas han vuelto a ser obras!"
        mensaje_mostrar_hasta = current_time + 5000

    if game.hasEarthquakePassed():
        sound_earthquake.play()
        mensaje = "¡Terremoto! ¡Las casas vuelven a ser tierra!"
        mensaje_mostrar_hasta = current_time + 5000

    ##################  UPDATES SCREEEEN ##########################
    screen.fill(grey)
    (grid, money, date, constructions) = game.getGameData()
    draw_game(screen, grid, money, date, current_time, constructions, mensaje)
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
                mensaje = "CASA"
                mensaje_mostrar_hasta = current_time + 1000
            elif event.key == pygame.K_2:
                build_mode = BuildMode.ROAD
                mensaje = "CALLE"
                mensaje_mostrar_hasta = current_time + 1000
            elif event.key == pygame.K_3:
                build_mode = BuildMode.DEMOLISH
                mensaje = "DEMOLER"
                mensaje_mostrar_hasta = current_time + 1000
            elif event.key == pygame.K_r:  # Reset game with "R" key.
                game = Game()
                mensaje_mostrar_hasta = 0
                frame_index_general = 0
                ultimo_cambio_frame_general = pygame.time.get_ticks()
                pygame.mixer.music.play(-1)

        ########################   CHANGE BUILD MODES   ##################################
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            row = y // cell_size
            col = x // cell_size
            # TODO: FIX BUG OF CLICKING OUTSIDE GRID

            if build_mode == BuildMode.HOUSE:
                if game.buildHouse(row, col):
                    sound_house.stop()
                    sound_house.play()
                else:
                    mensaje = "¡Debe haber una calle adyacente para construir una casa!"
                    mensaje_mostrar_hasta = current_time + 3000

            elif build_mode == BuildMode.ROAD:
                if game.buildRoad(row, col):
                    sound_road.stop()
                    sound_road.play()

            elif build_mode == BuildMode.DEMOLISH:
                if game.demolish(row, col):
                    sound_road.stop()
                    sound_road.play()

    ####################### ADDS TICKS TO GAME CLOCK ############################
    clk.tick(60) # VER QUE SI
