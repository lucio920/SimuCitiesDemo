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
orange = (255, 165, 0)

# Crear la pantalla
screen = pygame.display.set_mode(size)

# Generar la grilla con menos bloques de agua
def generar_grilla():
    grilla = []
    for _ in range(10):
        fila = []
        for _ in range(10):
            letra = 'T' if random.random() < 0.8 else 'A'  # 80% tierra, 20% agua
            fila.append(letra)
        grilla.append(fila)
    return grilla

grilla = generar_grilla()
dinero = 1000
modo = 'casa'  # Por defecto, construye casa
fecha = datetime(1993, 1, 1, 0, 0)  # Fecha inicial

# Mantener un registro del tiempo de construcción y ganancias
obras = {}
ultimo_ingreso = pygame.time.get_ticks()
ultimo_tornado = pygame.time.get_ticks()
mensaje_mostrar_hasta = 0

# Función para dibujar la grilla
def dibujar_grilla(screen, grilla, dinero, mensaje, fecha, tiempo_actual):
    for i, fila in enumerate(grilla):
        for j, letra in enumerate(fila):
            rect = pygame.Rect(j * cell_size, i * cell_size, cell_size, cell_size)
            if letra == 'A':
                color_fondo = blue
            elif letra == 'T':
                color_fondo = brown
            elif letra == 'C':
                color_fondo = yellow
            elif letra == 'S':
                color_fondo = grey
            elif letra == 'O':  # Obra en construcción
                color_fondo = orange
            else:
                color_fondo = black
            pygame.draw.rect(screen, color_fondo, rect)
            pygame.draw.rect(screen, black, rect, 1)
            font = pygame.font.Font(None, 74)
            text = font.render(letra, True, white)
            text_rect = text.get_rect(center=rect.center)
            screen.blit(text, text_rect.topleft)
    
    # Mostrar el dinero restante
    font = pygame.font.Font(None, 36)
    dinero_text = font.render(f"Dinero: ${dinero}", True, white)
    screen.blit(dinero_text, (10, height - 100))
    
    # Mostrar el mensaje y aplicar fade out después de 5 segundos
    if mensaje and tiempo_actual <= mensaje_mostrar_hasta:
        alpha = int(255 * (mensaje_mostrar_hasta - tiempo_actual) / 5000)
        mensaje_text = font.render(mensaje, True, (red[0], red[1], red[2], alpha))
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
            if grilla[nr][nc] == 'S':
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

    # Actualizar las obras en construcción
    tiempo_actual = pygame.time.get_ticks()
    for (row, col), inicio in list(obras.items()):
        if tiempo_actual - inicio > 10000:  # 10 segundos
            grilla[row][col] = 'C'
            del obras[(row, col)]

    # Generar ingresos cada 5 segundos por cada casa
    if tiempo_actual - ultimo_ingreso > 5000:
        for fila in grilla:
            dinero += fila.count('C') * 10
        ultimo_ingreso = tiempo_actual

    # Evento de tornado cada 30 segundos
    if tiempo_actual - ultimo_tornado > 30000:
        for i in range(random.randint(1, 10)):  # El tornado afecta entre 1 y 10 casas
            casas = [(r, c) for r, fila in enumerate(grilla) for c, letra in enumerate(fila) if letra == 'C']
            if casas:
                row, col = random.choice(casas)
                grilla[row][col] = 'O'
                obras[(row, col)] = pygame.time.get_ticks()
                dinero -= 20
        mensaje = "¡Un tornado ha pasado y algunas casas han vuelto a ser obras!"
        mensaje_mostrar_hasta = tiempo_actual + 5000
        ultimo_tornado = tiempo_actual

    # Actualizar la fecha y hora
    fecha += timedelta(minutes=1)
    
    screen.fill(black)
    dibujar_grilla(screen, grilla, dinero, mensaje, fecha, tiempo_actual)
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
