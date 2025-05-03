import math
import pygame
import pymunk
import config

class Slingshot:
    def __init__(self, physics):
        self.physics = physics
        self.shape = None  # Can be either a circle or square
        self.pressed_pos = None
        self.is_dragging = False

    def handle_mouse_down(self, event):
        if event.button == 1:
            if not self.shape:
                self.pressed_pos = pygame.mouse.get_pos()
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

    def handle_mouse_up(self, event):
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
                print(f"Error in handle_mouse_up: {e}")
                self.shape = None
                self.is_dragging = False
                self.pressed_pos = None

    def update(self):
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
                print(f"Error in update: {e}")
                self.shape = None
                self.is_dragging = False

    def draw(self, screen):
        if self.is_dragging and self.pressed_pos and self.shape:
            mouse_pos = pygame.mouse.get_pos()
            pygame.draw.line(screen, (0, 0, 0), self.pressed_pos, mouse_pos, 2)

    def reset(self):
        if self.shape:
            try:
                self.physics.space.remove(self.shape.body, self.shape)
            except Exception as e:
                print(f"Error in reset: {e}")
            self.shape = None
        self.pressed_pos = None
        self.is_dragging = False