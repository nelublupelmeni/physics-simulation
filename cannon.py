import pygame
import math
import pymunk
import config


class Cannon:
    """Класс для управления пушкой в симуляции."""

    def __init__(self, physics):
        """Инициализация пушки."""
        self.physics = physics
        # Начало координат в пикселях (0, 0 в метрах = 70, 700 в пикселях)
        self.x = 70  # Смещение пушки по X
        self.y = 700  # Смещение пушки по Y (для ствола и мячика)
        self.trajectory_points = []
        self.velocity_points = []
        self.range_data = []
        self.ball = None
        self.fired = False
        self.start_time = 0
        self.end_time = 0
        self.font = None
        self.scale_font = None
        self._setup_collision_handler()

    def _setup_collision_handler(self):
        """Настройка обработчика столкновений."""
        handler = self.physics.space.add_collision_handler(0, 0)
        handler.data["cannon"] = self
        handler.post_solve = self._collision_callback

    def _collision_callback(self, arbiter, space, data):
        """Обработка столкновений."""
        cannon = data["cannon"]
        if cannon.fired and cannon.ball in arbiter.shapes:
            for shape in arbiter.shapes:
                if isinstance(shape, pymunk.Poly) and shape.body.body_type == pymunk.Body.STATIC:
                    # Проверяем столкновение с землей (y ≈ 700)
                    if abs(shape.body.position.y - self.y) < 10:
                        if cannon.end_time == 0:
                            cannon.end_time = pygame.time.get_ticks()
                            if cannon.trajectory_points:
                                # Дальность относительно (0, 0) в метрах
                                max_x = max(x for x, y in self.trajectory_points)
                                range_m = (max_x - self.x) / 100  # Относительно x=70
                                angle = config.angle
                                cannon.range_data.append((angle, range_m))

    def handle_mouse_down(self, event):
        """Обработка нажатия кнопки мыши."""
        if event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            if config.shape_type == "button" and config.static_mode:
                try:
                    self.physics.add_shape(
                        shape_type="button",
                        radius=config.radius,
                        mass=config.mass,
                        pos=mouse_pos,
                        elasticity=config.elasticity,
                        friction=config.friction
                    )
                except:
                    pass
                return
            if self.ball:
                try:
                    self.physics.space.remove(self.ball.body, self.ball)
                except:
                    pass
                self.ball = None
            self.trajectory_points = []
            self.velocity_points = []
            self.ball = self.create_ball()

    def create_ball(self):
        """Создание мячика для выстрела."""
        try:
            # Начальная позиция мячика в (0, 0) метрах = (70, 700) пикселей
            ball = self.physics.add_shape(
                shape_type="circle",
                radius=config.radius,
                mass=config.mass,
                pos=(self.x, self.y),  # (70, 700)
                elasticity=config.elasticity,
                friction=config.friction
            )
            ball.body.body_type = pymunk.Body.KINEMATIC
            return ball
        except:
            return None

    def handle_mouse_up(self, event):
        """Обработка отпускания кнопки мыши."""
        if event.button == 1 and self.ball and config.shape_type != "button":
            try:
                self.ball.body.body_type = pymunk.Body.DYNAMIC
                angle_rad = math.radians(config.angle)
                velocity_x = config.initial_velocity * math.cos(angle_rad)
                velocity_y = -config.initial_velocity * math.sin(angle_rad)  # Отрицательная для движения вверх
                self.ball.body.velocity = (velocity_x, velocity_y)
                self.fired = True
                self.start_time = pygame.time.get_ticks()
                self.end_time = 0
            except:
                self.ball = None

    def update(self):
        """Обновление состояния пушки."""
        if self.fired and self.ball and self.ball.body and config.shape_type != "button":
            try:
                x, y = self.ball.body.position
                if not (isinstance(x, (int, float)) and isinstance(y, (int, float)) and
                        math.isfinite(x) and math.isfinite(y)):
                    self.fired = False
                    self.ball = None
                    return
                # Проверяем, достиг ли мячик земли (y ≥ 700)
                if y >= self.y and self.end_time == 0:
                    self.fired = False
                    self.end_time = pygame.time.get_ticks()
                    # Дальность относительно (0, 0)
                    self.trajectory_points.append((x, self.y))
                    max_x = max(x for x, y in self.trajectory_points)
                    range_m = (max_x - self.x) / 100  # Относительно x=70
                    angle = config.angle
                    self.range_data.append((angle, range_m))
                    return
                # Записываем траекторию
                self.trajectory_points.append((x, y))
                velocity = self.ball.body.velocity
                speed = math.sqrt(velocity[0]**2 + velocity[1]**2)
                elapsed_time = (pygame.time.get_ticks() - self.start_time) / 1000
                self.velocity_points.append((elapsed_time, speed / 100))
                if speed > 0 and config.air_resistance > 0:
                    rho = 1.225
                    C_d = 0.47
                    radius_m = config.radius / 100
                    A = math.pi * radius_m**2
                    k = 0.5 * rho * C_d * A * config.air_resistance
                    drag_force = (-k * speed * velocity[0], -k * speed * velocity[1])
                    self.ball.body.apply_force_at_local_point(drag_force, (0, 0))
            except:
                self.fired = False
                self.ball = None

    def draw(self, screen):
        """Отрисовка пушки и траектории."""
        if self.font is None:
            self.font = pygame.font.SysFont('Arial', 30)
        if self.scale_font is None:
            self.scale_font = pygame.font.SysFont('Arial', 20)

        METERS_TO_PIXELS = 100
        grid_step = METERS_TO_PIXELS
        origin_x = self.x  # Начало осей в (70, 700)
        origin_y = self.y

        axis_color = (255, 255, 255, 255) if config.theme == "dark" else (0, 0, 0, 255)
        text_color = (255, 255, 255, 255) if config.theme == "dark" else (0, 0, 0, 255)

        # Цвета пушки в зависимости от темы и режима
        cannon_base_color = (0, 150, 0) if config.shape_type == "button" and config.static_mode else (80, 80, 80)
        cannon_highlight_color = (0, 180, 0) if config.shape_type == "button" and config.static_mode else (100, 100, 100)
        barrel_color = (0, 150, 0) if config.shape_type == "button" and config.static_mode else (120, 120, 120)
        barrel_shadow_color = (50, 50, 50, 100)  # Полупрозрачная тень
        wheel_color = (60, 60, 60) if config.theme == "dark" else (40, 40, 40)

        # Рисуем оси с началом в (70, 700)
        pygame.draw.line(screen, axis_color, (origin_x, origin_y),
                         (self.physics.width, origin_y), 2)
        pygame.draw.line(screen, axis_color, (origin_x, origin_y), (origin_x, 0), 2)

        # Метки осей в метрах (Y вниз)
        for x in range(0, self.physics.width - origin_x, grid_step):
            meters_x = x // METERS_TO_PIXELS
            label = self.scale_font.render(f"{meters_x} м", True, text_color)
            screen.blit(label, (origin_x + x, origin_y + 5))

        for y in range(0, origin_y, grid_step):
            meters_y = y // METERS_TO_PIXELS  # Положительное Y вниз
            label = self.scale_font.render(f"{meters_y} м", True, text_color)
            screen.blit(label, (origin_x - 40, origin_y - y - 10))

        # Рисуем пушку с улучшенным дизайном
        # Ствол пушки (удлиненный, с тенью) — рисуем первым, чтобы он был позади
        end_x = self.x + 80 * math.cos(math.radians(config.angle))  # Удлиненный ствол
        end_y = self.y - 80 * math.sin(math.radians(config.angle))
        # Тень ствола
        pygame.draw.line(screen, barrel_shadow_color, (self.x + 2, self.y + 2),
                         (end_x + 2, end_y + 2), 7)
        # Основной ствол
        pygame.draw.line(screen, barrel_color, (self.x, self.y), (end_x, end_y), 5)
        # Подсветка ствола
        pygame.draw.line(screen, (200, 200, 200, 150), (self.x, self.y), (end_x, end_y), 2)

        # Основание пушки (скругленный прямоугольник с градиентом) — опущено вниз на 20 пикселей
        base_y = self.y + 20  # Сдвиг основания вниз
        pygame.draw.rect(screen, cannon_base_color, (self.x - 40, base_y - 25, 80, 30),
                         border_radius=5)
        pygame.draw.rect(screen, cannon_highlight_color, (self.x - 40, base_y - 25, 80, 15),
                         border_radius=5)  # Верхняя часть с подсветкой
        pygame.draw.rect(screen, (0, 0, 0, 50), (self.x - 40, base_y - 25, 80, 30), 2,
                         border_radius=5)  # Контур

        # Колеса пушки — также опущены вниз на 20 пикселей
        wheel_y = base_y + 5  # Сдвиг колес вниз
        pygame.draw.circle(screen, wheel_color, (self.x - 20, wheel_y), 10)  # Левое колесо
        pygame.draw.circle(screen, wheel_color, (self.x + 20, wheel_y), 10)  # Правое колесо
        pygame.draw.circle(screen, (255, 255, 255, 100), (self.x - 20, wheel_y), 3)  # Блик на левом колесе
        pygame.draw.circle(screen, (255, 255, 255, 100), (self.x + 20, wheel_y), 3)  # Блик на правом колесе

        # Рисуем траекторию
        for point in self.trajectory_points:
            try:
                if (isinstance(point, tuple) and len(point) == 2 and
                        isinstance(point[0], (int, float)) and
                        isinstance(point[1], (int, float)) and
                        math.isfinite(point[0]) and math.isfinite(point[1])):
                    pygame.draw.circle(screen, (200, 50, 50), (int(point[0]), int(point[1])), 2)
            except:
                pass

        # Отображаем время
        if self.fired or self.end_time > 0:
            current_time = pygame.time.get_ticks()
            elapsed_time = (self.end_time if self.end_time > 0 else current_time) - self.start_time
            elapsed_time /= 1000
            timer_text = self.font.render(f"Время: {elapsed_time:.2f} сек", True, text_color)
            screen.blit(timer_text, (screen.get_width() - 220, 10))

    def reset(self):
        """Сброс состояния пушки."""
        if self.ball:
            try:
                self.physics.space.remove(self.ball.body, self.ball)
            except:
                pass
            self.ball = None
        self.trajectory_points = []
        self.velocity_points = []
        self.fired = False
        self.start_time = 0
        self.end_time = 0