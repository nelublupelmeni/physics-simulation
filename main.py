import pygame
import threading
import os
from falling import PhysicsWorld
from graphics import Graphics
from ui import create_ui, UIData

def main():
    pygame.init()
    width, height = 1200, 800
    screen_width = pygame.display.Info().current_w # Получение размеров экрана
    screen_height = pygame.display.Info().current_h
    total_width = width + 300
    x_position = (screen_width - total_width) // 2
    y_position = (screen_height - height) // 2
    os.environ['SDL_VIDEO_WINDOW_POS'] = f"{x_position},{y_position}"

    graphics = Graphics(width, height, "Гравитационная симуляция", (255, 255, 255))
    physics = PhysicsWorld(width, height)

    # создание и запуск другого потока для UI
    ui_thread = threading.Thread(target=create_ui, args=(physics,), daemon=True)
    ui_thread.start()

    running = True
    clock = pygame.time.Clock()
    fps = 60
    dt = 1 / fps

    # основной цикл событий
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if UIData.mode == "normal" and event.button == 1:
                    x, y = event.pos
                    if x < 1000:
                        physics.add_ball(
                            radius=UIData.radius,
                            mass=UIData.mass,
                            pos=(x, y),
                            elasticity=UIData.elasticity,
                            friction=UIData.friction,
                        )
                elif UIData.mode == "slingshot":
                    physics.slingshot.handle_mouse_down(event)
                elif UIData.mode == "cannon":
                    physics.cannon.handle_mouse_down(event)
            elif event.type == pygame.MOUSEBUTTONUP:
                if UIData.mode == "slingshot":
                    physics.slingshot.handle_mouse_up(event)
                elif UIData.mode == "cannon":
                    physics.cannon.handle_mouse_up(event)

        physics.update(dt)
        if UIData.mode == "cannon":
            physics.cannon.update()

        graphics.clear()
        graphics.draw_objects(physics.space)
        if UIData.mode == "slingshot":
            physics.slingshot.draw(graphics.screen)
        elif UIData.mode == "cannon":
            physics.cannon.draw(graphics.screen)

        graphics.update()
        clock.tick(fps)

    pygame.quit()

if __name__ == "__main__":
    main()