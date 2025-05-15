import pymunk
import math
from slingshot import Slingshot
from cannon import Cannon


class PhysicsWorld:
    """Класс для управления физическим миром симуляции."""

    def __init__(self, width, height):
        """Инициализация физического мира."""
        self.space = pymunk.Space()
        self.space.gravity = (0, 981)
        self.width = width
        self.height = height
        self._create_boundaries()
        self.slingshot = Slingshot(self)
        self.cannon = Cannon(self)

    def _create_boundaries(self):
        """Создание границ физического мира."""
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
            shape.color = (128, 128, 128, 255)  # Серый цвет по умолчанию для границ
            self.space.add(body, shape)

    def add_shape(self, shape_type, radius, mass, pos, elasticity=0.9, friction=0.4):
        """Добавление формы в физический мир."""
        if shape_type == "button":
            body = pymunk.Body(body_type=pymunk.Body.STATIC)
        else:
            body = pymunk.Body()
        body.position = pos
        if shape_type == "circle":
            shape = pymunk.Circle(body, radius)
            shape.color = (255, 0, 0, 100)  # Красный для кругов
        elif shape_type == "square":
            side_length = 2 * radius
            shape = pymunk.Poly.create_box(body, (side_length, side_length))
            shape.color = (0, 0, 255, 100)  # Синий для квадратов
        elif shape_type == "triangle":
            side_length = 2 * radius
            height = (math.sqrt(3) / 2) * side_length
            vertices = [
                (0, -height / 3),
                (-side_length / 2, height * 2 / 3),
                (side_length / 2, height * 2 / 3)
            ]
            shape = pymunk.Poly(body, vertices)
            shape.color = (255, 255, 0, 100)  # Желтый для треугольников
        elif shape_type == "button":
            shape = pymunk.Circle(body, radius)
            shape.color = (0, 255, 0, 100)  # Зеленый для кнопок
        else:
            raise ValueError(f"Неизвестный тип формы: {shape_type}")
        if shape_type != "button":
            shape.mass = mass
            shape.hue = 0 
        shape.elasticity = elasticity
        shape.friction = friction
        try:
            self.space.add(body, shape)
        except Exception as e:
            print(f"Ошибка при добавлении формы в пространство: {e}")
            return None
        return shape

    def update(self, dt):
        """Обновление физического мира."""
        self.space.step(dt)
        for body in self.space.bodies:
            if body.body_type == pymunk.Body.DYNAMIC:
                for shape in body.shapes:
                    if isinstance(shape, (pymunk.Circle, pymunk.Poly)):
                        shape.hue = (shape.hue + 0.5) % 360

    def clear_objects(self):
        """Очистка всех объектов, кроме границ."""
        boundary_positions = [
            (self.width / 2, self.height - 5),
            (self.width / 2, 5),
            (5, self.height / 2),
            (self.width - 5, self.height / 2)
        ]
        for body in self.space.bodies:
            if (body.body_type == pymunk.Body.DYNAMIC or
                    (body.body_type == pymunk.Body.STATIC and
                     body.position not in boundary_positions)):
                self.space.remove(body, *body.shapes)

    def set_gravity(self, gravity):
        """Установка значения гравитации."""
        self.space.gravity = (0, gravity)

    def get_objects(self):
        """Получение списка объектов в физическом мире."""
        objects = []
        for body in self.space.bodies:
            for shape in body.shapes:
                if isinstance(shape, pymunk.Circle):
                    objects.append({
                        "type": "circle" if body.body_type != pymunk.Body.STATIC else "button",
                        "position": body.position,
                        "radius": shape.radius
                    })
                elif isinstance(shape, pymunk.Poly):
                    if body.body_type == pymunk.Body.DYNAMIC:
                        vertices = shape.get_vertices()
                        if len(vertices) == 4:
                            objects.append({
                                "type": "square",
                                "position": body.position,
                                "size": vertices[1][0] * 2
                            })
                        elif len(vertices) == 3:
                            objects.append({
                                "type": "triangle",
                                "position": body.position,
                                "size": math.hypot(vertices[1][0] - vertices[2][0],
                                                  vertices[1][1] - vertices[2][1])
                            })
        return objects