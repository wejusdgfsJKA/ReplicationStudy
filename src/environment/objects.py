class WorldObject:
    def __init__(self, pos):
        self.pos = pos
        self.picked_up = False


class Hub(WorldObject):
    type = "Hub"

    def __init__(self, pos, radius=10, debris_boundary=30):
        super().__init__(pos)
        self.radius = radius
        self.debris_boundary = debris_boundary


class Site(WorldObject):
    type = "Site"


class Food(WorldObject):
    type = "Food"


class Debris(WorldObject):
    type = "Debris"
