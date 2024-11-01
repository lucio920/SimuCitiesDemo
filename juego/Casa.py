from juego.celda import Celda


class Casa(Celda):
    def cambiar_estado(self, tipo):
        if tipo == 'C' and self.grilla.hay_calle_adyacente(self.row, self.col):
            return (True, Casa())

        return (False, self)