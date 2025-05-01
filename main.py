import pygame
import threading
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

def main():
    pygame.init()
    width, height = 1200, 800
    graphics = Graphics(width, height, "Гравитационная симуляция", (255, 255, 255))
    physics = PhysicsWorld(width, height)

    running_event = threading.Event()
    running_event.set()
    sim_thread = threading.Thread(target=run_simulation, args=(graphics, physics, running_event), daemon=True)
    sim_thread.start()

    ui = SimulationUI(physics, running_event, sim_thread)
    ui.run()

    running_event.clear()
    sim_thread.join(timeout=1.0)
    pygame.quit()

if __name__ == "__main__":
    main()