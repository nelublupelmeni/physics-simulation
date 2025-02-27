import pymunk
from slingshot import Slingshot
from cannon import Cannon

# отрисовка объектов на экране
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

    # добавляет мяч с заданными параметрами
    def add_ball(self, radius, mass, pos, elasticity=0.9, friction=0.4):
        body = pymunk.Body()
        body.position = pos
        shape = pymunk.Circle(body, radius)
        shape.mass = mass
        shape.elasticity = elasticity
        shape.friction = friction
        shape.color = (255, 0, 0, 100)
        shape.hue = 0
        self.space.add(body, shape)
        return shape

    # обновляет физическую симуляцию
    def update(self, dt):
        self.space.step(dt)
        for body in self.space.bodies:
            for shape in body.shapes:
                if isinstance(shape, pymunk.Circle):
                    shape.hue = (shape.hue + 0.5) % 360

    # очищает все динамические объекты
    def clear_objects(self):
        for body in self.space.bodies:
            if body.body_type == pymunk.Body.DYNAMIC:
                self.space.remove(body, *body.shapes)

    # задает силу гравитации
    def set_gravity(self, gravity):
        self.space.gravity = (0, gravity)

    # возвращает список объектов в симуляции
    def get_objects(self):
        objects = []
        for body in self.space.bodies:
            for shape in body.shapes:
                if isinstance(shape, pymunk.Circle):
                    objects.append({
                        "type": "ball",
                        "position": body.position,
                        "radius": shape.radius
                    })
        return objects