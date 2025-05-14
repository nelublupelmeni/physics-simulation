import math
import pygame
import pymunk
import config


class Slingshot:
    """Класс для управления рогаткой в симуляции."""

    def __init__(self, physics):
        """Инициализация рогатки."""
        self.physics = physics
        self.shape = None  # For LMB slingshot dragging (circle, square, or triangle)
        self.pressed_pos = None
        self.is_dragging = False
        self.rmb_shape = None  # For RMB direct dragging
        self.is_rmb_dragging = False

    def handle_mouse_down(self, event):
        """Обработка нажатия кнопки мыши."""
        mouse_pos = pygame.mouse.get_pos()
        if event.button == 1:  # Left mouse button
            if config.shape_type == "button" and config.static_mode:
                # Create a static button shape at the clicked position
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
                # Query the physics space to find a dynamic shape under the mouse
                point_query = self.physics.space.point_query_nearest(
                    mouse_pos, max_distance=10, shape_filter=pymunk.ShapeFilter(categories=0x1, mask=0x1)
                )
                if point_query and point_query.shape and point_query.shape.body.body_type == pymunk.Body.DYNAMIC:
                    self.shape = point_query.shape
                    try:
                        self.shape.body.body_type = pymunk.Body.STATIC
                        self.is_dragging = True
                    except Exception as e:
                        print(f"Error selecting shape for LMB: {e}")
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
                        self.shape.body.body_type = pymunk.Body.STATIC
                        self.is_dragging = True
                    except Exception as e:
                        print(f"Error creating shape: {e}")
                        self.shape = None
        elif event.button == 3:  # Right mouse button (direct dragging)
            if not self.rmb_shape:
                point_query = self.physics.space.point_query_nearest(
                    mouse_pos, max_distance=10, shape_filter=pymunk.ShapeFilter(categories=0x1, mask=0x1)
                )
                if point_query and point_query.shape and point_query.shape.body.body_type == pymunk.Body.DYNAMIC:
                    self.rmb_shape = point_query.shape
                    try:
                        self.rmb_shape.body.body_type = pymunk.Body.STATIC
                        self.is_rmb_dragging = True
                    except Exception as e:
                        print(f"Error selecting shape for RMB: {e}")
                        self.rmb_shape = None

    def handle_mouse_up(self, event):
        """Обработка отпускания кнопки мыши."""
        if event.button == 1 and self.shape and self.is_dragging:
            mouse_pos = pygame.mouse.get_pos()
            angle = math.atan2(self.pressed_pos[1] - mouse_pos[1], self.pressed_pos[0] - mouse_pos[0])
            force = math.hypot(self.pressed_pos[0] - mouse_pos[0], self.pressed_pos[1] - mouse_pos[1]) * 20
            fx = math.cos(angle) * force
            fy = math.sin(angle) * force
            try:
                self.shape.body.body_type = pymunk.Body.DYNAMIC
                self.shape.body.apply_impulse_at_local_point((fx, fy), (0, 0))
                self.is_dragging = False
                self.shape = None
                self.pressed_pos = None
            except Exception as e:
                print(f"Error in LMB handle_mouse_up: {e}")
                self.shape = None
                self.is_dragging = False
                self.pressed_pos = None
        elif event.button == 3 and self.rmb_shape and self.is_rmb_dragging:
            try:
                self.rmb_shape.body.body_type = pymunk.Body.DYNAMIC
                self.is_rmb_dragging = False
                self.rmb_shape = None
            except Exception as e:
                print(f"Error in RMB handle_mouse_up: {e}")
                self.rmb_shape = None
                self.is_rmb_dragging = False

    def update(self):
        """Обновление состояния рогатки."""
        if self.is_dragging and self.shape:
            mouse_pos = pygame.mouse.get_pos()
            max_distance = 100
            dx = mouse_pos[0] - self.pressed_pos[0]
            dy = mouse_pos[1] - self.pressed_pos[1]
            distance = math.hypot(dx, dy)
            if distance > max_distance:
                dx = dx * max_distance / distance
                dy = dy * max_distance / distance
            try:
                self.shape.body.position = (self.pressed_pos[0] + dx, self.pressed_pos[1] + dy)
            except Exception as e:
                print(f"Error in LMB update: {e}")
                self.shape = None
                self.is_dragging = False
        if self.is_rmb_dragging and self.rmb_shape:
            mouse_pos = pygame.mouse.get_pos()
            try:
                self.rmb_shape.body.position = mouse_pos
            except Exception as e:
                print(f"Error in RMB update: {e}")
                self.rmb_shape = None
                self.is_rmb_dragging = False

    def draw(self, screen):
        """Отрисовка рогатки на экране."""
        if self.is_dragging and self.pressed_pos and self.shape:
            mouse_pos = pygame.mouse.get_pos()
            pygame.draw.line(screen, (0, 0, 0), self.pressed_pos, mouse_pos, 2)

    def reset(self):
        """Сброс состояния рогатки."""
        if self.shape:
            try:
                self.physics.space.remove(self.shape.body, self.shape)
            except Exception as e:
                print(f"Error in reset (LMB shape): {e}")
            self.shape = None
        if self.rmb_shape:
            try:
                self.physics.space.remove(self.rmb_shape.body, self.rmb_shape)
            except Exception as e:
                print(f"Error in reset (RMB shape): {e}")
            self.rmb_shape = None
        self.pressed_pos = None
        self.is_dragging = False
        self.is_rmb_dragging = False