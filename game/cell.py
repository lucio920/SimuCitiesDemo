from abc import abstractmethod

class Cell:
    def __init__(self, cost):
        self.__cost = cost

    def chargeCost(self, fromAmount):
        return fromAmount - self.__cost

class Land(Cell):
    def __init__(self):
        super().__init__(100)

class House(Cell):
    def __init__(self):
        super().__init__(0)

class Road(Cell):
    def __init__(self):
        super().__init__(30)

class Water(Cell):
    def __init__(self):
        super().__init__(0)

class Construction(Cell):
    def __init__(self):
        super().__init__(50)

