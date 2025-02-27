import pygame
import pymunk
import pymunk.pygame_util
from ui import UIData

#инициализация экрана
class Graphics:
    def __init__(self, width, height, title, bg_color):
        self.width = width
        self.height = height
        self.bg_color = bg_color
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(title)
        self.draw_options = pymunk.pygame_util.DrawOptions(self.screen) # сопоставление координат pymunk и pygame
        pymunk.pygame_util.positive_y_is_up = False

    def clear(self):
        self.screen.fill(self.bg_color)

    def draw_objects(self, space):
        if UIData.color_effect:
            for body in space.bodies:
                for shape in body.shapes:
                    if isinstance(shape, pymunk.Circle):
                        color = pygame.Color(0)
                        color.hsva = (shape.hue, 90, 100, 100) #переливание цветов
                        pygame.draw.circle(self.screen, (30, 30, 30), (int(body.position.x), int(body.position.y)), int(shape.radius))
                        pygame.draw.circle(self.screen, color, (int(body.position.x), int(body.position.y)), int(shape.radius) - 2)
        else:
            space.debug_draw(self.draw_options)

    # обновляет отображение на экране
    def update(self):
        pygame.display.flip()