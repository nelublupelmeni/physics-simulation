import customtkinter as ctk
import config
from visualization import plot_velocity_vs_time, plot_range_vs_angle

class SimulationUI:
    def __init__(self, physics, running_event, sim_thread):
        self.physics = physics
        self.running_event = running_event
        self.sim_thread = sim_thread
        self.root = ctk.CTk()
        self.root.title("Настройки симуляции")
        self._setup_window_geometry()
        self.root.resizable(False, False)

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
        COLOR_MAP = {
            'gray': '#808080',
            'grey': '#808080',
            'black': '#000000',
            'white': '#FFFFFF',
            'blue': '#0000FF',
            'green': '#008000',
            'red': '#FF0000'
        }
        hex_color = COLOR_MAP.get(hex_color.lower(), hex_color)
        if not hex_color.startswith('#') and not all(c in '0123456789ABCDEFabcdef' for c in hex_color):
            hex_color = '#4A4D50' if config.theme == 'dark' else '#2FA572'

        hex_color = hex_color.lstrip('#')
        if len(hex_color) != 6:
            hex_color = '4A4D50' if config.theme == 'dark' else '2FA572'

        try:
            rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            rgb_light = tuple(min(255, int(c + (255 - c) * factor)) for c in rgb)
            return f"#{rgb_light[0]:02x}{rgb_light[1]:02x}{rgb_light[2]:02x}"
        except ValueError:
            return '#6A6D70' if config.theme == 'dark' else '#5FC89F'

    def _update_mode_buttons(self):
        default_fg_color = ctk.ThemeManager.theme["CTkButton"]["fg_color"]
        light_fg_color = self._lighten_color(default_fg_color[0], 0.3)
        self.slingshot_button.configure(fg_color=default_fg_color if config.mode == "slingshot" else light_fg_color)
        self.cannon_button.configure(fg_color=default_fg_color if config.mode == "cannon" else light_fg_color)

    def _update_shape_buttons(self):
        default_fg_color = ctk.ThemeManager.theme["CTkButton"]["fg_color"]
        light_fg_color = self._lighten_color(default_fg_color[0], 0.3)

        if config.mode == "cannon":
            # In cannon mode, circle and button are normal, triangle and square are lighter and disabled
            self.circle_button.configure(
                fg_color=default_fg_color if config.shape_type == "circle" else light_fg_color,
                state="normal"
            )
            self.button_button.configure(
                fg_color=default_fg_color if config.shape_type == "button" else light_fg_color,
                state="normal"
            )
            self.square_button.configure(fg_color=light_fg_color, state="disabled")
            self.triangle_button.configure(fg_color=light_fg_color, state="disabled")
        else:
            # In slingshot mode, all buttons are normal and clickable
            self.circle_button.configure(
                fg_color=default_fg_color if config.shape_type == "circle" else light_fg_color,
                state="normal"
            )
            self.square_button.configure(
                fg_color=default_fg_color if config.shape_type == "square" else light_fg_color,
                state="normal"
            )
            self.triangle_button.configure(
                fg_color=default_fg_color if config.shape_type == "triangle" else light_fg_color,
                state="normal"
            )
            self.button_button.configure(
                fg_color=default_fg_color if config.shape_type == "button" else light_fg_color,
                state="normal"
            )

    def _update_plot_buttons(self):
        default_fg_color = ctk.ThemeManager.theme["CTkButton"]["fg_color"]
        light_fg_color = self._lighten_color(default_fg_color[0], 0.3)

        if config.mode == "slingshot":
            # In slingshot mode, plot buttons are lighter and disabled
            self.velocity_plot_button.configure(fg_color=light_fg_color, state="disabled")
            self.range_plot_button.configure(fg_color=light_fg_color, state="disabled")
        else:
            # In cannon mode, plot buttons are normal and clickable
            self.velocity_plot_button.configure(fg_color=default_fg_color, state="normal")
            self.range_plot_button.configure(fg_color=default_fg_color, state="normal")

    def _update_slider_states(self):
        default_slider_color = ctk.ThemeManager.theme["CTkSlider"]["progress_color"]
        default_fg_color = ctk.ThemeManager.theme["CTkSlider"]["fg_color"]
        default_text_color = config.ui_colors[config.theme]["fg"]
        LIGHT_GRAY = "#D3D3D3"

        if config.mode == "cannon":
            self.elasticity_var.set(self.INITIAL_ELASTICITY)
            self.friction_var.set(self.INITIAL_FRICTION)
            config.elasticity = self.INITIAL_ELASTICITY
            config.friction = self.INITIAL_FRICTION
            self.elasticity_entry.delete(0, ctk.END)
            self.elasticity_entry.insert(0, str(self.INITIAL_ELASTICITY))
            self.friction_entry.delete(0, ctk.END)
            self.friction_entry.insert(0, str(self.INITIAL_FRICTION))
            self.elasticity_slider.configure(state="disabled", progress_color=LIGHT_GRAY, fg_color=LIGHT_GRAY)
            self.friction_slider.configure(state="disabled", progress_color=LIGHT_GRAY, fg_color=LIGHT_GRAY)
            self.elasticity_entry.configure(state="disabled", text_color=LIGHT_GRAY)
            self.friction_entry.configure(state="disabled", text_color=LIGHT_GRAY)
            self.elasticity_label.configure(text_color=LIGHT_GRAY)
            self.friction_label.configure(text_color=LIGHT_GRAY)
        else:
            self.elasticity_slider.configure(
                state="normal",
                progress_color=default_slider_color,
                fg_color=default_fg_color
            )
            self.friction_slider.configure(
                state="normal",
                progress_color=default_slider_color,
                fg_color=default_fg_color
            )
            self.elasticity_entry.configure(state="normal", text_color=default_text_color)
            self.friction_entry.configure(state="normal", text_color=default_text_color)
            self.elasticity_label.configure(text_color=default_text_color)
            self.friction_label.configure(text_color=default_text_color)

    def _safe_set_var(self, var, entry):
        try:
            var.set(round(float(entry.get()), 2))
        except ValueError:
            entry.delete(0, ctk.END)
            entry.insert(0, str(var.get()))

    def _create_widgets(self):
        self.INITIAL_ELASTICITY = config.elasticity
        self.INITIAL_FRICTION = config.friction

        self.mass_frame = ctk.CTkFrame(self.root, fg_color=config.ui_colors[config.theme]["bg"])
        self.mass_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(self.mass_frame, text="Масса:", width=150, anchor="w", 
                     text_color=config.ui_colors[config.theme]["fg"]).pack(side="left", padx=5)
        self.mass_slider = ctk.CTkSlider(self.mass_frame, from_=1, to=100, variable=self.mass_var, 
                                        command=self.update_mass, width=200)
        self.mass_slider.pack(side="left", padx=5)
        self.mass_entry = ctk.CTkEntry(self.mass_frame, width=80, 
                                      text_color=config.ui_colors[config.theme]["fg"])
        self.mass_entry.insert(0, str(self.mass_var.get()))
        self.mass_entry.pack(side="left", padx=5)
        self.mass_entry.bind("<Return>", lambda e: self._safe_set_var(self.mass_var, self.mass_entry))

        self.radius_frame = ctk.CTkFrame(self.root, fg_color=config.ui_colors[config.theme]["bg"])
        self.radius_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(self.radius_frame, text="Радиус:", width=150, anchor="w", 
                     text_color=config.ui_colors[config.theme]["fg"]).pack(side="left", padx=5)
        self.radius_slider = ctk.CTkSlider(self.radius_frame, from_=10, to=100, variable=self.radius_var, 
                                          command=self.update_radius, width=200)
        self.radius_slider.pack(side="left", padx=5)
        self.radius_entry = ctk.CTkEntry(self.radius_frame, width=80, 
                                        text_color=config.ui_colors[config.theme]["fg"])
        self.radius_entry.insert(0, str(self.radius_var.get()))
        self.radius_entry.pack(side="left", padx=5)
        self.radius_entry.bind("<Return>", lambda e: self._safe_set_var(self.radius_var, self.radius_entry))

        self.elasticity_frame = ctk.CTkFrame(self.root, fg_color=config.ui_colors[config.theme]["bg"])
        self.elasticity_frame.pack(fill="x", padx=10, pady=5)
        self.elasticity_label = ctk.CTkLabel(self.elasticity_frame, text="Упругость:", width=150, anchor="w", 
                                            text_color=config.ui_colors[config.theme]["fg"])
        self.elasticity_label.pack(side="left", padx=5)
        self.elasticity_slider = ctk.CTkSlider(self.elasticity_frame, from_=0, to=1, variable=self.elasticity_var, 
                                              command=self.update_elasticity, width=200)
        self.elasticity_slider.pack(side="left", padx=5)
        self.elasticity_entry = ctk.CTkEntry(self.elasticity_frame, width=80, 
                                            text_color=config.ui_colors[config.theme]["fg"])
        self.elasticity_entry.insert(0, str(self.elasticity_var.get()))
        self.elasticity_entry.pack(side="left", padx=5)
        self.elasticity_entry.bind("<Return>", lambda e: self._safe_set_var(self.elasticity_var, self.elasticity_entry))

        self.friction_frame = ctk.CTkFrame(self.root, fg_color=config.ui_colors[config.theme]["bg"])
        self.friction_frame.pack(fill="x", padx=10, pady=5)
        self.friction_label = ctk.CTkLabel(self.friction_frame, text="Трение:", width=150, anchor="w", 
                                          text_color=config.ui_colors[config.theme]["fg"])
        self.friction_label.pack(side="left", padx=5)
        self.friction_slider = ctk.CTkSlider(self.friction_frame, from_=0, to=1, variable=self.friction_var, 
                                            command=self.update_friction, width=200)
        self.friction_slider.pack(side="left", padx=5)
        self.friction_entry = ctk.CTkEntry(self.friction_frame, width=80, 
                                          text_color=config.ui_colors[config.theme]["fg"])
        self.friction_entry.insert(0, str(self.friction_var.get()))
        self.friction_entry.pack(side="left", padx=5)
        self.friction_entry.bind("<Return>", lambda e: self._safe_set_var(self.friction_var, self.friction_entry))

        self.gravity_frame = ctk.CTkFrame(self.root, fg_color=config.ui_colors[config.theme]["bg"])
        self.gravity_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(self.gravity_frame, text="Гравитация:", width=150, anchor="w", 
                     text_color=config.ui_colors[config.theme]["fg"]).pack(side="left", padx=5)
        self.gravity_slider = ctk.CTkSlider(self.gravity_frame, from_=0, to=2000, variable=self.gravity_var, 
                                           command=self.update_gravity, width=200)
        self.gravity_slider.pack(side="left", padx=5)
        self.gravity_entry = ctk.CTkEntry(self.gravity_frame, width=80, 
                                         text_color=config.ui_colors[config.theme]["fg"])
        self.gravity_entry.insert(0, str(self.gravity_var.get()))
        self.gravity_entry.pack(side="left", padx=5)
        self.gravity_entry.bind("<Return>", lambda e: self._safe_set_var(self.gravity_var, self.gravity_entry))

        self.velocity_frame = ctk.CTkFrame(self.root, fg_color=config.ui_colors[config.theme]["bg"])
        self.velocity_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(self.velocity_frame, text="Скорость (м/с):", width=150, anchor="w", 
                     text_color=config.ui_colors[config.theme]["fg"]).pack(side="left", padx=5)
        self.velocity_slider = ctk.CTkSlider(self.velocity_frame, from_=0, to=15, variable=self.velocity_var, 
                                            command=self.update_velocity, width=200)
        self.velocity_slider.pack(side="left", padx=5)
        self.velocity_entry = ctk.CTkEntry(self.velocity_frame, width=80, 
                                          text_color=config.ui_colors[config.theme]["fg"])
        self.velocity_entry.insert(0, str(self.velocity_var.get()))
        self.velocity_entry.pack(side="left", padx=5)
        self.velocity_entry.bind("<Return>", lambda e: self._safe_set_var(self.velocity_var, self.velocity_entry))

        self.angle_frame = ctk.CTkFrame(self.root, fg_color=config.ui_colors[config.theme]["bg"])
        self.angle_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(self.angle_frame, text="Угол наклона:", width=150, anchor="w", 
                     text_color=config.ui_colors[config.theme]["fg"]).pack(side="left", padx=5)
        self.angle_slider = ctk.CTkSlider(self.angle_frame, from_=0, to=90, variable=self.angle_var, 
                                         command=self.update_angle, width=200)
        self.angle_slider.pack(side="left", padx=5)
        self.angle_entry = ctk.CTkEntry(self.angle_frame, width=80, 
                                       text_color=config.ui_colors[config.theme]["fg"])
        self.angle_entry.insert(0, str(self.angle_var.get()))
        self.angle_entry.pack(side="left", padx=5)
        self.angle_entry.bind("<Return>", lambda e: self._safe_set_var(self.angle_var, self.angle_entry))

        self.air_resistance_frame = ctk.CTkFrame(self.root, fg_color=config.ui_colors[config.theme]["bg"])
        self.air_resistance_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(self.air_resistance_frame, text="Сопротивление воздуха:", width=150, anchor="w", 
                     text_color=config.ui_colors[config.theme]["fg"]).pack(side="left", padx=5)
        self.air_resistance_slider = ctk.CTkSlider(self.air_resistance_frame, from_=0, to=50, 
                                                  variable=self.air_resistance_var, command=self.update_air_resistance, width=200)
        self.air_resistance_slider.pack(side="left", padx=5)
        self.air_resistance_entry = ctk.CTkEntry(self.air_resistance_frame, width=80, 
                                                text_color=config.ui_colors[config.theme]["fg"])
        self.air_resistance_entry.insert(0, str(self.air_resistance_var.get()))
        self.air_resistance_entry.pack(side="left", padx=5)
        self.air_resistance_entry.bind("<Return>", lambda e: self._safe_set_var(self.air_resistance_var, self.air_resistance_entry))

        self.mode_button_frame = ctk.CTkFrame(self.root, fg_color=config.ui_colors[config.theme]["bg"])
        self.mode_button_frame.pack(pady=10, padx=(20, 0))
        self.slingshot_button = ctk.CTkButton(self.mode_button_frame, text="Рогатка", 
                                             command=self.set_slingshot_mode, width=100)
        self.slingshot_button.pack(side="left", padx=(0, 5))
        self.cannon_button = ctk.CTkButton(self.mode_button_frame, text="Пушка", 
                                          command=self.set_cannon_mode, width=100)
        self.cannon_button.pack(side="left", padx=5)

        self.shape_button_frame = ctk.CTkFrame(self.root, fg_color=config.ui_colors[config.theme]["bg"])
        self.shape_button_frame.pack(pady=10, padx=(20, 0))
        self.circle_button = ctk.CTkButton(self.shape_button_frame, text="Круг", 
                                          command=self.set_circle_shape, width=80)
        self.circle_button.pack(side="left", padx=(0, 5))
        self.square_button = ctk.CTkButton(self.shape_button_frame, text="Квадрат", 
                                          command=self.set_square_shape, width=80)
        self.square_button.pack(side="left", padx=(0, 5))
        self.triangle_button = ctk.CTkButton(self.shape_button_frame, text="Треугольник", 
                                            command=self.set_triangle_shape, width=80)
        self.triangle_button.pack(side="left", padx=(0, 5))
        self.button_button = ctk.CTkButton(self.shape_button_frame, text="Кнопка", 
                                          command=self.set_button_shape, width=80)
        self.button_button.pack(side="left", padx=5)

        self.clear_button = ctk.CTkButton(self.root, text="Очистить поле", 
                                         command=self.clear_objects, width=150)
        self.clear_button.pack(pady=10, padx=10)

        self.color_effect_switch = ctk.CTkSwitch(self.root, text="Эффект: Выкл", 
                                                command=self.toggle_color_effect, width=150)
        self.color_effect_switch.pack(pady=10, padx=10)

        self.theme_switch = ctk.CTkSwitch(self.root, text="Тема: Светлая" if config.theme == "light" else "Тема: Тёмная", 
                                         command=self.toggle_theme, width=150)
        self.theme_switch.pack(pady=10, padx=10)

        self.plot_button_frame = ctk.CTkFrame(self.root, fg_color=config.ui_colors[config.theme]["bg"])
        self.plot_button_frame.pack(pady=10, padx=(20, 0))
        self.velocity_plot_button = ctk.CTkButton(self.plot_button_frame, text="График скорости", 
                                                 command=lambda: plot_velocity_vs_time(self.physics.cannon), width=120)
        self.velocity_plot_button.pack(side="left", padx=(0, 5))
        self.range_plot_button = ctk.CTkButton(self.plot_button_frame, text="График дальности", 
                                              command=lambda: plot_range_vs_angle(self.physics.cannon), width=120)
        self.range_plot_button.pack(side="left", padx=5)

        self._update_mode_buttons()
        self._update_shape_buttons()
        self._update_plot_buttons()
        self._update_slider_states()

    def toggle_theme(self):
        config.theme = "dark" if config.theme == "light" else "light"
        ctk.set_appearance_mode(config.theme)
        self.root.configure(fg_color=config.ui_colors[config.theme]["bg"])

        for frame in [self.mass_frame, self.radius_frame, self.elasticity_frame, self.friction_frame,
                      self.gravity_frame, self.velocity_frame, self.angle_frame, self.air_resistance_frame]:
            frame.configure(fg_color=config.ui_colors[config.theme]["bg"])
            label, _, entry = frame.winfo_children()
            label.configure(text_color=config.ui_colors[config.theme]["fg"])
            entry.configure(text_color=config.ui_colors[config.theme]["fg"])

        self.mode_button_frame.configure(fg_color=config.ui_colors[config.theme]["bg"])
        self.shape_button_frame.configure(fg_color=config.ui_colors[config.theme]["bg"])
        self.plot_button_frame.configure(fg_color=config.ui_colors[config.theme]["bg"])

        self.theme_switch.configure(text="Тема: Светлая" if config.theme == "light" else "Тема: Тёмная")
        self._update_mode_buttons()
        self._update_shape_buttons()
        self._update_plot_buttons()
        self._update_slider_states()

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
        if config.mode == "cannon":
            return
        config.elasticity = round(float(value), 2)
        self.elasticity_entry.delete(0, ctk.END)
        self.elasticity_entry.insert(0, str(config.elasticity))

    def update_friction(self, value):
        if config.mode == "cannon":
            return
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
        self._update_plot_buttons()
        self._update_slider_states()
        self._update_shape_buttons()

    def set_cannon_mode(self):
        config.mode = "cannon"
        self.physics.slingshot.reset()
        self.physics.cannon.reset()
        self.clear_objects()
        # Ensure shape_type is valid for cannon mode
        if config.shape_type in ["square", "triangle"]:
            config.shape_type = "circle"
        self._update_mode_buttons()
        self._update_plot_buttons()
        self._update_slider_states()
        self._update_shape_buttons()

    def set_circle_shape(self):
        config.shape_type = "circle"
        config.static_mode = False
        self.physics.slingshot.reset()
        self._update_shape_buttons()

    def set_square_shape(self):
        config.shape_type = "square"
        config.static_mode = False
        self.physics.slingshot.reset()
        self._update_shape_buttons()

    def set_triangle_shape(self):
        config.shape_type = "triangle"
        config.static_mode = False
        self.physics.slingshot.reset()
        self._update_shape_buttons()

    def set_button_shape(self):
        config.shape_type = "button"
        config.static_mode = True
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