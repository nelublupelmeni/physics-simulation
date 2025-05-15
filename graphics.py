import pygame
import pymunk
import pymunk.pygame_util
import config
import os
import math


class Graphics:
    """Класс для управления графикой симуляции."""

    def __init__(self, width, height, title, bg_color):
        """Инициализация графического окна."""
        self.width = width
        self.height = height
        self.bg_color = bg_color
        screen_width = pygame.display.Info().current_w
        screen_height = pygame.display.Info().current_h
        total_width = width + 300
        x_position = (screen_width - total_width) // 2
        y_position = (screen_height - height) // 2
        os.environ['SDL_VIDEO_WINDOW_POS'] = f"{x_position},{y_position}"
        self.screen = pygame.display.set_mode((width, height), pygame.NOFRAME)
        pygame.display.set_caption(title)
        self.draw_options = pymunk.pygame_util.DrawOptions(self.screen)
        pymunk.pygame_util.positive_y_is_up = False

    def clear(self):
        """Очистка экрана."""
        bg_hex = config.ui_colors[config.theme]["bg"]
        bg_rgb = tuple(int(bg_hex[i:i+2], 16) for i in (1, 3, 5))
        self.screen.fill(bg_rgb)

    def draw_objects(self, space):
        """Отрисовка объектов в пространстве."""
        if config.color_effect:
            dynamic_shapes = []
            static_shapes = []
            default_color = (128, 128, 128, 255)  
            for body in space.bodies:
                for shape in body.shapes:
                    if isinstance(shape, pymunk.Shape):
                        shape_color = getattr(shape, 'color', default_color)
                        if body.body_type == pymunk.Body.DYNAMIC:
                            dynamic_shapes.append((shape, shape_color))
                            space.remove(shape)
                        else:
                            static_shapes.append((shape, shape_color))
                            space.remove(shape)

            space.debug_draw(self.draw_options)

            for shape, original_color in dynamic_shapes:
                space.add(shape)
                shape.color = original_color
                color = pygame.Color(0)
                color.hsva = (shape.hue, 90, 100, 100)

                if isinstance(shape, pymunk.Circle):
                    pygame.draw.circle(self.screen, color,
                                       (int(shape.body.position.x), int(shape.body.position.y)),
                                       int(shape.radius))
                elif isinstance(shape, pymunk.Poly):
                    vertices = shape.get_vertices()
                    body = shape.body
                    cos_angle = math.cos(body.angle)
                    sin_angle = math.sin(body.angle)
                    transformed_vertices = []
                    for v in vertices:
                        x = v.x * cos_angle - v.y * sin_angle
                        y = v.x * sin_angle + v.y * cos_angle
                        x += body.position.x
                        y += body.position.y
                        transformed_vertices.append((x, y))
                    pygame.draw.polygon(self.screen, color, transformed_vertices)

            for shape, original_color in static_shapes:
                space.add(shape)
                shape.color = original_color
                if isinstance(shape, pymunk.Circle):
                    pygame.draw.circle(self.screen, original_color,
                                       (int(shape.body.position.x), int(shape.body.position.y)),
                                       int(shape.radius))
                elif isinstance(shape, pymunk.Poly):
                    vertices = shape.get_vertices()
                    body = shape.body
                    cos_angle = math.cos(body.angle)
                    sin_angle = math.sin(body.angle)
                    transformed_vertices = []
                    for v in vertices:
                        x = v.x * cos_angle - v.y * sin_angle
                        y = v.x * sin_angle + v.y * cos_angle
                        x += body.position.x
                        y += body.position.y
                        transformed_vertices.append((x, y))
                    pygame.draw.polygon(self.screen, original_color, transformed_vertices)
        else:
            space.debug_draw(self.draw_options)

    def update(self):
        """Обновление экрана."""
        pygame.display.flip()