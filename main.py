import pygame
import sys
import random
from datetime import datetime, timedelta
import pygame.mixer

from juego.juego import Juego

# Inicializar pygame
pygame.init()
pygame.display.set_caption('SimuCities 2000')

#icono = pygame.image.load('ruta/al/icono.ico')
#pygame.display.set_icon(icono)

# Inicializar el mezclador de sonido
pygame.mixer.init()


# Dimensiones de la pantalla
size = width, height = 800, 900
cell_size = 80

# Colores
black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
blue = (0, 0, 255)
green = (0, 255,0)
bluer = (2, 147, 250)
grey = (43, 56, 77)

# Crear la pantalla
screen = pygame.display.set_mode(size)
screen.fill(white)
font = pygame.font.Font(None, 74)
font2 = pygame.font.Font(None, 30)
title = font.render("SimuCities 2000", True, black)
subtitle = font2.render("Presiona cualquier tecla para comenzar", True, black)
screen.blit(title, (width//4.5, height//2 - 40))
screen.blit(subtitle, (width//4.4, height//1.9))
pygame.display.flip()


# Cargar los fotogramas de la animación desde la carpeta 'frames'
frames_tierra = [pygame.image.load(f'frames/tierra_frame_{i}.png') for i in range(1, 6)]
frames_agua = [pygame.image.load(f'frames/agua_frame_{i}.png') for i in range(1, 6)]
frames_casa = [pygame.image.load(f'frames/casa_frame_{i}.png') for i in range(1, 6)]
frames_calle = [pygame.image.load(f'frames/calle_frame_{i}.png') for i in range(1, 6)]
frames_obra = [pygame.image.load(f'frames/obra_frame_{i}.png') for i in range(1, 11)]  # 10 fotogramas

# Redimensionar las imágenes
frames_tierra = [pygame.transform.scale(img, (cell_size, cell_size)) for img in frames_tierra]
frames_agua = [pygame.transform.scale(img, (cell_size, cell_size)) for img in frames_agua]
frames_casa = [pygame.transform.scale(img, (cell_size, cell_size)) for img in frames_casa]
frames_calle = [pygame.transform.scale(img, (cell_size, cell_size)) for img in frames_calle]
frames_obra = [pygame.transform.scale(img, (cell_size, cell_size)) for img in frames_obra]

# Cargar los efectos de sonido
sonido_casa = pygame.mixer.Sound('sounds/construir_casa.wav')
sonido_calle = pygame.mixer.Sound('sounds/construir_calle.wav')
sonido_tornado = pygame.mixer.Sound('sounds/tornado.wav')
sonido_perder = pygame.mixer.Sound('sounds/game_over.wav')
sonido_terremoto = pygame.mixer.Sound('sounds/terremoto.wav')
sonido_ganar = pygame.mixer.Sound('sounds/win.wav')

# Cargar la música de fondo
pygame.mixer.music.load('sounds/theme.mp3')
pygame.mixer.music.set_volume(0.2)  # Ajustar el volumen de la música
pygame.mixer.music.play(-1)  # Reproducir la música en bucle (-1 para bucle infinito)

## JUEGO
juego = Juego(1000, 'casa', datetime(1993, 1, 1, 0, 0))

# Mantener un registro del tiempo de construcción y ganancias
obras = {}
ultimo_ingreso = pygame.time.get_ticks()
ultimo_tornado = pygame.time.get_ticks()
mensaje_mostrar_hasta = 0
frame_index_general = 0
ultimo_cambio_frame_general = pygame.time.get_ticks()


# Función para dibujar la grilla
def dibujar_grilla(screen, grilla, dinero, mensaje, fecha, tiempo_actual):
    global frame_index_general, ultimo_cambio_frame_general

    if tiempo_actual - ultimo_cambio_frame_general > 1000:
        frame_index_general = (frame_index_general + 1) % len(frames_tierra)
        ultimo_cambio_frame_general = tiempo_actual

    for i, fila in enumerate(grilla):
        for j, celda in enumerate(fila):
            rect = pygame.Rect(j * cell_size, i * cell_size, cell_size, cell_size)
            if celda.tipo == 'A':
                screen.blit(frames_agua[frame_index_general], rect.topleft)
            elif celda.tipo == 'T':
                screen.blit(frames_tierra[frame_index_general], rect.topleft)
            elif celda.tipo == 'C':
                screen.blit(frames_casa[frame_index_general], rect.topleft)
            elif celda.tipo == 'S':
                screen.blit(frames_calle[frame_index_general], rect.topleft)
            elif celda.tipo == 'O':
                inicio = obras.get((i, j), tiempo_actual)
                frame_index_obra = ((tiempo_actual - inicio) // 1000) % len(frames_obra)
                screen.blit(frames_obra[frame_index_obra], rect.topleft)
            pygame.draw.rect(screen, black, rect, 1)

    font = pygame.font.Font(None, 36)
    dinero_text = font.render(f"Dinero: ${dinero}", True, green)
    screen.blit(dinero_text, (10, height - 100))


    if mensaje and tiempo_actual <= mensaje_mostrar_hasta:
        alpha = int(255 * (mensaje_mostrar_hasta - tiempo_actual) / 5000)
        mensaje_text = font.render(mensaje, True, (bluer[0], bluer[1], bluer[2], alpha),grey)
        screen.blit(mensaje_text, (10, height - 130))

    controles_text = font.render("[1]-Casa($50)     [2]-Calle($30)      [3]-Demoler($100)   [R]-Reiniciar", True, white)
    screen.blit(controles_text, (10, height - 70))

    fecha_text = font.render(fecha.strftime("OBJETIVO: $2000    Fecha: %d/%m/%Y Hora: %H:%M"), True, white)
    screen.blit(fecha_text, (10, height - 40))

def hay_calle_adyacente(grilla, row, col):
    direcciones = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    for dr, dc in direcciones:
        nr, nc = row + dr, col + dc
        if 0 <= nr < len(grilla) and 0 <= nc < len(grilla[0]):
            if grilla[nr][nc].tipo == 'S':
                return True
    return False

def evento_terremoto():
    global grilla, dinero, mensaje, mensaje_mostrar_hasta
    num_casas_terremoto = random.randint(1, 15)  # Número aleatorio de casas afectadas por el terremoto
    casas = [(r, c) for r, fila in enumerate(grilla) for c, letra in enumerate(fila) if letra == 'C']
    for _ in range(num_casas_terremoto):
        if casas:
            row, col = random.choice(casas)
            juego.grilla[row][col].tipo = 'T'
            casas.remove((row, col))
    dinero -= num_casas_terremoto * 10 #costo de perder una casa
    sonido_terremoto.play()

mensaje = ""
reloj = pygame.time.Clock()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            row = y // cell_size
            col = x // cell_size

            #MODOS DE JUGADOR

            if juego.modo == 'casa':
                # if juego.cambiar_estado(row, col, 'C', -50):
                #    sonido_casa.stop()
                #    sonido_casa.play()
                if juego.grilla[row][col].tipo == 'T' and hay_calle_adyacente(juego.grilla, row, col):
                    juego.grilla[row][col].tipo = 'O'
                    obras[(row, col)] = pygame.time.get_ticks()
                    juego.dinero -= 50
                    sonido_casa.stop()
                    sonido_casa.play()

                else:
                    mensaje = "¡Debe haber una calle adyacente para construir una casa!"
                    mensaje_mostrar_hasta = juego.tiempo_actual + 3000
            elif juego.modo == 'calle' and juego.grilla[row][col].tipo == 'T':
                juego.grilla[row][col].tipo = 'S'
                sonido_calle.stop()
                sonido_calle.play()
                juego.dinero -= 30
                mensaje = ""
            elif juego.modo == 'demoler' and juego.grilla[row][col].tipo == 'C':
                juego.grilla[row][col].tipo = 'T'
                sonido_calle.stop()
                sonido_calle.play()
                juego.dinero -= 100
                mensaje = ""

        #TECLAS DE LOS MODOS

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                juego.modo = 'casa'
                mensaje = "CASA"
                mensaje_mostrar_hasta = juego.tiempo_actual + 1000
            elif event.key == pygame.K_2:
                juego.modo = 'calle'
                mensaje = "CALLE"
                mensaje_mostrar_hasta = juego.tiempo_actual + 1000
            elif event.key == pygame.K_3:
                juego.modo = 'demoler'
                mensaje = "DEMOLER"
                mensaje_mostrar_hasta = juego.tiempo_actual + 1000
            elif event.key == pygame.K_r:  # Reiniciar el juego con la tecla "R"
                juego = Juego(1000, 'casa', datetime(1993, 1, 1, 0, 0))
                obras = {}
                ultimo_ingreso = pygame.time.get_ticks()
                ultimo_tornado = pygame.time.get_ticks()
                mensaje_mostrar_hasta = 0
                frame_index_general = 0
                ultimo_cambio_frame_general = pygame.time.get_ticks()
                pygame.mixer.music.play(-1)

    juego.actualizar_tiempo(pygame.time.get_ticks())
    for (row, col), inicio in list(obras.items()):
        if juego.tiempo_actual - inicio > 10000:
            juego.grilla[row][col].tipo = 'C'
            del obras[(row, col)]

    if juego.tiempo_actual - ultimo_ingreso > 5000:
        for fila in juego.grilla:
            juego.dinero += sum(celda.tipo == 'C' for celda in fila) * 10
        ultimo_ingreso = juego.tiempo_actual


    if juego.tiempo_actual - ultimo_tornado > 30000:
        sonido_tornado.play()
        for i in range(random.randint(1, 10)):
            casas = [
                (r, c)
                for r, fila in enumerate(juego.grilla)
                for c, celda in enumerate(fila) if celda.tipo == 'C'
            ]
            if casas:
                row, col = random.choice(casas)
                juego.grilla[row][col].tipo = 'O'
                obras[(row, col)] = pygame.time.get_ticks()
                juego.dinero -= 20
        mensaje = "¡Un tornado ha pasado y algunas casas han vuelto a ser obras!"
        mensaje_mostrar_hasta = juego.tiempo_actual + 5000
        ultimo_tornado = juego.tiempo_actual


    if random.randint(0, 1500) == 1 and juego.tiempo_actual >= 60000: #probabilidad de terremoto
        evento_terremoto()
        mensaje = "¡Terremoto! ¡Las casas vuelven a ser tierra!"
        mensaje_mostrar_hasta = juego.tiempo_actual + 5000

    juego.actualizar_fecha(timedelta(minutes=1))

    screen.fill(grey)
    dibujar_grilla(screen, juego.grilla, juego.dinero, mensaje, juego.fecha, juego.tiempo_actual)
    pygame.display.flip()

    reloj.tick(60)

    if juego.dinero <= 0:
        screen.fill(red)
        font = pygame.font.Font(None, 74)

        pygame.mixer.music.stop()
        sonido_casa.stop()
        #sonido_tornado.stop()
        #sonido_terremoto.stop()
        sonido_perder.play()

        game_over_text = font.render("  GAME OVER", True, white)
        screen.blit(game_over_text, (width//4, height//2 - 40))
        pygame.display.flip()
        pygame.time.wait(3000)
        pygame.quit()
        sys.exit()

    if juego.dinero >= 2000:
        screen.fill(blue)
        font = pygame.font.Font(None, 74)

        pygame.mixer.music.stop()
        sonido_casa.stop()
        sonido_tornado.stop()
        sonido_terremoto.stop()
        sonido_ganar.play()

        win_text = font.render("    ¡GANASTE!", True, white)
        screen.blit(win_text, (width//4, height//2 - 40))
        pygame.display.flip()
        pygame.time.wait(5000)
        pygame.quit()
        sys.exit()

