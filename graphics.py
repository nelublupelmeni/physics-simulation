import pygame
import pymunk
import pymunk.pygame_util
import config
import os

class Graphics:
    def __init__(self, width, height, title, bg_color):
        self.width = width
        self.height = height
        self.bg_color = bg_color
        # Set window position
        screen_width = pygame.display.Info().current_w
        screen_height = pygame.display.Info().current_h
        total_width = width + 300
        x_position = (screen_width - total_width) // 2
        y_position = (screen_height - height) // 2
        os.environ['SDL_VIDEO_WINDOW_POS'] = f"{x_position},{y_position}"
        # Initialize display without title bar
        self.screen = pygame.display.set_mode((width, height), pygame.NOFRAME)
        pygame.display.set_caption(title)  # Caption is set but not visible due to NOFRAME
        self.draw_options = pymunk.pygame_util.DrawOptions(self.screen)
        pymunk.pygame_util.positive_y_is_up = False

    def clear(self):
        # Use the background color from config.ui_colors based on the current theme
        bg_hex = config.ui_colors[config.theme]["bg"]
        # Convert hex color to RGB tuple
        bg_rgb = tuple(int(bg_hex[i:i+2], 16) for i in (1, 3, 5))
        self.screen.fill(bg_rgb)

    def draw_objects(self, space):
        if config.color_effect:
            # Store original colors and set to transparent
            shape_colors = []
            for body in space.bodies:
                for shape in body.shapes:
                    if isinstance(shape, (pymunk.Circle, pymunk.Poly)) and body.body_type == pymunk.Body.DYNAMIC:
                        shape_colors.append((shape, shape.color))
                        shape.color = (0, 0, 0, 0)  # Transparent
            # Draw all shapes (boundaries, etc.)
            space.debug_draw(self.draw_options)
            # Restore colors and draw with color effect
            for shape, original_color in shape_colors:
                shape.color = original_color
                color = pygame.Color(0)
                color.hsva = (shape.hue, 90, 100, 100)
                if isinstance(shape, pymunk.Circle):
                    pygame.draw.circle(self.screen, (30, 30, 30), (int(shape.body.position.x), int(shape.body.position.y)), int(shape.radius))
                    pygame.draw.circle(self.screen, color, (int(shape.body.position.x), int(shape.body.position.y)), int(shape.radius) - 2)
                elif isinstance(shape, pymunk.Poly):
                    vertices = [(shape.body.position.x + v.x, shape.body.position.y + v.y) for v in shape.get_vertices()]
                    pygame.draw.polygon(self.screen, (30, 30, 30), vertices)
                    pygame.draw.polygon(self.screen, color, vertices, 2)
        else:
            # Draw all shapes using default draw_options
            space.debug_draw(self.draw_options)

    def update(self):
        pygame.display.flip()