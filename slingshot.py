import math
import pygame
import pymunk
import config


class Slingshot:
    """Класс для управления рогаткой в симуляции."""
    MAX_SLINGSHOT_LENGTH = 400.0  # Maximum slingshot stretch distance in pixels

    def __init__(self, physics):
        """Инициализация рогатки."""
        self.physics = physics
        self.shape = None
        self.pressed_pos = None
        self.is_dragging = False

    def handle_mouse_down(self, event):
        """Обработка нажатия кнопки мыши."""
        if event.button != 1:  # Only handle left mouse button
            return
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
            except Exception as e:
                print(f"Error creating button shape: {e}")
            return
        if not self.shape:
            self.pressed_pos = mouse_pos
            # Check for existing dynamic shape under cursor
            point_query = self.physics.space.point_query_nearest(
                mouse_pos, max_distance=10, shape_filter=pymunk.ShapeFilter(categories=0x1, mask=0x1)
            )
            if point_query and point_query.shape and point_query.shape.body.body_type == pymunk.Body.DYNAMIC:
                self.shape = point_query.shape
                try:
                    self.shape.body.body_type = pymunk.Body.STATIC
                    self.is_dragging = True
                    print(f"Selected existing shape at {mouse_pos}")
                except Exception as e:
                    print(f"Error selecting shape: {e}")
                    self.shape = None
            else:
                try:
                    self.shape = self.physics.add_shape(
                        shape_type=config.shape_type,
                        radius=config.radius,
                        mass=config.mass,
                        pos=self.pressed_pos,
                        elasticity=config.elasticity,
                        friction=config.friction
                    )
                    if self.shape:
                        self.shape.body.body_type = pymunk.Body.STATIC
                        self.is_dragging = True
                       
                    else:
                        print("Failed to create shape")
                except Exception as e:
                    print(f"Error creating shape: {e}")
                    self.shape = None

    def handle_mouse_up(self, event):
        """Обработка отпускания кнопки мыши."""
        if event.button != 1 or not self.shape or not self.is_dragging:
            return
        mouse_pos = pygame.mouse.get_pos()
        dx = mouse_pos[0] - self.pressed_pos[0]
        dy = mouse_pos[1] - self.pressed_pos[1]
        distance = math.hypot(dx, dy)
        if distance > self.MAX_SLINGSHOT_LENGTH:
            dx = dx * self.MAX_SLINGSHOT_LENGTH / distance
            dy = dy * self.MAX_SLINGSHOT_LENGTH / distance
            distance = self.MAX_SLINGSHOT_LENGTH
        angle = math.atan2(dy, dx)
        if config.mass < 7:
            force = distance * 40 * 0.1
        else:
            force = distance * 40
        fx = -math.cos(angle) * force  
        fy = -math.sin(angle) * force  
        try:
            self.shape.body.body_type = pymunk.Body.DYNAMIC
            self.shape.body.apply_impulse_at_local_point((fx, fy), (0, 0))
            self.is_dragging = False
            self.shape = None
            self.pressed_pos = None
        except Exception as e:
            print(f"Error releasing shape: {e}")
            self.shape = None
            self.is_dragging = False
            self.pressed_pos = None

    def update(self):
        """Обновление состояния рогатки."""
        if not self.is_dragging or not self.shape:
            return
        mouse_pos = pygame.mouse.get_pos()
        dx = mouse_pos[0] - self.pressed_pos[0]
        dy = mouse_pos[1] - self.pressed_pos[1]
        distance = math.hypot(dx, dy)
        if distance > self.MAX_SLINGSHOT_LENGTH:
            dx = dx * self.MAX_SLINGSHOT_LENGTH / distance
            dy = dy * self.MAX_SLINGSHOT_LENGTH / distance
        try:
            self.shape.body.position = (self.pressed_pos[0] + dx, self.pressed_pos[1] + dy)
        except Exception as e:
            print(f"Error updating shape position: {e}")
            self.shape = None
            self.is_dragging = False

    def draw(self, screen):
        """Отрисовка рогатки на экране."""
        if not self.is_dragging or not self.pressed_pos or not self.shape:
            return
        mouse_pos = pygame.mouse.get_pos()
        dx = mouse_pos[0] - self.pressed_pos[0]
        dy = mouse_pos[1] - self.pressed_pos[1]
        distance = math.hypot(dx, dy)
        if distance > self.MAX_SLINGSHOT_LENGTH:
            dx = dx * self.MAX_SLINGSHOT_LENGTH / distance
            dy = dy * self.MAX_SLINGSHOT_LENGTH / distance
            mouse_pos = (self.pressed_pos[0] + dx, self.pressed_pos[1] + dy)
        pygame.draw.line(screen, (0, 0, 0), self.pressed_pos, mouse_pos, 2)

    def reset(self):
        """Сброс состояния рогатки."""
        if self.shape:
            try:
                self.physics.space.remove(self.shape.body, self.shape)
                print("Slingshot reset: Shape removed")
            except Exception as e:
                print(f"Error resetting slingshot: {e}")
            self.shape = None
        self.pressed_pos = None
        self.is_dragging = False