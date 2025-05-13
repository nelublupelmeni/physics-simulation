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
        self.root.configure(fg_color=self._get_theme_color("bg"))

        self.mass_var = ctk.DoubleVar(value=config.mass)
        self.radius_var = ctk.DoubleVar(value=config.radius)
        self.elasticity_var = ctk.DoubleVar(value=config.elasticity)
        self.friction_var = ctk.DoubleVar(value=config.friction)
        self.gravity_var = ctk.DoubleVar(value=config.gravity)  # Value in m/s²
        self.velocity_var = ctk.DoubleVar(value=config.initial_velocity / 100)
        self.angle_var = ctk.DoubleVar(value=config.angle)
        self.air_resistance_var = ctk.DoubleVar(value=config.air_resistance)

        self._is_switching_mode = False  # Debounce flag for mode switching

        self._create_widgets()
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _get_theme_color(self, key):
        default_colors = {
            "light": {"fg": "#000000", "bg": "#FFFFFF"},
            "dark": {"fg": "#FFFFFF", "bg": "#2B2B2B"}
        }
        try:
            return config.ui_colors[config.theme][key]
        except (KeyError, AttributeError):
            return default_colors.get(config.theme, default_colors["dark"])[key]

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

    def _update_shape_buttons(self):
        default_button_fg = ctk.ThemeManager.theme["CTkButton"]["fg_color"]
        light_fg_color = self._lighten_color(default_button_fg[0], 0.3)
        very_light_fg_color = self._lighten_color(default_button_fg[0], 0.7)

        if config.mode == "cannon":
            circle_fg = default_button_fg if config.shape_type == "circle" else light_fg_color
            button_fg = default_button_fg if config.shape_type == "button" else light_fg_color
            square_fg = very_light_fg_color
            triangle_fg = very_light_fg_color
        else:
            circle_fg = default_button_fg if config.shape_type == "circle" else light_fg_color
            square_fg = default_button_fg if config.shape_type == "square" else light_fg_color
            triangle_fg = default_button_fg if config.shape_type == "triangle" else light_fg_color
            button_fg = default_button_fg if config.shape_type == "button" else light_fg_color

        if self.circle_button.cget("fg_color") != circle_fg:
            self.circle_button.configure(fg_color=circle_fg)
        if self.square_button.cget("fg_color") != square_fg:
            self.square_button.configure(fg_color=square_fg)
        if self.triangle_button.cget("fg_color") != triangle_fg:
            self.triangle_button.configure(fg_color=triangle_fg)
        if self.button_button.cget("fg_color") != button_fg:
            self.button_button.configure(fg_color=button_fg)

    def _update_plot_buttons(self):
        default_button_fg = ctk.ThemeManager.theme["CTkButton"]["fg_color"]
        very_light_fg_color = self._lighten_color(default_button_fg[0], 0.7)

        # Normalize fg_color for comparison (handle tuple vs string)
        def normalize_color(color):
            if isinstance(color, tuple):
                return color[0] if color else '#000000'
            return color

        # Determine desired state
        if config.mode == "slingshot":
            plot_fg = very_light_fg_color
            plot_cmd = None
            range_cmd = None
        else:
            plot_fg = default_button_fg
            plot_cmd = lambda: plot_velocity_vs_time(self.physics.cannon)
            range_cmd = lambda: plot_range_vs_angle(self.physics.cannon)

        # Update velocity plot button
        velocity_current_fg = normalize_color(self.velocity_plot_button.cget("fg_color"))
        velocity_current_cmd = self.velocity_plot_button.cget("command")
        velocity_needs_update = False

        if velocity_current_fg != normalize_color(plot_fg):
            self.velocity_plot_button.configure(fg_color=plot_fg)
            velocity_needs_update = True
        if (config.mode == "slingshot" and velocity_current_cmd is not None) or \
           (config.mode == "cannon" and velocity_current_cmd != plot_cmd):
            self.velocity_plot_button.configure(command=plot_cmd)
            velocity_needs_update = True

        # Update range plot button
        range_current_fg = normalize_color(self.range_plot_button.cget("fg_color"))
        range_current_cmd = self.range_plot_button.cget("command")
        range_needs_update = False

        if range_current_fg != normalize_color(plot_fg):
            self.range_plot_button.configure(fg_color=plot_fg)
            range_needs_update = True
        if (config.mode == "slingshot" and range_current_cmd is not None) or \
           (config.mode == "cannon" and range_current_cmd != range_cmd):
            self.range_plot_button.configure(command=range_cmd)
            range_needs_update = True

    def _update_ui_state(self):
        if self._is_switching_mode:
            return
        self._is_switching_mode = True

        default_button_fg = ctk.ThemeManager.theme["CTkButton"]["fg_color"]
        default_slider_color = ctk.ThemeManager.theme["CTkSlider"]["progress_color"]
        default_slider_fg = ctk.ThemeManager.theme["CTkSlider"]["fg_color"]
        default_text_color = self._get_theme_color("fg")
        light_fg_color = self._lighten_color(default_button_fg[0], 0.3)
        very_light_fg_color = self._lighten_color(default_button_fg[0], 0.7)
        LIGHT_GRAY = "#D3D3D3"

        # Update mode buttons
        slingshot_fg = default_button_fg if config.mode == "slingshot" else light_fg_color
        cannon_fg = default_button_fg if config.mode == "cannon" else light_fg_color
        if self.slingshot_button.cget("fg_color") != slingshot_fg:
            self.slingshot_button.configure(fg_color=slingshot_fg)
        if self.cannon_button.cget("fg_color") != cannon_fg:
            self.cannon_button.configure(fg_color=cannon_fg)

        # Update shape buttons
        self._update_shape_buttons()

        # Update plot buttons
        self._update_plot_buttons()

        # Update sliders
        if config.mode == "cannon":
            self.elasticity_var.set(self.INITIAL_ELASTICITY)
            self.friction_var.set(self.INITIAL_FRICTION)
            config.elasticity = self.INITIAL_ELASTICITY
            config.friction = self.INITIAL_FRICTION
            self.elasticity_entry.delete(0, ctk.END)
            self.elasticity_entry.insert(0, str(self.INITIAL_ELASTICITY))
            self.friction_entry.delete(0, ctk.END)
            self.friction_entry.insert(0, str(self.INITIAL_FRICTION))
            elasticity_colors = {"progress_color": LIGHT_GRAY, "fg_color": LIGHT_GRAY, "text_color": LIGHT_GRAY}
            friction_colors = {"progress_color": LIGHT_GRAY, "fg_color": LIGHT_GRAY, "text_color": LIGHT_GRAY}
            velocity_colors = {"progress_color": default_slider_color, "fg_color": default_slider_fg, "text_color": default_text_color}
            angle_colors = {"progress_color": default_slider_color, "fg_color": default_slider_fg, "text_color": default_text_color}
            air_colors = {"progress_color": default_slider_color, "fg_color": default_slider_fg, "text_color": default_text_color}
        else:
            self.velocity_var.set(self.INITIAL_VELOCITY)
            self.angle_var.set(self.INITIAL_ANGLE)
            self.air_resistance_var.set(self.INITIAL_AIR_RESISTANCE)
            config.initial_velocity = self.INITIAL_VELOCITY * 100
            config.angle = self.INITIAL_ANGLE
            config.air_resistance = self.INITIAL_AIR_RESISTANCE
            self.velocity_entry.delete(0, ctk.END)
            self.velocity_entry.insert(0, str(self.INITIAL_VELOCITY))
            self.angle_entry.delete(0, ctk.END)
            self.angle_entry.insert(0, str(self.INITIAL_ANGLE))
            self.air_resistance_entry.delete(0, ctk.END)
            self.air_resistance_entry.insert(0, str(self.INITIAL_AIR_RESISTANCE))
            elasticity_colors = {"progress_color": default_slider_color, "fg_color": default_slider_fg, "text_color": default_text_color}
            friction_colors = {"progress_color": default_slider_color, "fg_color": default_slider_fg, "text_color": default_text_color}
            velocity_colors = {"progress_color": LIGHT_GRAY, "fg_color": LIGHT_GRAY, "text_color": LIGHT_GRAY}
            angle_colors = {"progress_color": LIGHT_GRAY, "fg_color": LIGHT_GRAY, "text_color": LIGHT_GRAY}
            air_colors = {"progress_color": LIGHT_GRAY, "fg_color": LIGHT_GRAY, "text_color": LIGHT_GRAY}

        if self.elasticity_slider.cget("progress_color") != elasticity_colors["progress_color"]:
            self.elasticity_slider.configure(progress_color=elasticity_colors["progress_color"], fg_color=elasticity_colors["fg_color"])
            self.elasticity_entry.configure(text_color=elasticity_colors["text_color"])
            self.elasticity_label.configure(text_color=elasticity_colors["text_color"])
        if self.friction_slider.cget("progress_color") != friction_colors["progress_color"]:
            self.friction_slider.configure(progress_color=friction_colors["progress_color"], fg_color=friction_colors["fg_color"])
            self.friction_entry.configure(text_color=friction_colors["text_color"])
            self.friction_label.configure(text_color=friction_colors["text_color"])
        if self.velocity_slider.cget("progress_color") != velocity_colors["progress_color"]:
            self.velocity_slider.configure(progress_color=velocity_colors["progress_color"], fg_color=velocity_colors["fg_color"])
            self.velocity_entry.configure(text_color=velocity_colors["text_color"])
            self.velocity_label.configure(text_color=velocity_colors["text_color"])
        if self.angle_slider.cget("progress_color") != angle_colors["progress_color"]:
            self.angle_slider.configure(progress_color=angle_colors["progress_color"], fg_color=angle_colors["fg_color"])
            self.angle_entry.configure(text_color=angle_colors["text_color"])
            self.angle_label.configure(text_color=angle_colors["text_color"])
        if self.air_resistance_slider.cget("progress_color") != air_colors["progress_color"]:
            self.air_resistance_slider.configure(progress_color=air_colors["progress_color"], fg_color=air_colors["fg_color"])
            self.air_resistance_entry.configure(text_color=air_colors["text_color"])
            self.air_resistance_label.configure(text_color=air_colors["text_color"])

        # Throttle rendering to reduce shaking
        self.root.after(10, self._complete_ui_update)

    def _complete_ui_update(self):
        self._is_switching_mode = False
        self.root.update_idletasks()

    def _safe_set_var(self, var, entry):
        if (var in [self.velocity_var, self.angle_var, self.air_resistance_var] and config.mode == "slingshot") or \
           (var in [self.elasticity_var, self.friction_var] and config.mode == "cannon"):
            entry.delete(0, ctk.END)
            entry.insert(0, str(var.get()))
            return
        try:
            precision = 3 if var == self.angle_var else 2
            var.set(round(float(entry.get()), precision))
        except ValueError:
            entry.delete(0, ctk.END)
            entry.insert(0, str(var.get()))

    def _create_widgets(self):
        self.INITIAL_ELASTICITY = config.elasticity
        self.INITIAL_FRICTION = config.friction
        self.INITIAL_VELOCITY = config.initial_velocity / 100
        self.INITIAL_ANGLE = config.angle
        self.INITIAL_AIR_RESISTANCE = config.air_resistance

        self.mass_frame = ctk.CTkFrame(self.root, fg_color=self._get_theme_color("bg"))
        self.mass_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(self.mass_frame, text="Масса:", width=150, anchor="w", 
                     text_color=self._get_theme_color("fg")).pack(side="left", padx=5)
        self.mass_slider = ctk.CTkSlider(self.mass_frame, from_=1, to=100, variable=self.mass_var, 
                                         command=self.update_mass, width=200)
        self.mass_slider.pack(side="left", padx=5)
        self.mass_entry = ctk.CTkEntry(self.mass_frame, width=80, 
                                       text_color=self._get_theme_color("fg"))
        self.mass_entry.insert(0, str(self.mass_var.get()))
        self.mass_entry.pack(side="left", padx=5)
        self.mass_entry.bind("<Return>", lambda e: self._safe_set_var(self.mass_var, self.mass_entry))

        self.radius_frame = ctk.CTkFrame(self.root, fg_color=self._get_theme_color("bg"))
        self.radius_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(self.radius_frame, text="Радиус:", width=150, anchor="w", 
                     text_color=self._get_theme_color("fg")).pack(side="left", padx=5)
        self.radius_slider = ctk.CTkSlider(self.radius_frame, from_=10, to=100, variable=self.radius_var, 
                                           command=self.update_radius, width=200)
        self.radius_slider.pack(side="left", padx=5)
        self.radius_entry = ctk.CTkEntry(self.radius_frame, width=80, 
                                         text_color=self._get_theme_color("fg"))
        self.radius_entry.insert(0, str(self.radius_var.get()))
        self.radius_entry.pack(side="left", padx=5)
        self.radius_entry.bind("<Return>", lambda e: self._safe_set_var(self.radius_var, self.radius_entry))

        self.elasticity_frame = ctk.CTkFrame(self.root, fg_color=self._get_theme_color("bg"))
        self.elasticity_frame.pack(fill="x", padx=10, pady=5)
        self.elasticity_label = ctk.CTkLabel(self.elasticity_frame, text="Упругость:", width=150, anchor="w", 
                                             text_color=self._get_theme_color("fg"))
        self.elasticity_label.pack(side="left", padx=5)
        self.elasticity_slider = ctk.CTkSlider(self.elasticity_frame, from_=0, to=1, variable=self.elasticity_var, 
                                               command=self.update_elasticity, width=200)
        self.elasticity_slider.pack(side="left", padx=5)
        self.elasticity_entry = ctk.CTkEntry(self.elasticity_frame, width=80, 
                                             text_color=self._get_theme_color("fg"))
        self.elasticity_entry.insert(0, str(self.elasticity_var.get()))
        self.elasticity_entry.pack(side="left", padx=5)
        self.elasticity_entry.bind("<Return>", lambda e: self._safe_set_var(self.elasticity_var, self.elasticity_entry))

        self.friction_frame = ctk.CTkFrame(self.root, fg_color=self._get_theme_color("bg"))
        self.friction_frame.pack(fill="x", padx=10, pady=5)
        self.friction_label = ctk.CTkLabel(self.friction_frame, text="Трение:", width=150, anchor="w", 
                                           text_color=self._get_theme_color("fg"))
        self.friction_label.pack(side="left", padx=5)
        self.friction_slider = ctk.CTkSlider(self.friction_frame, from_=0, to=1, variable=self.friction_var, 
                                             command=self.update_friction, width=200)
        self.friction_slider.pack(side="left", padx=5)
        self.friction_entry = ctk.CTkEntry(self.friction_frame, width=80, 
                                           text_color=self._get_theme_color("fg"))
        self.friction_entry.insert(0, str(self.friction_var.get()))
        self.friction_entry.pack(side="left", padx=5)
        self.friction_entry.bind("<Return>", lambda e: self._safe_set_var(self.friction_var, self.friction_entry))

        self.gravity_frame = ctk.CTkFrame(self.root, fg_color=self._get_theme_color("bg"))
        self.gravity_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(self.gravity_frame, text="Гравитация (м/с²):", width=150, anchor="w", 
                     text_color=self._get_theme_color("fg")).pack(side="left", padx=5)
        self.gravity_slider = ctk.CTkSlider(self.gravity_frame, from_=0, to=50, variable=self.gravity_var, 
                                            command=self.update_gravity, width=200)
        self.gravity_slider.pack(side="left", padx=5)
        self.gravity_entry = ctk.CTkEntry(self.gravity_frame, width=80, 
                                          text_color=self._get_theme_color("fg"))
        self.gravity_entry.insert(0, str(self.gravity_var.get()))
        self.gravity_entry.pack(side="left", padx=5)
        self.gravity_entry.bind("<Return>", lambda e: self._safe_set_var(self.gravity_var, self.gravity_entry))

        self.velocity_frame = ctk.CTkFrame(self.root, fg_color=self._get_theme_color("bg"))
        self.velocity_frame.pack(fill="x", padx=10, pady=5)
        self.velocity_label = ctk.CTkLabel(self.velocity_frame, text="Скорость (м/с):", width=150, anchor="w", 
                                           text_color=self._get_theme_color("fg"))
        self.velocity_label.pack(side="left", padx=5)
        self.velocity_slider = ctk.CTkSlider(self.velocity_frame, from_=0, to=15, variable=self.velocity_var, 
                                             command=self.update_velocity, width=200)
        self.velocity_slider.pack(side="left", padx=5)
        self.velocity_entry = ctk.CTkEntry(self.velocity_frame, width=80, 
                                           text_color=self._get_theme_color("fg"))
        self.velocity_entry.insert(0, str(self.velocity_var.get()))
        self.velocity_entry.pack(side="left", padx=5)
        self.velocity_entry.bind("<Return>", lambda e: self._safe_set_var(self.velocity_var, self.velocity_entry))

        self.angle_frame = ctk.CTkFrame(self.root, fg_color=self._get_theme_color("bg"))
        self.angle_frame.pack(fill="x", padx=10, pady=5)
        self.angle_label = ctk.CTkLabel(self.angle_frame, text="Угол наклона:", width=150, anchor="w", 
                                        text_color=self._get_theme_color("fg"))
        self.angle_label.pack(side="left", padx=5)
        self.angle_slider = ctk.CTkSlider(self.angle_frame, from_=0, to=90, variable=self.angle_var, 
                                          command=self.update_angle, width=200)
        self.angle_slider.pack(side="left", padx=5)
        self.angle_entry = ctk.CTkEntry(self.angle_frame, width=80, 
                                        text_color=self._get_theme_color("fg"))
        self.angle_entry.insert(0, str(self.angle_var.get()))
        self.angle_entry.pack(side="left", padx=5)
        self.angle_entry.bind("<Return>", lambda e: self._safe_set_var(self.angle_var, self.angle_entry))

        self.air_resistance_frame = ctk.CTkFrame(self.root, fg_color=self._get_theme_color("bg"))
        self.air_resistance_frame.pack(fill="x", padx=10, pady=5)
        self.air_resistance_label = ctk.CTkLabel(self.air_resistance_frame, text="Сопротивление воздуха:", width=150, anchor="w", 
                                                 text_color=self._get_theme_color("fg"))
        self.air_resistance_label.pack(side="left", padx=5)
        self.air_resistance_slider = ctk.CTkSlider(self.air_resistance_frame, from_=0, to=50, 
                                                   variable=self.air_resistance_var, command=self.update_air_resistance, width=200)
        self.air_resistance_slider.pack(side="left", padx=5)
        self.air_resistance_entry = ctk.CTkEntry(self.air_resistance_frame, width=80, 
                                                 text_color=self._get_theme_color("fg"))
        self.air_resistance_entry.insert(0, str(self.air_resistance_var.get()))
        self.air_resistance_entry.pack(side="left", padx=5)
        self.air_resistance_entry.bind("<Return>", lambda e: self._safe_set_var(self.air_resistance_var, self.air_resistance_entry))

        self.mode_button_frame = ctk.CTkFrame(self.root, fg_color=self._get_theme_color("bg"))
        self.mode_button_frame.pack(pady=10, padx=(20, 0))
        self.slingshot_button = ctk.CTkButton(self.mode_button_frame, text="Рогатка", 
                                              command=self.set_slingshot_mode, width=100)
        self.slingshot_button.pack(side="left", padx=(0, 5))
        self.cannon_button = ctk.CTkButton(self.mode_button_frame, text="Пушка", 
                                           command=self.set_cannon_mode, width=100)
        self.cannon_button.pack(side="left", padx=5)

        self.shape_button_frame = ctk.CTkFrame(self.root, fg_color=self._get_theme_color("bg"))
        self.shape_button_frame.pack(pady=10, padx=(20, 0))
        self.circle_button = ctk.CTkButton(self.shape_button_frame, text="Круг", 
                                           command=self.set_circle_shape, width=80)
        self.circle_button.pack(side="left", padx=5)
        self.square_button = ctk.CTkButton(self.shape_button_frame, text="Квадрат", 
                                           command=self.set_square_shape, width=80)
        self.square_button.pack(side="left", padx=5)
        self.triangle_button = ctk.CTkButton(self.shape_button_frame, text="Треугольник", 
                                             command=self.set_triangle_shape, width=80)
        self.triangle_button.pack(side="left", padx=5)
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

        self.plot_button_frame = ctk.CTkFrame(self.root, fg_color=self._get_theme_color("bg"))
        self.plot_button_frame.pack(pady=10, padx=(20, 0))
        self.velocity_plot_button = ctk.CTkButton(self.plot_button_frame, text="График скорости", 
                                                  command=lambda: plot_velocity_vs_time(self.physics.cannon), width=120)
        self.velocity_plot_button.pack(side="left", padx=(0, 5))
        self.range_plot_button = ctk.CTkButton(self.plot_button_frame, text="График дальности", 
                                               command=lambda: plot_range_vs_angle(self.physics.cannon), width=120)
        self.range_plot_button.pack(side="left", padx=5)

        # Initialize shape button commands based on initial mode
        self._update_shape_button_commands()
        self._update_ui_state()

    def _update_shape_button_commands(self):
        if config.mode == "cannon":
            if self.circle_button.cget("command") != self.set_circle_shape:
                self.circle_button.configure(command=self.set_circle_shape)
            if self.button_button.cget("command") != self.set_button_shape:
                self.button_button.configure(command=self.set_button_shape)
            if self.square_button.cget("command") is not None:
                self.square_button.configure(command=None)
            if self.triangle_button.cget("command") is not None:
                self.triangle_button.configure(command=None)
        else:
            if self.circle_button.cget("command") != self.set_circle_shape:
                self.circle_button.configure(command=self.set_circle_shape)
            if self.square_button.cget("command") != self.set_square_shape:
                self.square_button.configure(command=self.set_square_shape)
            if self.triangle_button.cget("command") != self.set_triangle_shape:
                self.triangle_button.configure(command=self.set_triangle_shape)
            if self.button_button.cget("command") != self.set_button_shape:
                self.button_button.configure(command=self.set_button_shape)

    def toggle_theme(self):
        config.theme = "dark" if config.theme == "light" else "light"
        ctk.set_appearance_mode(config.theme)
        self.root.configure(fg_color=self._get_theme_color("bg"))

        for frame in [self.mass_frame, self.radius_frame, self.elasticity_frame, self.friction_frame,
                      self.gravity_frame, self.velocity_frame, self.angle_frame, self.air_resistance_frame]:
            frame.configure(fg_color=self._get_theme_color("bg"))
            children = frame.winfo_children()
            if len(children) >= 3:
                label, _, entry = children[:3]
                if isinstance(label, ctk.CTkLabel):
                    label.configure(text_color=self._get_theme_color("fg"))
                if isinstance(entry, ctk.CTkEntry):
                    entry.configure(text_color=self._get_theme_color("fg"))

        self.mode_button_frame.configure(fg_color=self._get_theme_color("bg"))
        self.shape_button_frame.configure(fg_color=self._get_theme_color("bg"))
        self.plot_button_frame.configure(fg_color=self._get_theme_color("bg"))

        self.theme_switch.configure(text="Тема: Светлая" if config.theme == "light" else "Тема: Тёмная")
        self._update_ui_state()

    def update_gravity(self, value):
        gravity_ms2 = round(float(value), 2)  # Value in m/s²
        gravity_cm2 = gravity_ms2 * 100  # Convert to cm/s² for Pymunk
        self.physics.set_gravity(gravity_cm2)
        self.gravity_entry.delete(0, ctk.END)
        self.gravity_entry.insert(0, str(gravity_ms2))
        config.gravity = gravity_ms2  # Update config to reflect UI value

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
            self.elasticity_var.set(self.INITIAL_ELASTICITY)
            config.elasticity = self.INITIAL_ELASTICITY
            self.elasticity_entry.delete(0, ctk.END)
            self.elasticity_entry.insert(0, str(self.INITIAL_ELASTICITY))
            return
        config.elasticity = round(float(value), 2)
        self.elasticity_entry.delete(0, ctk.END)
        self.elasticity_entry.insert(0, str(config.elasticity))

    def update_friction(self, value):
        if config.mode == "cannon":
            self.friction_var.set(self.INITIAL_FRICTION)
            config.friction = self.INITIAL_FRICTION
            self.friction_entry.delete(0, ctk.END)
            self.friction_entry.insert(0, str(self.INITIAL_FRICTION))
            return
        config.friction = round(float(value), 2)
        self.friction_entry.delete(0, ctk.END)
        self.friction_entry.insert(0, str(config.friction))

    def update_velocity(self, value):
        if config.mode == "slingshot":
            self.velocity_var.set(self.INITIAL_VELOCITY)
            config.initial_velocity = self.INITIAL_VELOCITY * 100
            self.velocity_entry.delete(0, ctk.END)
            self.velocity_entry.insert(0, str(self.INITIAL_VELOCITY))
            return
        velocity_mps = round(float(value), 2)
        config.initial_velocity = velocity_mps * 100
        self.velocity_entry.delete(0, ctk.END)
        self.velocity_entry.insert(0, str(velocity_mps))

    def update_angle(self, value):
        if config.mode == "slingshot":
            self.angle_var.set(self.INITIAL_ANGLE)
            config.angle = self.INITIAL_ANGLE
            self.angle_entry.delete(0, ctk.END)
            self.angle_entry.insert(0, str(self.INITIAL_ANGLE))
            return
        config.angle = round(float(value), 3)
        self.angle_entry.delete(0, ctk.END)
        self.angle_entry.insert(0, str(config.angle))

    def update_air_resistance(self, value):
        if config.mode == "slingshot":
            self.air_resistance_var.set(self.INITIAL_AIR_RESISTANCE)
            config.air_resistance = self.INITIAL_AIR_RESISTANCE
            self.air_resistance_entry.delete(0, ctk.END)
            self.air_resistance_entry.insert(0, str(self.INITIAL_AIR_RESISTANCE))
            return
        config.air_resistance = round(float(value), 2)
        self.air_resistance_entry.delete(0, ctk.END)
        self.air_resistance_entry.insert(0, str(config.air_resistance))

    def clear_objects(self):
        self.physics.clear_objects()

    def set_slingshot_mode(self):
        if config.mode == "slingshot":
            return
        config.mode = "slingshot"
        self.physics.slingshot.reset()
        self.physics.cannon.reset()
        self.clear_objects()
        self._update_shape_button_commands()
        self._update_ui_state()

    def set_cannon_mode(self):
        if config.mode == "cannon":
            return
        config.mode = "cannon"
        self.physics.slingshot.reset()
        self.physics.cannon.reset()
        self.clear_objects()
        if config.shape_type in ["square", "triangle"]:
            config.shape_type = "circle"
        self._update_shape_button_commands()
        self._update_ui_state()

    def set_circle_shape(self):
        config.shape_type = "circle"
        config.static_mode = False
        self.physics.slingshot.reset()
        self._update_shape_buttons()

    def set_square_shape(self):
        if config.mode == "cannon":
            return
        config.shape_type = "square"
        config.static_mode = False
        self.physics.slingshot.reset()
        self._update_shape_buttons()

    def set_triangle_shape(self):
        if config.mode == "cannon":
            return
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