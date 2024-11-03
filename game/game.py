from datetime import datetime, timedelta
import random

from game.cell import Land, Construction, Road
from game.cell import Water
from game.cell import House

class Game:
    __CELL_LAND_PROB = 0.8

    def __init__(self, rows=10, cols=10, money=1000, date=datetime(1993, 1, 1, 0, 0)):
        self.__grid = self.__gridInit(rows, cols)
        self.__constructions = dict()
        self.__money = money
        self.__date = date
        self.__lastTaxCollectionDate = date
        self.__lastTornadoDate = date
        self.__lastEarthquakeDate = date
        self.__tornadoHasPassed = False
        self.__earthquakeHasPassed = False

    # __gridInit defines the game grid and sets a random amount of land and water.
    def __gridInit(self, rows, cols):
        grid = []
        for rowNum in range(rows):
            row = []
            for colNum in range(cols):
                cell = Land() if random.random() < self.__CELL_LAND_PROB else Water()
                row.append(cell)
            grid.append(row)
        return grid

    # updateGameState advances everything in the game, by a delta in date.
    def updateGameState(self, delta):
        self.__date += delta
        self.__advanceContructionSites()
        self.__collectTaxes()
        self.__tornadoEventRun()
        self.__earthquakeEventRun()


    # __tornadoEventRun returns a random amount of houses back to construction state, and charges some money for it.
    def __tornadoEventRun(self):
        if self.__date - self.__lastTornadoDate >= timedelta(days=2):
            numAffectedHouses = random.randint(1, 10)  # Número aleatorio de casas afectadas por el terremoto
            houses = [
                (r, c)
                for r, row in enumerate(self.__grid)
                for c, cell in enumerate(row) if isinstance(cell, House)
            ]
            self.__money -= min(numAffectedHouses, len(houses)) * 20 # 20$ each.
            for _ in range(numAffectedHouses):
                if houses:
                    row, col = random.choice(houses)
                    self.__grid[row][col] = Construction()
                    houses.remove((row, col))
                    self.__constructions[(row, col)] = self.__date

            self.__lastTornadoDate = self.__date
            self.__tornadoHasPassed = True

    # hasTornadoPassed returns true if there was a tornado after the last time checked.
    def hasTornadoPassed(self):
        if self.__tornadoHasPassed:
            self.__tornadoHasPassed = False
            return True

        return False

    # __earthquakeEventRun returns a random amount of houses back to land state, and charges some money for it.
    def __earthquakeEventRun(self):
        if random.randint(0, 10) >= 5 and self.__date - self.__lastEarthquakeDate > timedelta(days=5):
            numAffectedHouses = random.randint(1, 15)
            houses = [
                (r, c)
                for r, row in enumerate(self.__grid)
                for c, cell in enumerate(row) if isinstance(cell, House)
            ]
            self.__money -= min(numAffectedHouses, len(houses)) * 50  # 50$ each.
            for _ in range(numAffectedHouses):
                if houses:
                    row, col = random.choice(houses)
                    self.__grid[row][col] = Land()
                    houses.remove((row, col))
            self.__lastEarthquakeDate = self.__date
            self.__earthquakeHasPassed = True

    # hasEarthquakePassed returns true if there was an earthquake after the last time checked.
    def hasEarthquakePassed(self):
        if self.__earthquakeHasPassed:
            self.__earthquakeHasPassed = False
            return True

        return False

    # __advanceConstructionSites advances construction sites to houses if a given time has passed since creation.
    def __advanceContructionSites(self):
        for (row, col), startDate in list(self.__constructions.items()):
            if self.__date - startDate >= timedelta(hours=10):
                self.__advanceCell(row, col, House())
                del self.__constructions[(row, col)]

    # __collectTaxes increases the amount of money for each cell, being the amount managed by each cell.
    def __collectTaxes(self):
        if self.__date - self.__lastTaxCollectionDate > timedelta(days=1):
            for row in self.__grid:
                self.__money += sum(isinstance(cell, House) for cell in row) * 10 # 10 simoleons for each house built.
            self.__lastTaxCollectionDate = self.__date

    # TODO: QUIZAS HACER QUE LAS CELDAS CONOZCAN SUS ADYACENTES Y PASAR ESTA LOGICA DIRECTO A LA CELDA
    #  (POR EJEMPLO QUE CELDA TENGA UN METODO "canBuild()" que devuelva un booleano, y cada tipo de celda lo implemente a su gusto)?
    # __isStreetAdjacent returns a boolean if the cell by its given coordinates row, col is adjacent to at least one road type cell.
    def __isStreetAdjacent(self, row, col):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in directions:
            nr, nc = row + dr, col + dc
            if 0 <= nr < len(self.__grid) and 0 <= nc < len(self.__grid[0]):
                if isinstance(self.__grid[nr][nc], Road):
                    return True
        return False

    # buildHouse returns a boolean indicating if a house was built on the given coordinates.
    def buildHouse(self, row, col):
        if isinstance(self.__grid[row][col], Land) and self.__isStreetAdjacent(row, col):
            self.__advanceCell(row, col, Construction())
            self.__constructions[(row, col)] = self.__date
            return True

        return False

    # buildRoad returns a boolean indicating if a road was built on the given coordinates.
    def buildRoad(self, row, col):
        if isinstance(self.__grid[row][col], Land):
            self.__advanceCell(row, col, Road())
            return True

        return False

    # buildRoad returns a boolean indicating if a house was demolished on the given coordinates.
    def demolish(self, row, col):
        if isinstance(self.__grid[row][col], House):
            self.__advanceCell(row, col, Land())
            return True

        return False

    # __advanceCell sets a new cell in the given coordinates, and charges a set amount of money given by the new cell.
    def __advanceCell(self, row, col, newCell):
        self.__grid[row][col] = newCell
        self.__money = self.__grid[row][col].chargeCost(self.__money)

    # isGameOver returns a boolean indicating is the game was lost.
    def isGameOver(self):
        return self.__money <= 0

    # isGameWin returns a boolean indicating if the game was won.
    def isGameWin(self):
        return self.__money >= 2000

    # getGameData is a getter that is used to pass game information to be drawed on the screen.
    def getGameData(self):
        return self.__grid, self.__money, self.__date, self.__constructions