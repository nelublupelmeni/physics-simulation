import pygame
import pymunk
import pymunk.pygame_util
import config
import os
import math

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
            # Store dynamic shapes and remove them from space to prevent debug_draw rendering
            dynamic_shapes = []
            for body in space.bodies:
                if body.body_type == pymunk.Body.DYNAMIC:
                    for shape in body.shapes:
                        if isinstance(shape, pymunk.Shape):
                            dynamic_shapes.append((shape, shape.color))
                            space.remove(shape)
            
            # Draw static shapes (boundaries, etc.)
            space.debug_draw(self.draw_options)
            
            # Re-add dynamic shapes and draw with color effect
            for shape, original_color in dynamic_shapes:
                space.add(shape)
                shape.color = original_color
                color = pygame.Color(0)
                color.hsva = (shape.hue, 90, 100, 100)  # Hue-based color for full shape
                
                if isinstance(shape, pymunk.Circle):
                    # Draw circle with solid hue-based color fill
                    pygame.draw.circle(self.screen, color, 
                                     (int(shape.body.position.x), int(shape.body.position.y)), 
                                     int(shape.radius))
                elif isinstance(shape, pymunk.Poly):
                    # Draw polygon with solid hue-based color fill, accounting for rotation
                    vertices = shape.get_vertices()
                    body = shape.body
                    cos_angle = math.cos(body.angle)
                    sin_angle = math.sin(body.angle)
                    # Transform vertices: rotate by body.angle, then translate by body.position
                    transformed_vertices = []
                    for v in vertices:
                        # Rotate vertex around shape center
                        x = v.x * cos_angle - v.y * sin_angle
                        y = v.x * sin_angle + v.y * cos_angle
                        # Translate by body position
                        x += body.position.x
                        y += body.position.y
                        transformed_vertices.append((x, y))
                    pygame.draw.polygon(self.screen, color, transformed_vertices)
                # Add drawing logic for future shape types here (e.g., pymunk.Segment)
        else:
            # Draw all shapes using default draw_options
            space.debug_draw(self.draw_options)

    def update(self):
        pygame.display.flip()