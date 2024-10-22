import pygame
import sys
import random
import os
from datetime import datetime, timedelta

# Inicializar pygame
pygame.init()

# Dimensiones de la pantalla
size = width, height = 800, 900
cell_size = 80

# Colores
black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)

# Crear la pantalla
screen = pygame.display.set_mode(size)
# Ruta de la carpeta de frames
frames_path = 'frames'

# Cargar los fotogramas de la animación desde la carpeta "frames"
frames_tierra = [pygame.image.load(os.path.join(frames_path, f'tierra_frame_{i}.png')) for i in range(1, 6)]
frames_agua = [pygame.image.load(os.path.join(frames_path, f'agua_frame_{i}.png')) for i in range(1, 6)]
frames_casa = [pygame.image.load(os.path.join(frames_path, f'casa_frame_{i}.png')) for i in range(1, 6)]
frames_calle = [pygame.image.load(os.path.join(frames_path, f'calle_frame_{i}.png')) for i in range(1, 6)]
frames_obra = [pygame.image.load(os.path.join(frames_path, f'obra_frame_{i}.png')) for i in range(1, 11)]

# Redimensionar las imágenes
frames_tierra = [pygame.transform.scale(img, (cell_size, cell_size)) for img in frames_tierra]
frames_agua = [pygame.transform.scale(img, (cell_size, cell_size)) for img in frames_agua]
frames_casa = [pygame.transform.scale(img, (cell_size, cell_size)) for img in frames_casa]
frames_calle = [pygame.transform.scale(img, (cell_size, cell_size)) for img in frames_calle]
frames_obra = [pygame.transform.scale(img, (cell_size, cell_size)) for img in frames_obra]

# Generar la grilla con menos bloques de agua
def generar_grilla():
    grilla = []
    for _ in range(10):
        fila = []
        for _ in range(10):
            letra = 'T' if random.random() < 0.8 else 'A'
            fila.append(letra)
        grilla.append(fila)
    return grilla

grilla = generar_grilla()
dinero = 1000
modo = 'casa'
fecha = datetime(1993, 1, 1, 0, 0)

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
    
    if tiempo_actual - ultimo_cambio_frame_general > 1000:  # Cambiar el frame cada 1 segundo
        frame_index_general = (frame_index_general + 1) % len(frames_tierra)
        ultimo_cambio_frame_general = tiempo_actual
    
    for i, fila in enumerate(grilla):
        for j, letra in enumerate(fila):
            rect = pygame.Rect(j * cell_size, i * cell_size, cell_size, cell_size)
            if letra == 'A':
                screen.blit(frames_agua[frame_index_general], rect.topleft)
            elif letra == 'T':
                screen.blit(frames_tierra[frame_index_general], rect.topleft)
            elif letra == 'C':
                screen.blit(frames_casa[frame_index_general], rect.topleft)
            elif letra == 'S':
                screen.blit(frames_calle[frame_index_general], rect.topleft)
            elif letra == 'O':
                inicio = obras.get((i, j), tiempo_actual)
                frame_index_obra = ((tiempo_actual - inicio) // 1000) % len(frames_obra)
                screen.blit(frames_obra[frame_index_obra], rect.topleft)
            pygame.draw.rect(screen, black, rect, 1)
    
    font = pygame.font.Font(None, 36)
    dinero_text = font.render(f"Dinero: ${dinero}", True, white)
    screen.blit(dinero_text, (10, height - 100))
    
    if mensaje and tiempo_actual <= mensaje_mostrar_hasta:
        alpha = int(255 * (mensaje_mostrar_hasta - tiempo_actual) / 5000)
        mensaje_text = font.render(mensaje, True, (red[0], red[1], red[2], alpha))
        screen.blit(mensaje_text, (10, height - 130))

    controles_text = font.render("Controles: 1 - Construir Casa ($50), 2 - Construir Calle ($30)", True, white)
    screen.blit(controles_text, (10, height - 70))

    fecha_text = font.render(fecha.strftime("Fecha: %d/%m/%Y Hora: %H:%M"), True, white)
    screen.blit(fecha_text, (10, height - 40))

def hay_calle_adyacente(grilla, row, col):
    direcciones = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    for dr, dc in direcciones:
        nr, nc = row + dr, col + dc
        if 0 <= nr < len(grilla) and 0 <= nc < len(grilla[0]):
            if grilla[nr][nc] == 'S':
                return True
    return False

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
            if modo == 'casa':
                if grilla[row][col] == 'T' and hay_calle_adyacente(grilla, row, col):
                    grilla[row][col] = 'O'
                    obras[(row, col)] = pygame.time.get_ticks()
                    dinero -= 50
                    mensaje = ""
                else:
                    mensaje = "¡Debe haber una calle adyacente para construir una casa!"
            elif modo == 'calle' and grilla[row][col] == 'T':
                grilla[row][col] = 'S'
                dinero -= 30
                mensaje = ""
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                modo = 'casa'
            elif event.key == pygame.K_2:
                modo = 'calle'

    tiempo_actual = pygame.time.get_ticks()
    for (row, col), inicio in list(obras.items()):
        if tiempo_actual - inicio > 10000:
            grilla[row][col] = 'C'
            del obras[(row, col)]

    if tiempo_actual - ultimo_ingreso > 5000:
        for fila in grilla:
            dinero += fila.count('C') * 10
        ultimo_ingreso = tiempo_actual

    if tiempo_actual - ultimo_tornado > 30000:
        for i in range(random.randint(1, 10)):
            casas = [(r, c) for r, fila in enumerate(grilla) for c, letra in enumerate(fila) if letra == 'C']
            if casas:
                row, col = random.choice(casas)
                grilla[row][col] = 'O'
                obras[(row, col)] = pygame.time.get_ticks()
                dinero -= 20
        mensaje = "¡Un tornado ha pasado y algunas casas han vuelto a ser obras!"
        mensaje_mostrar_hasta = tiempo_actual + 5000
        ultimo_tornado = tiempo_actual

    fecha += timedelta(minutes=1)
    
    screen.fill(black)
    dibujar_grilla(screen, grilla, dinero, mensaje, fecha, tiempo_actual)
    pygame.display.flip()
    
    reloj.tick(60)

    if dinero <= 0:
        screen.fill(red)
        font = pygame.font.Font(None, 74)
        game_over_text = font.render("¡Juego Terminado!", True, white)
        screen.blit(game_over_text, (width//4, height//2 - 40))
        pygame.display.flip()
        pygame.time.wait(3000)
        pygame.quit()
        sys.exit()
