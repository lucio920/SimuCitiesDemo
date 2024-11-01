from datetime import datetime
import random

from juego.celda import Celda


class Juego:

    def __init__(self, dinero_inicial=1000, modo_inicial='casa', fecha_inicial=datetime(1993, 1, 1, 0, 0)):
        self.grilla = self.generar_grilla()
        self.dinero = dinero_inicial
        self.modo = modo_inicial
        self.fecha = fecha_inicial
        self.tiempo_actual = 0

    def generar_grilla(self):
        grilla = []
        for row in range(10):
            fila = []
            for col in range(10):
                letra = 'T' if random.random() < 0.8 else 'A'
                fila.append(Celda(row, col, letra))
            grilla.append(fila)
        return grilla

    def actualizar_tiempo(self, tiempo):
        self.tiempo_actual = tiempo

    def actualizar_fecha(self, delta):
        self.fecha += delta

    def hay_calle_adyacente(self, row, col):
        direcciones = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in direcciones:
            nr, nc = row + dr, col + dc
            if 0 <= nr < len(self.grilla) and 0 <= nc < len(self.grilla[0]):
                if self.grilla[nr][nc] == 'S':
                    return True
        return False

    #def actualizar_celda(self, row, col, tipo, dinero):
    #    self.grilla[row][col].
