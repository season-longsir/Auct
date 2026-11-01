from constants import *

class Building:
    def __init__(self, btype: int, health: float, 
                 level: int, position: list[float, float]):
        self.type = btype
        self.health = health
        self.level = level
        self.position = position

class CentralB(Building):
    def __init__(self, health: float, level: int, position: list[float, float]):
        super().__init__(CCC, health, level, position)

class OffensiveB(Building):
    def __init__(self, health: float, subtype, damage: float, 
                 cooltime: float, level: int, position: list[float, float]):
        super().__init__(OB, health, level, position)
        self.damage = damage
        self.cooltime = cooltime
        self.subtype = subtype

class ResourseB(Building):
    def __init__(self, health: float, level: int, subtype: int, position: list[float, float]):
        super().__init__(RB, health, level, position)
        self.subtype = subtype

class DecorationB(Building):
    def __init__(self, level: int, subtype: int, position: list[float, float]):
        super().__init__(DEC, 0, level, position)
        self.subtype = subtype



class RapidFire(OffensiveB):
    def __init__(self, health: float, damage: float, cooltime:float, 
                 level: int, position: list[float, float]):
        super().__init__(health, RFG, damage, cooltime, level, position)

class PowerGen(ResourseB):
    def __init__(self, health: float, level: int, position: list[float, float]):
        super().__init__(health, level, PG, position)

class GoldMine(ResourseB):
    def __init__(self, health, level, position):
        super().__init__(health, level, GM, position)

class Tree(DecorationB):
    def __init__(self, level: int, position: list[float, float]):
        super().__init__(level, TREE, position)



# a = RapidFire(1,2,3,4,(1,2))
# print(a)
