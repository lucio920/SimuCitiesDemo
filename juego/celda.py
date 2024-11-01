from abc import abstractmethod
from typing import override


class Celda:

    def __init__(self, row, col, grilla, tipo):
        self.row = row
        self.col = col
        self.tipo = tipo
        self.grilla = grilla

    @abstractmethod
    def cambiar_estado(self, tipo):
        pass