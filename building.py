from constants import *

class Building:
    def __init__(self, btype: int, health: float, level: int):
        self.type = btype
        self.health = health
        self.level = level

class CentralB(Building):
    def __init__(self, health: float, level: int):
        super().__init__(CCC, health, level)

class OffensiveB(Building):
    def __init__(self, health: float, subtype, damage: float, 
                 cooltime: float, level: int):
        super().__init__(OB, health, level)
        self.damage = damage
        self.cooltime = cooltime
        self.subtype = subtype

class ResourseB(Building):
    def __init__(self, health: float, level: int, subtype: int):
        super().__init__(RB, health, level)
        self.subtype = subtype

class DecorationB(Building):
    def __init__(self, level: int, subtype: int):
        super().__init__(DEC, 0, level)
        self.subtype = subtype
