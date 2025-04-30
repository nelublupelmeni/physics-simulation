import pygame
import threading
import os
import pymunk
from slingshot import Slingshot
from cannon import Cannon
from graphics import Graphics
from ui import SimulationUI
from physics_world import PhysicsWorld
import config

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