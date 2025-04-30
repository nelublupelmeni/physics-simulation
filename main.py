import pygame
import threading
import os
import pymunk
from slingshot import Slingshot
from cannon import Cannon
from graphics import Graphics
from ui import SimulationUI
import config

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

    def update(self, dt):
        self.space.step(dt)
        for body in self.space.bodies:
            for shape in body.shapes:
                if isinstance(shape, pymunk.Circle):
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
                        "type": "ball",
                        "position": body.position,
                        "radius": shape.radius
                    })
        return objects

def run_simulation(graphics, physics, running_event):
    clock = pygame.time.Clock()
    fps = 60
    dt = 1 / fps

    while running_event.is_set():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running_event.clear()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if config.mode == "slingshot":
                    physics.slingshot.handle_mouse_down(event)
                elif config.mode == "cannon":
                    physics.cannon.handle_mouse_down(event)
            elif event.type == pygame.MOUSEBUTTONUP:
                if config.mode == "slingshot":
                    physics.slingshot.handle_mouse_up(event)
                elif config.mode == "cannon":
                    physics.cannon.handle_mouse_up(event)

        physics.update(dt)
        if config.mode == "cannon":
            physics.cannon.update()

        graphics.clear()
        graphics.draw_objects(physics.space)
        if config.mode == "slingshot":
            physics.slingshot.draw(graphics.screen)
        elif config.mode == "cannon":
            physics.cannon.draw(graphics.screen)

        graphics.update()
        clock.tick(fps)

    pygame.quit()

def main():
    pygame.init()
    width, height = 1200, 800
    screen_width = pygame.display.Info().current_w
    screen_height = pygame.display.Info().current_h
    total_width = width + 300
    x_position = (screen_width - total_width) // 2
    y_position = (screen_height - height) // 2
    os.environ['SDL_VIDEO_WINDOW_POS'] = f"{x_position},{y_position}"

    graphics = Graphics(width, height, "Гравитационная симуляция", (255, 255, 255))
    physics = PhysicsWorld(width, height)

    running_event = threading.Event()
    running_event.set()
    sim_thread = threading.Thread(target=run_simulation, args=(graphics, physics, running_event), daemon=True)
    sim_thread.start()

    ui = SimulationUI(physics, running_event)
    ui.run()

if __name__ == "__main__":
    main()