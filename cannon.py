import pygame
import math
import pymunk
from ui import UIData

class Cannon:
    def __init__(self, physics): #инициализация пушки
        self.physics = physics
        self.x = 100
        self.y = physics.height - 25
        self.trajectory_points = []
        self.ball = None
        self.fired = False
        self.start_time = 0
        self.end_time = 0
        self.font = None
        self.scale_font = None
        self._setup_collision_handler()

    # отслеживает столкновение с землей, чтобы остановить таймер (единственный способ, который у меня заработал)
    def _setup_collision_handler(self): 
        handler = self.physics.space.add_collision_handler(0, 0)
        handler.data["cannon"] = self
        handler.post_solve = self._collision_callback

    def _collision_callback(self, arbiter, space, data):
        cannon = data["cannon"]
        if cannon.fired and cannon.ball in arbiter.shapes:
            for shape in arbiter.shapes:
                if isinstance(shape, pymunk.Poly) and shape.body.body_type == pymunk.Body.STATIC:
                    if abs(shape.body.position.y - (self.physics.height - 5)) < 10:
                        cannon.fired = False
                        if cannon.end_time == 0:
                            cannon.end_time = pygame.time.get_ticks()

    # обрабатывает нажатие мыши - перезаряжает пушку
    def handle_mouse_down(self, event):
        if event.button == 1:
            if self.ball:
                self.physics.space.remove(self.ball.body, self.ball)
                self.ball = None
            self.trajectory_points = []
            self.ball = self.create_ball()

    # создает мяч для выстрела
    def create_ball(self):
        ball = self.physics.add_ball(
            radius=UIData.radius,
            mass=UIData.mass,
            pos=(self.x + 30, self.y - 20),
            elasticity=UIData.elasticity,
            friction=UIData.friction,
        )
        ball.body.body_type = pymunk.Body.KINEMATIC
        return ball

    # обрабатывает "выстрел из пушки"
    def handle_mouse_up(self, event):
        if event.button == 1 and self.ball:
            self.ball.body.body_type = pymunk.Body.DYNAMIC
            angle_rad = math.radians(UIData.angle)
            velocity_x = UIData.initial_velocity * math.cos(angle_rad)
            velocity_y = -UIData.initial_velocity * math.sin(angle_rad)
            self.ball.body.velocity = (velocity_x, velocity_y)
            self.fired = True
            self.start_time = pygame.time.get_ticks()
            self.end_time = 0

    # обновляет состояние пушки
    def update(self): 
        if self.fired and self.ball:
            x, y = self.ball.body.position
            self.trajectory_points.append((x, y)) # добавляет траекторию

    # отрисовывает пушку и элементы интерфейса
    def draw(self, screen):
        if self.font is None:
            self.font = pygame.font.SysFont('Arial', 30)
        if self.scale_font is None:
            self.scale_font = pygame.font.SysFont('Arial', 20)

        METERS_TO_PIXELS = 100
        grid_step = METERS_TO_PIXELS
        origin_x = self.x
        origin_y = self.y

        pygame.draw.line(screen, (0, 0, 0, 128), (origin_x, origin_y), (self.physics.width, origin_y), 2)
        pygame.draw.line(screen, (0, 0, 0, 128), (origin_x, origin_y), (origin_x, 0), 2)

        for x in range(0, self.physics.width - origin_x, grid_step):
            meters_x = x // METERS_TO_PIXELS
            label = self.scale_font.render(f"{meters_x} м", True, (0, 0, 0, 128))
            screen.blit(label, (origin_x + x, origin_y + 5))

        for y in range(0, origin_y, grid_step):
            meters_y = y // METERS_TO_PIXELS
            label = self.scale_font.render(f"{meters_y} м", True, (0, 0, 0, 128))
            screen.blit(label, (origin_x - 40, origin_y - y - 10))

        pygame.draw.rect(screen, (100, 100, 100), (self.x, self.y - 20, 60, 20))
        end_x = self.x + 30 + 60 * math.cos(math.radians(UIData.angle))
        end_y = self.y - 20 - 60 * math.sin(math.radians(UIData.angle))
        pygame.draw.line(screen, (150, 150, 150), (self.x + 30, self.y - 20), (end_x, end_y), 3)

        for point in self.trajectory_points:
            pygame.draw.circle(screen, (200, 50, 50), (int(point[0]), int(point[1])), 2)

        if self.fired or self.end_time > 0:
            current_time = pygame.time.get_ticks()
            elapsed_time = (self.end_time if self.end_time > 0 else current_time) - self.start_time
            elapsed_time /= 1000
            timer_text = self.font.render(f"Время: {elapsed_time:.2f} сек", True, (0, 0, 0))
            screen.blit(timer_text, (screen.get_width() - 220, 10))

    # сбрасывает состояние пушки
    def reset(self):
        if self.ball:
            self.physics.space.remove(self.ball.body, self.ball)
            self.ball = None
        self.trajectory_points = []
        self.fired = False
        self.start_time = 0
        self.end_time = 0