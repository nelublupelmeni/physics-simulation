import pymunk
from slingshot import Slingshot
from cannon import Cannon

class PhysicsWorld:
    def __init__(self, width, height):
        self.space = pymunk.Space()
        self.space.gravity = (0, 981)
        self.width = width
        self.height = height
        self._create_boundaries()
        self.slingshot = Slingshot(self)
        self.cannon = Cannon(self)

    def _create_boundaries(self):
        boundaries = [
            [(self.width / 2, self.height - 5), (self.width, 10)],
            [(self.width / 2, 5), (self.width, 10)],
            [(5, self.height / 2), (10, self.height)],
            [(self.width - 5, self.height / 2), (10, self.height)]
        ]

        for pos, size in boundaries:
            body = pymunk.Body(body_type=pymunk.Body.STATIC)
            body.position = pos
            shape = pymunk.Poly.create_box(body, size)
            shape.elasticity = 0.4
            shape.friction = 0.5
            self.space.add(body, shape)

    def add_shape(self, shape_type, radius, mass, pos, elasticity=0.9, friction=0.4):
        body = pymunk.Body()
        body.position = pos
        if shape_type == "circle":
            shape = pymunk.Circle(body, radius)
            shape.color = (255, 0, 0, 100)  # Red for circles
        elif shape_type == "square":
            # Create a square with side length equal to diameter (2 * radius)
            side_length = 2 * radius
            shape = pymunk.Poly.create_box(body, (side_length, side_length))
            shape.color = (0, 0, 255, 100)  # Blue for squares
        else:
            raise ValueError(f"Unknown shape_type: {shape_type}")
        shape.mass = mass
        shape.elasticity = elasticity
        shape.friction = friction
        shape.hue = 0  # Initialize hue for color effect
        self.space.add(body, shape)
        return shape

    def update(self, dt):
        self.space.step(dt)
        for body in self.space.bodies:
            if body.body_type == pymunk.Body.DYNAMIC:  # Only dynamic shapes
                for shape in body.shapes:
                    if isinstance(shape, (pymunk.Circle, pymunk.Poly)):
                        shape.hue = (shape.hue + 0.5) % 360

    def clear_objects(self):
        for body in self.space.bodies:
            if body.body_type == pymunk.Body.DYNAMIC:
                self.space.remove(body, *body.shapes)

    def set_gravity(self, gravity):
        self.space.gravity = (0, gravity)

    def get_objects(self):
        objects = []
        for body in self.space.bodies:
            for shape in body.shapes:
                if isinstance(shape, pymunk.Circle):
                    objects.append({
                        "type": "circle",
                        "position": body.position,
                        "radius": shape.radius
                    })
                elif isinstance(shape, pymunk.Poly):
                    # Check if it's a square (dynamic body) vs boundary (static)
                    if body.body_type == pymunk.Body.DYNAMIC:
                        objects.append({
                            "type": "square",
                            "position": body.position,
                            "size": shape.get_vertices()[1][0] * 2  # Side length
                        })
        return objects