from enum import Enum


class SObjects(Enum):
    Site = 1,
    Hub = 2


class DObjects(Enum):
    Food = 1,
    Debris = 2


def dist(a, b):
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5
