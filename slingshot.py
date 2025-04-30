import math
import pygame
import pymunk
import config

class Slingshot:
    def __init__(self, physics):
        self.physics = physics
        self.ball = None
        self.pressed_pos = None
        self.is_dragging = False

    def handle_mouse_down(self, event):
        if event.button == 1:
            if not self.ball:
                self.pressed_pos = pygame.mouse.get_pos()
                self.ball = self.physics.add_ball(
                    radius=config.radius,
                    mass=config.mass,
                    pos=self.pressed_pos,
                    elasticity=config.elasticity,
                    friction=config.friction,
                )
                self.ball.body.body_type = pymunk.Body.STATIC
                self.is_dragging = True

    def handle_mouse_up(self, event):
        if event.button == 1 and self.ball and self.is_dragging:
            mouse_pos = pygame.mouse.get_pos()
            angle = math.atan2(self.pressed_pos[1] - mouse_pos[1], self.pressed_pos[0] - mouse_pos[0])
            force = math.hypot(self.pressed_pos[0] - mouse_pos[0], self.pressed_pos[1] - mouse_pos[1]) * 50
            fx = math.cos(angle) * force
            fy = math.sin(angle) * force
            self.ball.body.body_type = pymunk.Body.DYNAMIC
            self.ball.body.apply_impulse_at_local_point((fx, fy), (0, 0))
            self.is_dragging = False
            self.ball = None
            self.pressed_pos = None

    def update(self):
        if self.is_dragging and self.ball:
            mouse_pos = pygame.mouse.get_pos()
            max_distance = 200
            dx = mouse_pos[0] - self.pressed_pos[0]
            dy = mouse_pos[1] - self.pressed_pos[1]
            distance = math.hypot(dx, dy)
            if distance > max_distance:
                dx = dx * max_distance / distance
                dy = dy * max_distance / distance
            self.ball.body.position = (self.pressed_pos[0] + dx, self.pressed_pos[1] + dy)

    def draw(self, screen):
        if self.is_dragging and self.pressed_pos and self.ball:
            mouse_pos = pygame.mouse.get_pos()
            pygame.draw.line(screen, (0, 0, 0), self.pressed_pos, mouse_pos, 2)

    def reset(self):
        if self.ball:
            self.physics.space.remove(self.ball.body, self.ball)
            self.ball = None
        self.pressed_pos = None
        self.is_dragging = False