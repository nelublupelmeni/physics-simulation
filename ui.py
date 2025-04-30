import customtkinter as ctk
import config

def create_ui(physics):
    root = ctk.CTk()
    root.title("Настройки симуляции")
    window_width = 500
    window_height = 650
    pygame_width = 1200
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    total_width = pygame_width + window_width
    x_position = (screen_width - total_width) // 2 + pygame_width
    y_position = (screen_height - window_height) // 2
    root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
    root.resizable(False, False)

    mass_var = ctk.DoubleVar(value=config.mass)
    radius_var = ctk.DoubleVar(value=config.radius)
    elasticity_var = ctk.DoubleVar(value=config.elasticity)
    friction_var = ctk.DoubleVar(value=config.friction)
    gravity_var = ctk.DoubleVar(value=config.gravity)
    velocity_var = ctk.DoubleVar(value=config.initial_velocity / 100)
    angle_var = ctk.DoubleVar(value=config.angle)

    def update_gravity(value):
        gravity = round(float(value), 2)
        physics.set_gravity(gravity)
        gravity_entry.delete(0, ctk.END)
        gravity_entry.insert(0, str(gravity))

    def update_mass(value):
        config.mass = round(float(value), 2)
        mass_entry.delete(0, ctk.END)
        mass_entry.insert(0, str(config.mass))

    def update_radius(value):
        config.radius = round(float(value), 2)
        radius_entry.delete(0, ctk.END)
        radius_entry.insert(0, str(config.radius))

    def update_elasticity(value):
        config.elasticity = round(float(value), 2)
        elasticity_entry.delete(0, ctk.END)
        elasticity_entry.insert(0, str(config.elasticity))

    def update_friction(value):
        config.friction = round(float(value), 2)
        friction_entry.delete(0, ctk.END)
        friction_entry.insert(0, str(config.friction))

    def update_velocity(value):
        velocity_mps = round(float(value), 2)
        config.initial_velocity = velocity_mps * 100
        velocity_entry.delete(0, ctk.END)
        velocity_entry.insert(0, str(velocity_mps))

    def update_angle(value):
        config.angle = round(float(value), 2)
        angle_entry.delete(0, ctk.END)
        angle_entry.insert(0, str(config.angle))

    def clear_objects():
        physics.clear_objects()

    def toggle_mode():
        if config.mode == "normal":
            config.mode = "slingshot"
            mode_button.configure(text="Режим: Рогатка")
        elif config.mode == "slingshot":
            config.mode = "cannon"
            mode_button.configure(text="Режим: Пушка")
        else:
            config.mode = "normal"
            mode_button.configure(text="Режим: Обычный")
        physics.slingshot.reset()
        physics.cannon.reset()
        clear_objects()

    def toggle_color_effect():
        config.color_effect = not config.color_effect
        color_effect_button.configure(text="Эффект: " + ("Вкл" if config.color_effect else "Выкл"))

    ctk.CTkLabel(root, text="Масса:").grid(row=0, column=0, padx=10, pady=10)
    mass_slider = ctk.CTkSlider(root, from_=1, to=100, variable=mass_var, command=update_mass)
    mass_slider.grid(row=0, column=1, padx=10, pady=10)
    mass_entry = ctk.CTkEntry(root, width=80)
    mass_entry.insert(0, str(mass_var.get()))
    mass_entry.grid(row=0, column=2, padx=10, pady=10)
    mass_entry.bind("<Return>", lambda e: mass_var.set(round(float(mass_entry.get()), 2)))

    ctk.CTkLabel(root, text="Радиус:").grid(row=1, column=0, padx=10, pady=10)
    radius_slider = ctk.CTkSlider(root, from_=10, to=100, variable=radius_var, command=update_radius)
    radius_slider.grid(row=1, column=1, padx=10, pady=10)
    radius_entry = ctk.CTkEntry(root, width=80)
    radius_entry.insert(0, str(radius_var.get()))
    radius_entry.grid(row=1, column=2, padx=10, pady=10)
    radius_entry.bind("<Return>", lambda e: radius_var.set(round(float(radius_entry.get()), 2)))

    ctk.CTkLabel(root, text="Упругость:").grid(row=2, column=0, padx=10, pady=10)
    elasticity_slider = ctk.CTkSlider(root, from_=0, to=1, variable=elasticity_var, command=update_elasticity)
    elasticity_slider.grid(row=2, column=1, padx=10, pady=10)
    elasticity_entry = ctk.CTkEntry(root, width=80)
    elasticity_entry.insert(0, str(elasticity_var.get()))
    elasticity_entry.grid(row=2, column=2, padx=10, pady=10)
    elasticity_entry.bind("<Return>", lambda e: elasticity_var.set(round(float(elasticity_entry.get()), 2)))

    ctk.CTkLabel(root, text="Трение:").grid(row=3, column=0, padx=10, pady=10)
    friction_slider = ctk.CTkSlider(root, from_=0, to=1, variable=friction_var, command=update_friction)
    friction_slider.grid(row=3, column=1, padx=10, pady=10)
    friction_entry = ctk.CTkEntry(root, width=80)
    friction_entry.insert(0, str(friction_var.get()))
    friction_entry.grid(row=3, column=2, padx=10, pady=10)
    friction_entry.bind("<Return>", lambda e: friction_var.set(round(float(friction_entry.get()), 2)))

    ctk.CTkLabel(root, text="Гравитация:").grid(row=4, column=0, padx=10, pady=10)
    gravity_slider = ctk.CTkSlider(root, from_=0, to=2000, variable=gravity_var, command=update_gravity)
    gravity_slider.grid(row=4, column=1, padx=10, pady=10)
    gravity_entry = ctk.CTkEntry(root, width=80)
    gravity_entry.insert(0, str(gravity_var.get()))
    gravity_entry.grid(row=4, column=2, padx=10, pady=10)
    gravity_entry.bind("<Return>", lambda e: gravity_var.set(round(float(gravity_entry.get()), 2)))

    ctk.CTkLabel(root, text="Скорость (м/с):").grid(row=5, column=0, padx=10, pady=10)
    velocity_slider = ctk.CTkSlider(root, from_=0, to=30, variable=velocity_var, command=update_velocity)
    velocity_slider.grid(row=5, column=1, padx=10, pady=10)
    velocity_entry = ctk.CTkEntry(root, width=80)
    velocity_entry.insert(0, str(velocity_var.get()))
    velocity_entry.grid(row=5, column=2, padx=10, pady=10)
    velocity_entry.bind("<Return>", lambda e: velocity_var.set(round(float(velocity_entry.get()), 2)))

    ctk.CTkLabel(root, text="Угол наклона:").grid(row=6, column=0, padx=10, pady=10)
    angle_slider = ctk.CTkSlider(root, from_=0, to=90, variable=angle_var, command=update_angle)
    angle_slider.grid(row=6, column=1, padx=10, pady=10)
    angle_entry = ctk.CTkEntry(root, width=80)
    angle_entry.insert(0, str(angle_var.get()))
    angle_entry.grid(row=6, column=2, padx=10, pady=10)
    angle_entry.bind("<Return>", lambda e: angle_var.set(round(float(angle_entry.get()), 2)))

    ctk.CTkButton(root, text="Очистить поле", command=clear_objects).grid(row=7, column=0, columnspan=3, padx=10, pady=20)
    mode_button = ctk.CTkButton(root, text="Режим: Обычный", command=toggle_mode)
    mode_button.grid(row=8, column=0, columnspan=3, padx=10, pady=20)
    color_effect_button = ctk.CTkButton(root, text="Эффект: Выкл", command=toggle_color_effect)
    color_effect_button.grid(row=9, column=0, columnspan=3, padx=10, pady=20)

    root.mainloop()