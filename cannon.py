import pygame
import math
import pymunk
import config

class Cannon:
    def __init__(self, physics):
        self.physics = physics
        self.x = 50  # Moved left from 100 to 50
        self.y = physics.height - 75  # Moved up from height-25 to height-75
        self.trajectory_points = []
        self.ball = None
        self.fired = False
        self.start_time = 0
        self.end_time = 0
        self.font = None
        self.scale_font = None
        self._setup_collision_handler()

    def _setup_collision_handler(self):
        handler = self.physics.space.add_collision_handler(0, 0)
        handler.data["cannon"] = self
        handler.post_solve = self._collision_callback

    def _collision_callback(self, arbiter, space, data):
        cannon = data["cannon"]
        if cannon.fired and cannon.ball in arbiter.shapes:
            for shape in arbiter.shapes:
                if isinstance(shape, pymunk.Poly) and shape.body.body_type == pymunk.Body.STATIC:
                    if abs(shape.body.position.y - (self.physics.height - 5)) < 10:
                        cannon.fired = False
                        if cannon.end_time == 0:
                            cannon.end_time = pygame.time.get_ticks()

    def handle_mouse_down(self, event):
        if event.button == 1:
            if self.ball:
                try:
                    self.physics.space.remove(self.ball.body, self.ball)
                except Exception as e:
                    print(f"Error removing ball: {e}")
                self.ball = None
            self.trajectory_points = []
            self.ball = self.create_ball()

    def create_ball(self):
        try:
            ball = self.physics.add_shape(
                shape_type="circle",
                radius=config.radius,
                mass=config.mass,
                pos=(self.x + 30, self.y - 20),
                elasticity=config.elasticity,
                friction=config.friction
            )
            ball.body.body_type = pymunk.Body.KINEMATIC
            return ball
        except Exception as e:
            print(f"Error creating ball: {e}")
            return None

    def handle_mouse_up(self, event):
        if event.button == 1 and self.ball:
            try:
                self.ball.body.body_type = pymunk.Body.DYNAMIC
                angle_rad = math.radians(config.angle)
                velocity_x = config.initial_velocity * math.cos(angle_rad)
                velocity_y = -config.initial_velocity * math.sin(angle_rad)
                self.ball.body.velocity = (velocity_x, velocity_y)
                self.fired = True
                self.start_time = pygame.time.get_ticks()
                self.end_time = 0
            except Exception as e:
                print(f"Error in handle_mouse_up: {e}")

    def update(self):
        if self.fired and self.ball and self.ball.body:
            try:
                x, y = self.ball.body.position
                # Check for valid position
                if not (isinstance(x, (int, float)) and isinstance(y, (int, float)) and math.isfinite(x) and math.isfinite(y)):
                    self.fired = False
                    self.ball = None
                    return
                self.trajectory_points.append((x, y))
                # Apply air resistance force (quadratic model)
                velocity = self.ball.body.velocity
                speed = math.sqrt(velocity[0]**2 + velocity[1]**2)
                if speed > 0:
                    rho = 1.225  # Air density (kg/m^3)
                    C_d = 0.47   # Drag coefficient for a sphere
                    radius_m = config.radius / 100  # Convert radius to meters
                    A = math.pi * radius_m**2  # Cross-sectional area (m^2)
                    k = 0.5 * rho * C_d * A * config.air_resistance
                    drag_force = (-k * speed * velocity[0], -k * speed * velocity[1])
                    # Limit drag force to prevent instability
                    max_force = 10000
                    drag_magnitude = math.sqrt(drag_force[0]**2 + drag_force[1]**2)
                    if drag_magnitude > max_force:
                        scale = max_force / drag_magnitude
                        drag_force = (drag_force[0] * scale, drag_force[1] * scale)
                    self.ball.body.apply_force_at_local_point(drag_force, (0, 0))
            except Exception as e:
                print(f"Error in update: {e}")
                self.fired = False
                self.ball = None

    def draw(self, screen):
        if self.font is None:
            self.font = pygame.font.SysFont('Arial', 30)
        if self.scale_font is None:
            self.scale_font = pygame.font.SysFont('Arial', 20)

        METERS_TO_PIXELS = 100
        grid_step = METERS_TO_PIXELS
        origin_x = self.x
        origin_y = self.y

        # Determine color based on theme (using RGBA for compatibility)
        axis_color = (255, 255, 255, 255) if config.theme == "dark" else (0, 0, 0, 255)
        text_color = (255, 255, 255, 255) if config.theme == "dark" else (0, 0, 0, 255)

        # Draw axes
        pygame.draw.line(screen, axis_color, (origin_x, origin_y), (self.physics.width, origin_y), 2)
        pygame.draw.line(screen, axis_color, (origin_x, origin_y), (origin_x, 0), 2)

        # Draw grid labels
        for x in range(0, self.physics.width - origin_x, grid_step):
            meters_x = x // METERS_TO_PIXELS
            label = self.scale_font.render(f"{meters_x} м", True, text_color)
            screen.blit(label, (origin_x + x, origin_y + 5))

        for y in range(0, origin_y, grid_step):
            meters_y = y // METERS_TO_PIXELS
            label = self.scale_font.render(f"{meters_y} м", True, text_color)
            screen.blit(label, (origin_x - 40, origin_y - y - 10))

        # Draw cannon
        pygame.draw.rect(screen, (100, 100, 100), (self.x, self.y - 20, 60, 20))
        end_x = self.x + 30 + 60 * math.cos(math.radians(config.angle))
        end_y = self.y - 20 - 60 * math.sin(math.radians(config.angle))
        pygame.draw.line(screen, (150, 150, 150), (self.x + 30, self.y - 20), (end_x, end_y), 3)

        # Draw trajectory points
        for point in self.trajectory_points:
            try:
                if (isinstance(point, tuple) and len(point) == 2 and
                    isinstance(point[0], (int, float)) and isinstance(point[1], (int, float)) and
                    math.isfinite(point[0]) and math.isfinite(point[1])):
                    pygame.draw.circle(screen, (200, 50, 50), (int(point[0]), int(point[1])), 2)
            except Exception as e:
                print(f"Error drawing trajectory point {point}: {e}")

        # Draw timer
        if self.fired or self.end_time > 0:
            current_time = pygame.time.get_ticks()
            elapsed_time = (self.end_time if self.end_time > 0 else current_time) - self.start_time
            elapsed_time /= 1000
            timer_text = self.font.render(f"Время: {elapsed_time:.2f} сек", True, text_color)
            screen.blit(timer_text, (screen.get_width() - 220, 10))

    def reset(self):
        if self.ball:
            try:
                self.physics.space.remove(self.ball.body, self.ball)
            except Exception as e:
                print(f"Error in reset: {e}")
            self.ball = None
        self.trajectory_points = []
        self.fired = False
        self.start_time = 0
        self.end_time = 0