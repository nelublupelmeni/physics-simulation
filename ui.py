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

    def _create_widgets(self):
        ctk.CTkLabel(self.root, text="Масса:").grid(row=0, column=0, padx=10, pady=5)
        self.mass_slider = ctk.CTkSlider(self.root, from_=1, to=100, variable=self.mass_var, command=self.update_mass)
        self.mass_slider.grid(row=0, column=1, padx=10, pady=5)
        self.mass_entry = ctk.CTkEntry(self.root, width=80)
        self.mass_entry.insert(0, str(self.mass_var.get()))
        self.mass_entry.grid(row=0, column=2, padx=10, pady=5)
        self.mass_entry.bind("<Return>", lambda e: self.mass_var.set(round(float(self.mass_entry.get()), 2)))

        ctk.CTkLabel(self.root, text="Радиус:").grid(row=1, column=0, padx=10, pady=5)
        self.radius_slider = ctk.CTkSlider(self.root, from_=10, to=100, variable=self.radius_var, command=self.update_radius)
        self.radius_slider.grid(row=1, column=1, padx=10, pady=5)
        self.radius_entry = ctk.CTkEntry(self.root, width=80)
        self.radius_entry.insert(0, str(self.radius_var.get()))
        self.radius_entry.grid(row=1, column=2, padx=10, pady=5)
        self.radius_entry.bind("<Return>", lambda e: self.radius_var.set(round(float(self.radius_entry.get()), 2)))

        ctk.CTkLabel(self.root, text="Упругость:").grid(row=2, column=0, padx=10, pady=5)
        self.elasticity_slider = ctk.CTkSlider(self.root, from_=0, to=1, variable=self.elasticity_var, command=self.update_elasticity)
        self.elasticity_slider.grid(row=2, column=1, padx=10, pady=5)
        self.elasticity_entry = ctk.CTkEntry(self.root, width=80)
        self.elasticity_entry.insert(0, str(self.elasticity_var.get()))
        self.elasticity_entry.grid(row=2, column=2, padx=10, pady=5)
        self.elasticity_entry.bind("<Return>", lambda e: self.elasticity_var.set(round(float(self.elasticity_entry.get()), 2)))

        ctk.CTkLabel(self.root, text="Трение:").grid(row=3, column=0, padx=10, pady=5)
        self.friction_slider = ctk.CTkSlider(self.root, from_=0, to=1, variable=self.friction_var, command=self.update_friction)
        self.friction_slider.grid(row=3, column=1, padx=10, pady=5)
        self.friction_entry = ctk.CTkEntry(self.root, width=80)
        self.friction_entry.insert(0, str(self.friction_var.get()))
        self.friction_entry.grid(row=3, column=2, padx=10, pady=5)
        self.friction_entry.bind("<Return>", lambda e: self.friction_var.set(round(float(self.friction_entry.get()), 2)))

        ctk.CTkLabel(self.root, text="Гравитация:").grid(row=4, column=0, padx=10, pady=5)
        self.gravity_slider = ctk.CTkSlider(self.root, from_=0, to=2000, variable=self.gravity_var, command=self.update_gravity)
        self.gravity_slider.grid(row=4, column=1, padx=10, pady=5)
        self.gravity_entry = ctk.CTkEntry(self.root, width=80)
        self.gravity_entry.insert(0, str(self.gravity_var.get()))
        self.gravity_entry.grid(row=4, column=2, padx=10, pady=5)
        self.gravity_entry.bind("<Return>", lambda e: self.gravity_var.set(round(float(self.gravity_entry.get()), 2)))

        ctk.CTkLabel(self.root, text="Скорость (м/с):").grid(row=5, column=0, padx=10, pady=5)
        self.velocity_slider = ctk.CTkSlider(self.root, from_=0, to=15, variable=self.velocity_var, command=self.update_velocity)
        self.velocity_slider.grid(row=5, column=1, padx=10, pady=5)
        self.velocity_entry = ctk.CTkEntry(self.root, width=80)
        self.velocity_entry.insert(0, str(self.velocity_var.get()))
        self.velocity_entry.grid(row=5, column=2, padx=10, pady=5)
        self.velocity_entry.bind("<Return>", lambda e: self.velocity_var.set(round(float(self.velocity_entry.get()), 2)))

        ctk.CTkLabel(self.root, text="Угол наклона:").grid(row=6, column=0, padx=10, pady=5)
        self.angle_slider = ctk.CTkSlider(self.root, from_=0, to=90, variable=self.angle_var, command=self.update_angle)
        self.angle_slider.grid(row=6, column=1, padx=10, pady=5)
        self.angle_entry = ctk.CTkEntry(self.root, width=80)
        self.angle_entry.insert(0, str(self.angle_var.get()))
        self.angle_entry.grid(row=6, column=2, padx=10, pady=5)
        self.angle_entry.bind("<Return>", lambda e: self.angle_var.set(round(float(self.angle_entry.get()), 2)))

        ctk.CTkLabel(self.root, text="Сопротивление воздуха:").grid(row=7, column=0, padx=10, pady=5)
        self.air_resistance_slider = ctk.CTkSlider(self.root, from_=0, to=50, variable=self.air_resistance_var, command=self.update_air_resistance)
        self.air_resistance_slider.grid(row=7, column=1, padx=10, pady=5)
        self.air_resistance_entry = ctk.CTkEntry(self.root, width=80)
        self.air_resistance_entry.insert(0, str(self.air_resistance_var.get()))
        self.air_resistance_entry.grid(row=7, column=2, padx=10, pady=5)
        self.air_resistance_entry.bind("<Return>", lambda e: self.air_resistance_var.set(round(float(self.air_resistance_entry.get()), 2)))

        self.clear_button = ctk.CTkButton(self.root, text="Очистить поле", command=self.clear_objects)
        self.clear_button.grid(row=8, column=0, columnspan=3, padx=10, pady=10)
        self.mode_button = ctk.CTkButton(self.root, text="Режим: Рогатка", command=self.toggle_mode)
        self.mode_button.grid(row=9, column=0, columnspan=3, padx=10, pady=10)
        self.color_effect_button = ctk.CTkButton(self.root, text="Эффект: Выкл", command=self.toggle_color_effect)
        self.color_effect_button.grid(row=10, column=0, columnspan=3, padx=10, pady=10)

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

    def toggle_mode(self):
        if config.mode == "slingshot":
            config.mode = "cannon"
            self.mode_button.configure(text="Режим: Пушка")
        else:
            config.mode = "slingshot"
            self.mode_button.configure(text="Режим: Рогатка")
        self.physics.slingshot.reset()
        self.physics.cannon.reset()
        self.clear_objects()

    def toggle_color_effect(self):
        config.color_effect = not config.color_effect
        self.color_effect_button.configure(text="Эффект: " + ("Вкл" if config.color_effect else "Выкл"))

    def _on_closing(self):
        self.running_event.clear()
        self.sim_thread.join(timeout=1.0)
        self.root.quit()
        self.root.destroy()

    def run(self):
        self.root.mainloop()