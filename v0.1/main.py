import pygame
import sys
import random
from datetime import datetime, timedelta

# Inicializar pygame
pygame.init()

# Dimensiones de la pantalla
size = width, height = 800, 900  # Aumenté la altura para tener espacio para el texto
cell_size = 80

# Colores
black = (0, 0, 0)
white = (255, 255, 255)
blue = (0, 0, 255)
brown = (139, 69, 19)
yellow = (255, 255, 0)
grey = (128, 128, 128)
red = (255, 0, 0)

# Crear la pantalla
screen = pygame.display.set_mode(size)

# Generar la grilla con menos bloques de agua
def generar_grilla():
    grilla = []
    for _ in range(10):
        fila = []
        for _ in range(10):
            letra = 't' if random.random() < 0.8 else 'a'  # 80% tierra, 20% agua
            fila.append(letra)
        grilla.append(fila)
    return grilla

grilla = generar_grilla()
dinero = 1000
modo = 'casa'  # Por defecto, construye casa
fecha = datetime(1993, 1, 1, 0, 0)  # Fecha inicial

# Función para dibujar la grilla
def dibujar_grilla(screen, grilla, dinero, mensaje, fecha):
    for i, fila in enumerate(grilla):
        for j, letra in enumerate(fila):
            rect = pygame.Rect(j * cell_size, i * cell_size, cell_size, cell_size)
            if letra == 'a':
                color_fondo = blue
            elif letra == 't':
                color_fondo = brown
            elif letra == 'c':
                color_fondo = yellow
            elif letra == 's':
                color_fondo = grey
            else:
                color_fondo = black
            pygame.draw.rect(screen, color_fondo, rect)
            pygame.draw.rect(screen, black, rect, 1)
            font = pygame.font.Font(None, 74)
            text = font.render(letra, True, white)
            screen.blit(text, rect.topleft)
    
    # Mostrar el dinero restante y el mensaje
    font = pygame.font.Font(None, 36)
    dinero_text = font.render(f"Dinero: ${dinero}", True, white)
    screen.blit(dinero_text, (10, height - 100))
    
    if mensaje:
        mensaje_text = font.render(mensaje, True, red)
        screen.blit(mensaje_text, (10, height - 130))

    # Mostrar los controles del juego
    controles_text = font.render("Controles: 1 - Construir Casa ($50), 2 - Construir Calle ($30)", True, white)
    screen.blit(controles_text, (10, height - 70))

    # Mostrar la fecha y hora
    fecha_text = font.render(fecha.strftime("Fecha: %d/%m/%Y Hora: %H:%M"), True, white)
    screen.blit(fecha_text, (10, height - 40))

# Función para verificar si hay una calle adyacente
def hay_calle_adyacente(grilla, row, col):
    direcciones = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    for dr, dc in direcciones:
        nr, nc = row + dr, col + dc
        if 0 <= nr < len(grilla) and 0 <= nc < len(grilla[0]):
            if grilla[nr][nc] == 's':
                return True
    return False

# Bucle principal del juego
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
                if grilla[row][col] == 't' and hay_calle_adyacente(grilla, row, col):
                    grilla[row][col] = 'c'
                    dinero -= 50
                    mensaje = ""
                else:
                    mensaje = "¡Debe haber una calle adyacente para construir una casa!"
            elif modo == 'calle' and grilla[row][col] == 't':
                grilla[row][col] = 's'
                dinero -= 30
                mensaje = ""
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                modo = 'casa'
            elif event.key == pygame.K_2:
                modo = 'calle'

    # Actualizar la fecha y hora
    fecha += timedelta(minutes=1)
    
    screen.fill(black)
    dibujar_grilla(screen, grilla, dinero, mensaje, fecha)
    pygame.display.flip()
    
    # Limitar la velocidad del juego a 60 fps
    reloj.tick(60)

    # Verificar si el dinero llegó a $0
    if dinero <= 0:
        screen.fill(red)
        font = pygame.font.Font(None, 74)
        game_over_text = font.render("¡Juego Terminado!", True, white)
        screen.blit(game_over_text, (width//4, height//2 - 40))
        pygame.display.flip()
        pygame.time.wait(3000)
        pygame.quit()
        sys.exit()
