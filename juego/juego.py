from datetime import datetime
import random


class Juego:

    def __init__(self, dinero_inicial=1000, modo_inicial='casa', fecha_inicial=datetime(1993, 1, 1, 0, 0)):
        self.grilla = self.generar_grilla()
        self.dinero = dinero_inicial
        self.modo = modo_inicial
        self.fecha = fecha_inicial
        self.tiempo_actual = 0

    def generar_grilla(self):
        grilla = []
        for _ in range(10):
            fila = []
            for _ in range(10):
                letra = 'T' if random.random() < 0.8 else 'A'
                fila.append(letra)
            grilla.append(fila)
        return grilla

    def actualizar_tiempo(self, tiempo):
        self.tiempo_actual = tiempo