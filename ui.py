import customtkinter as ctk
import config

class SimulationUI:
    def __init__(self, physics, running_event, sim_thread):
        self.physics = physics
        self.running_event = running_event
        self.sim_thread = sim_thread
        self.root = ctk.CTk()
        self.root.title("Настройки симуляции")
        self._setup_window_geometry()
        self.root.resizable(False, False)

        # Set initial theme
        ctk.set_appearance_mode(config.theme)
        self.root.configure(fg_color=config.ui_colors[config.theme]["bg"])

        self.mass_var = ctk.DoubleVar(value=config.mass)
        self.radius_var = ctk.DoubleVar(value=config.radius)
        self.elasticity_var = ctk.DoubleVar(value=config.elasticity)
        self.friction_var = ctk.DoubleVar(value=config.friction)
        self.gravity_var = ctk.DoubleVar(value=config.gravity)
        self.velocity_var = ctk.DoubleVar(value=config.initial_velocity / 100)
        self.angle_var = ctk.DoubleVar(value=config.angle)
        self.air_resistance_var = ctk.DoubleVar(value=config.air_resistance)

        self._create_widgets()
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _setup_window_geometry(self):
        window_width = 500
        window_height = 600
        pygame_width = 1200
        pygame_height = 800
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        total_width = pygame_width + 300
        pygame_x = (screen_width - total_width) // 2
        pygame_y = (screen_height - pygame_height) // 2
        x_position = pygame_x + pygame_width
        y_position = pygame_y
        self.root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

    def _lighten_color(self, hex_color, factor=0.3):
        """Lighten a hex color by a given factor (0 to 1)."""
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        rgb_light = tuple(min(255, int(c + (255 - c) * factor)) for c in rgb)
        return f"#{rgb_light[0]:02x}{rgb_light[1]:02x}{rgb_light[2]:02x}"

    def _update_mode_buttons(self):
        """Update the appearance of mode buttons based on the current mode."""
        default_fg_color = ctk.ThemeManager.theme["CTkButton"]["fg_color"]
        light_fg_color = self._lighten_color(default_fg_color[0], 0.3)
        
        self.slingshot_button.configure(fg_color=default_fg_color if config.mode == "slingshot" else light_fg_color)
        self.cannon_button.configure(fg_color=default_fg_color if config.mode == "cannon" else light_fg_color)

    def _update_shape_buttons(self):
        """Update the appearance of shape buttons based on the current shape type."""
        default_fg_color = ctk.ThemeManager.theme["CTkButton"]["fg_color"]
        light_fg_color = self._lighten_color(default_fg_color[0], 0.3)
        
        self.circle_button.configure(fg_color=default_fg_color if config.shape_type == "circle" else light_fg_color)
        self.square_button.configure(fg_color=default_fg_color if config.shape_type == "square" else light_fg_color)
        self.triangle_button.configure(fg_color=default_fg_color if config.shape_type == "triangle" else light_fg_color)

    def _create_widgets(self):
        # Mass row
        mass_frame = ctk.CTkFrame(self.root, fg_color=config.ui_colors[config.theme]["bg"])
        mass_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(mass_frame, text="Масса:", width=150, anchor="w", 
                     text_color=config.ui_colors[config.theme]["fg"]).pack(side="left", padx=5)
        self.mass_slider = ctk.CTkSlider(mass_frame, from_=1, to=100, variable=self.mass_var, 
                                        command=self.update_mass, width=200)
        self.mass_slider.pack(side="left", padx=5)
        self.mass_entry = ctk.CTkEntry(mass_frame, width=80, 
                                      text_color=config.ui_colors[config.theme]["fg"])
        self.mass_entry.insert(0, str(self.mass_var.get()))
        self.mass_entry.pack(side="left", padx=5)
        self.mass_entry.bind("<Return>", lambda e: self.mass_var.set(round(float(self.mass_entry.get()), 2)))

        # Radius row
        radius_frame = ctk.CTkFrame(self.root, fg_color=config.ui_colors[config.theme]["bg"])
        radius_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(radius_frame, text="Радиус:", width=150, anchor="w", 
                     text_color=config.ui_colors[config.theme]["fg"]).pack(side="left", padx=5)
        self.radius_slider = ctk.CTkSlider(radius_frame, from_=10, to=100, variable=self.radius_var, 
                                          command=self.update_radius, width=200)
        self.radius_slider.pack(side="left", padx=5)
        self.radius_entry = ctk.CTkEntry(radius_frame, width=80, 
                                        text_color=config.ui_colors[config.theme]["fg"])
        self.radius_entry.insert(0, str(self.radius_var.get()))
        self.radius_entry.pack(side="left", padx=5)
        self.radius_entry.bind("<Return>", lambda e: self.radius_var.set(round(float(self.radius_entry.get()), 2)))

        # Elasticity row
        elasticity_frame = ctk.CTkFrame(self.root, fg_color=config.ui_colors[config.theme]["bg"])
        elasticity_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(elasticity_frame, text="Упругость:", width=150, anchor="w", 
                     text_color=config.ui_colors[config.theme]["fg"]).pack(side="left", padx=5)
        self.elasticity_slider = ctk.CTkSlider(elasticity_frame, from_=0, to=1, variable=self.elasticity_var, 
                                              command=self.update_elasticity, width=200)
        self.elasticity_slider.pack(side="left", padx=5)
        self.elasticity_entry = ctk.CTkEntry(elasticity_frame, width=80, 
                                            text_color=config.ui_colors[config.theme]["fg"])
        self.elasticity_entry.insert(0, str(self.elasticity_var.get()))
        self.elasticity_entry.pack(side="left", padx=5)
        self.elasticity_entry.bind("<Return>", lambda e: self.elasticity_var.set(round(float(self.elasticity_entry.get()), 2)))

        # Friction row
        friction_frame = ctk.CTkFrame(self.root, fg_color=config.ui_colors[config.theme]["bg"])
        friction_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(friction_frame, text="Трение:", width=150, anchor="w", 
                     text_color=config.ui_colors[config.theme]["fg"]).pack(side="left", padx=5)
        self.friction_slider = ctk.CTkSlider(friction_frame, from_=0, to=1, variable=self.friction_var, 
                                            command=self.update_friction, width=200)
        self.friction_slider.pack(side="left", padx=5)
        self.friction_entry = ctk.CTkEntry(friction_frame, width=80, 
                                          text_color=config.ui_colors[config.theme]["fg"])
        self.friction_entry.insert(0, str(self.friction_var.get()))
        self.friction_entry.pack(side="left", padx=5)
        self.friction_entry.bind("<Return>", lambda e: self.friction_var.set(round(float(self.friction_entry.get()), 2)))

        # Gravity row
        gravity_frame = ctk.CTkFrame(self.root, fg_color=config.ui_colors[config.theme]["bg"])
        gravity_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(gravity_frame, text="Гравитация:", width=150, anchor="w", 
                     text_color=config.ui_colors[config.theme]["fg"]).pack(side="left", padx=5)
        self.gravity_slider = ctk.CTkSlider(gravity_frame, from_=0, to=2000, variable=self.gravity_var, 
                                           command=self.update_gravity, width=200)
        self.gravity_slider.pack(side="left", padx=5)
        self.gravity_entry = ctk.CTkEntry(gravity_frame, width=80, 
                                         text_color=config.ui_colors[config.theme]["fg"])
        self.gravity_entry.insert(0, str(self.gravity_var.get()))
        self.gravity_entry.pack(side="left", padx=5)
        self.gravity_entry.bind("<Return>", lambda e: self.gravity_var.set(round(float(self.gravity_entry.get()), 2)))

        # Velocity row
        velocity_frame = ctk.CTkFrame(self.root, fg_color=config.ui_colors[config.theme]["bg"])
        velocity_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(velocity_frame, text="Скорость (м/с):", width=150, anchor="w", 
                     text_color=config.ui_colors[config.theme]["fg"]).pack(side="left", padx=5)
        self.velocity_slider = ctk.CTkSlider(velocity_frame, from_=0, to=15, variable=self.velocity_var, 
                                            command=self.update_velocity, width=200)
        self.velocity_slider.pack(side="left", padx=5)
        self.velocity_entry = ctk.CTkEntry(velocity_frame, width=80, 
                                          text_color=config.ui_colors[config.theme]["fg"])
        self.velocity_entry.insert(0, str(self.velocity_var.get()))
        self.velocity_entry.pack(side="left", padx=5)
        self.velocity_entry.bind("<Return>", lambda e: self.velocity_var.set(round(float(self.velocity_entry.get()), 2)))

        # Angle row
        angle_frame = ctk.CTkFrame(self.root, fg_color=config.ui_colors[config.theme]["bg"])
        angle_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(angle_frame, text="Угол наклона:", width=150, anchor="w", 
                     text_color=config.ui_colors[config.theme]["fg"]).pack(side="left", padx=5)
        self.angle_slider = ctk.CTkSlider(angle_frame, from_=0, to=90, variable=self.angle_var, 
                                         command=self.update_angle, width=200)
        self.angle_slider.pack(side="left", padx=5)
        self.angle_entry = ctk.CTkEntry(angle_frame, width=80, 
                                       text_color=config.ui_colors[config.theme]["fg"])
        self.angle_entry.insert(0, str(self.angle_var.get()))
        self.angle_entry.pack(side="left", padx=5)
        self.angle_entry.bind("<Return>", lambda e: self.angle_var.set(round(float(self.angle_entry.get()), 2)))

        # Air resistance row
        air_resistance_frame = ctk.CTkFrame(self.root, fg_color=config.ui_colors[config.theme]["bg"])
        air_resistance_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(air_resistance_frame, text="Сопротивление воздуха:", width=150, anchor="w", 
                     text_color=config.ui_colors[config.theme]["fg"]).pack(side="left", padx=5)
        self.air_resistance_slider = ctk.CTkSlider(air_resistance_frame, from_=0, to=50, 
                                                  variable=self.air_resistance_var, command=self.update_air_resistance, width=200)
        self.air_resistance_slider.pack(side="left", padx=5)
        self.air_resistance_entry = ctk.CTkEntry(air_resistance_frame, width=80, 
                                                text_color=config.ui_colors[config.theme]["fg"])
        self.air_resistance_entry.insert(0, str(self.air_resistance_var.get()))
        self.air_resistance_entry.pack(side="left", padx=5)
        self.air_resistance_entry.bind("<Return>", lambda e: self.air_resistance_var.set(round(float(self.air_resistance_entry.get()), 2)))

        # Mode buttons frame
        mode_button_frame = ctk.CTkFrame(self.root, fg_color=config.ui_colors[config.theme]["bg"])
        mode_button_frame.pack(pady=10, padx=(20, 0))  # Shift right with padx
        self.slingshot_button = ctk.CTkButton(mode_button_frame, text="Рогатка", 
                                             command=self.set_slingshot_mode, width=100)
        self.slingshot_button.pack(side="left", padx=(0, 5))
        self.cannon_button = ctk.CTkButton(mode_button_frame, text="Пушка", 
                                          command=self.set_cannon_mode, width=100)
        self.cannon_button.pack(side="left", padx=5)

        # Shape selection buttons frame (below mode buttons)
        shape_button_frame = ctk.CTkFrame(self.root, fg_color=config.ui_colors[config.theme]["bg"])
        shape_button_frame.pack(pady=10, padx=(20, 0))
        self.circle_button = ctk.CTkButton(shape_button_frame, text="Круг", 
                                          command=self.set_circle_shape, width=100)
        self.circle_button.pack(side="left", padx=(0, 5))
        self.square_button = ctk.CTkButton(shape_button_frame, text="Квадрат", 
                                          command=self.set_square_shape, width=100)
        self.square_button.pack(side="left", padx=(0, 5))
        self.triangle_button = ctk.CTkButton(shape_button_frame, text="Треугольник", 
                                            command=self.set_triangle_shape, width=100)
        self.triangle_button.pack(side="left", padx=5)

        # Clear button (below shape buttons)
        self.clear_button = ctk.CTkButton(self.root, text="Очистить поле", 
                                         command=self.clear_objects, width=150)
        self.clear_button.pack(pady=10, padx=10)

        # Color effect switch (below clear button)
        self.color_effect_switch = ctk.CTkSwitch(self.root, text="Эффект: Выкл", 
                                                command=self.toggle_color_effect, width=150)
        self.color_effect_switch.pack(pady=10, padx=10)

        # Theme switch (below color effect switch)
        self.theme_switch = ctk.CTkSwitch(self.root, text="Тема: Светлая" if config.theme == "light" else "Тема: Тёмная", 
                                         command=self.toggle_theme, width=150)
        self.theme_switch.pack(pady=10, padx=10)

        # Initialize button states
        self._update_mode_buttons()
        self._update_shape_buttons()

    def toggle_theme(self):
        # Toggle theme
        config.theme = "dark" if config.theme == "light" else "light"
        ctk.set_appearance_mode(config.theme)
        self.root.configure(fg_color=config.ui_colors[config.theme]["bg"])

        # Update widget colors
        for frame in [self.root.winfo_children()[i] for i in range(0, 8)]:  # Slider frames
            frame.configure(fg_color=config.ui_colors[config.theme]["bg"])
            label, _, entry = frame.winfo_children()
            label.configure(text_color=config.ui_colors[config.theme]["fg"])
            entry.configure(text_color=config.ui_colors[config.theme]["fg"])
        
        self.mode_button_frame = self.root.winfo_children()[8]  # Mode button frame
        self.mode_button_frame.configure(fg_color=config.ui_colors[config.theme]["bg"])
        self.shape_button_frame = self.root.winfo_children()[9]  # Shape button frame
        self.shape_button_frame.configure(fg_color=config.ui_colors[config.theme]["bg"])

        self.theme_switch.configure(text="Тема: Светлая" if config.theme == "light" else "Тема: Тёмная")
        
        # Update button states after theme change
        self._update_mode_buttons()
        self._update_shape_buttons()

    def update_gravity(self, value):
        gravity = round(float(value), 2)
        self.physics.set_gravity(gravity)
        self.gravity_entry.delete(0, ctk.END)
        self.gravity_entry.insert(0, str(gravity))

    def update_mass(self, value):
        config.mass = round(float(value), 2)
        self.mass_entry.delete(0, ctk.END)
        self.mass_entry.insert(0, str(config.mass))

    def update_radius(self, value):
        config.radius = round(float(value), 2)
        self.radius_entry.delete(0, ctk.END)
        self.radius_entry.insert(0, str(config.radius))

    def update_elasticity(self, value):
        config.elasticity = round(float(value), 2)
        self.elasticity_entry.delete(0, ctk.END)
        self.elasticity_entry.insert(0, str(config.elasticity))

    def update_friction(self, value):
        config.friction = round(float(value), 2)
        self.friction_entry.delete(0, ctk.END)
        self.friction_entry.insert(0, str(config.friction))

    def update_velocity(self, value):
        velocity_mps = round(float(value), 2)
        config.initial_velocity = velocity_mps * 100
        self.velocity_entry.delete(0, ctk.END)
        self.velocity_entry.insert(0, str(velocity_mps))

    def update_angle(self, value):
        config.angle = round(float(value), 2)
        self.angle_entry.delete(0, ctk.END)
        self.angle_entry.insert(0, str(config.angle))

    def update_air_resistance(self, value):
        config.air_resistance = round(float(value), 2)
        self.air_resistance_entry.delete(0, ctk.END)
        self.air_resistance_entry.insert(0, str(config.air_resistance))

    def clear_objects(self):
        self.physics.clear_objects()

    def set_slingshot_mode(self):
        config.mode = "slingshot"
        self.physics.slingshot.reset()
        self.physics.cannon.reset()
        self.clear_objects()
        self._update_mode_buttons()

    def set_cannon_mode(self):
        config.mode = "cannon"
        self.physics.slingshot.reset()
        self.physics.cannon.reset()
        self.clear_objects()
        self._update_mode_buttons()

    def set_circle_shape(self):
        config.shape_type = "circle"
        self.physics.slingshot.reset()
        self._update_shape_buttons()

    def set_square_shape(self):
        config.shape_type = "square"
        self.physics.slingshot.reset()
        self._update_shape_buttons()

    def set_triangle_shape(self):
        config.shape_type = "triangle"
        self.physics.slingshot.reset()
        self._update_shape_buttons()

    def toggle_color_effect(self):
        config.color_effect = not config.color_effect
        self.color_effect_switch.configure(text="Эффект: " + ("Вкл" if config.color_effect else "Выкл"))

    def _on_closing(self):
        self.running_event.clear()
        self.sim_thread.join(timeout=1.0)
        self.root.quit()
        self.root.destroy()

    def run(self):
        self.root.mainloop()