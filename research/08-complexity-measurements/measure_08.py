"""Задание 8. Замеры пяти функций на разных объёмах данных.

Запуск из корня репозитория:

    python research/08-complexity-measurements/measure_08.py

Программа печатает таблицу и сохраняет замеры в два файла рядом с собой:
results_08.csv (время от n) и results_08_k.csv (время от k при постоянном n).
Графики по этим файлам строит plot_08.py.

Напишите тела четырёх функций с пометкой TODO. Остальное уже готово.
"""

import csv
import random
from pathlib import Path
from statistics import median
from time import perf_counter

from algorithms_08 import (
    merge_intervals,
    unique_in_order_list,
    unique_in_order_set,
    window_sum_shift,
    window_sum_slices,
)

HERE = Path(__file__).parent
SIZES = [1_000, 2_000, 4_000, 8_000, 16_000]
K_SERIES_N = 10_000
K_SERIES = [1, 1_000, 2_500, 5_000, 7_500, 9_000, 10_000]
def make_numbers(n, seed=8):
    rng = random.Random(seed)
    return rng.sample(range(10 * n), n)


def measure_time(func, *args, repeats=5):
    times = []
    for _ in range(repeats):
        start = perf_counter()
        func(*args)
        end = perf_counter()
        times.append(end - start)
    return median(times)


def growth_ratios(times):
    return [times[i] / times[i - 1] for i in range(1, len(times))]


def measure_k_series(n, ks, repeats=3):
    nums = make_numbers(n)
    results = []
    for k in ks:
        seconds = measure_time(window_sum_slices, nums, k, repeats=repeats)
        results.append((k, seconds))
    return results

# Функции замера для каждой алгоритмической функции 

def measure_window_sum_slices(n):
    """Замер window_sum_slices. k = n // 2, чтобы увидеть квадратичный рост."""
    nums = make_numbers(n)
    k = n // 2
    return measure_time(window_sum_slices, nums, k)

def measure_window_sum_shift(n):
    """Замер window_sum_shift. k = n // 2, сложность не зависит от k."""
    nums = make_numbers(n)
    k = n // 2
    return measure_time(window_sum_shift, nums, k)

def measure_merge_intervals(n):
    """Замер merge_intervals. Генерируем n случайных интервалов."""
    rng = random.Random(8)
    intervals = []
    for _ in range(n):
        start = rng.randint(0, 10 * n)
        end = start + rng.randint(0, 100)  # длина от 0 до 100
        intervals.append([start, end])
    return measure_time(merge_intervals, intervals)

def measure_unique_in_order_list(n):
    """Замер unique_in_order_list. Данные уникальны (худший случай)."""
    items = make_numbers(n)
    return measure_time(unique_in_order_list, items)

def measure_unique_in_order_set(n):
    """Замер unique_in_order_set. Данные уникальны."""
    items = make_numbers(n)
    return measure_time(unique_in_order_set, items)

def main():
    funcs = [
        ("window_sum_slices", measure_window_sum_slices),
        ("window_sum_shift", measure_window_sum_shift),
        ("merge_intervals", measure_merge_intervals),
        ("unique_in_order_list", measure_unique_in_order_list),
        ("unique_in_order_set", measure_unique_in_order_set),
    ]

    results = {}
    for name, func in funcs:
        times = [func(n) for n in SIZES]
        results[name] = times

    # Сохранение в CSV (правильный формат для plot_08.py)
    with open(HERE / "results_08.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["function", "n", "seconds"])
        for name, _ in funcs:
            for i, n in enumerate(SIZES):
                writer.writerow([name, n, results[name][i]])

    # Замеры для графика 3
    k_results = measure_k_series(K_SERIES_N, K_SERIES)

    with open(HERE / "results_08_k.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["k", "seconds"])
        for k, t in k_results:
            writer.writerow([k, t])

    print("Готово: results_08.csv и results_08_k.csv сохранены в правильном формате.")
if __name__ == "__main__":
    main()