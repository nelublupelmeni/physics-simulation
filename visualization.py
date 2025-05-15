import matplotlib.pyplot as plt
from collections import defaultdict


def plot_velocity_vs_time(cannon):
    """Отрисовка графика скорости от времени."""
    if not cannon.velocity_points:
        return

    times, velocities = zip(*cannon.velocity_points)

    plt.figure(figsize=(10, 6))
    plt.plot(times, velocities, 'b-', label='Скорость шара')
    plt.xlabel('Время (с)')
    plt.ylabel('Скорость (м/с)')
    plt.title('Зависимость скорости шара от времени')
    plt.legend()
    plt.grid(True)
    plt.savefig('velocity_vs_time.png')


def plot_range_vs_angle(cannon):
    """Отрисовка графика дальности полёта от угла наклона."""
    if not cannon.range_data:
        return

    # Средние значения дальности для повторяющихся углов
    angle_ranges = defaultdict(list)
    for angle, range_m in cannon.range_data:
        angle_ranges[angle].append(range_m)
    averaged_data = [(angle, sum(ranges) / len(ranges)) for angle, ranges in angle_ranges.items()]
    averaged_data.sort()  # Сортировка по углу

    angles, ranges = zip(*averaged_data)

    plt.figure(figsize=(10, 6))
    plt.plot(angles, ranges, 'r-', label='Дальность полёта')
    plt.xlabel('Угол наклона (градусы)')
    plt.ylabel('Дальность полёта (м)')
    plt.title('Зависимость дальности полёта от угла наклона')
    plt.legend()
    plt.grid(True)
    plt.savefig('range_vs_angle.png')