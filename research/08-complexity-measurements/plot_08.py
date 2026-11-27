"""Задание 8. Графики по замерам из measure_08.py.

Запуск из корня репозитория, после measure_08.py:

    python research/08-complexity-measurements/plot_08.py

Картинки сохраняются в lesson_08/screens/ поверх заглушек.
График 1 уже готов. Графики 2 и 3 постройте по его образцу.
"""

import csv
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt

HERE = Path(__file__).parent
SCREENS = HERE / "screens"


def read_results():
    """Прочитать results_08.csv: {имя функции: ([n, ...], [секунды, ...])}."""
    series = defaultdict(lambda: ([], []))
    with open(HERE / "results_08.csv", encoding="utf-8") as file:
        for row in csv.DictReader(file):
            sizes, times = series[row["function"]]
            sizes.append(int(row["n"]))
            times.append(float(row["seconds"]))
    return series


def read_k_results():
    """Прочитать results_08_k.csv: ([k, ...], [секунды, ...])."""
    ks, times = [], []
    with open(HERE / "results_08_k.csv", encoding="utf-8") as file:
        for row in csv.DictReader(file):
            ks.append(int(row["k"]))
            times.append(float(row["seconds"]))
    return ks, times


def plot_linear(series):
    """График 1: время от n на обычных осях. Образец для графиков 2 и 3."""
    fig, ax = plt.subplots(figsize=(10, 6))
    for name, (sizes, times) in series.items():
        ax.plot(sizes, times, marker="o", label=name)
    ax.set_title("Время от размера входа")
    ax.set_xlabel("n, элементов")
    ax.set_ylabel("время, с")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.savefig(SCREENS / "01-lineinyi.png", dpi=120, bbox_inches="tight")
    plt.close(fig)

def plot_log_log(series):
    fig, ax = plt.subplots(figsize=(10, 6))
    for name, (sizes, times) in series.items():
        ax.plot(sizes, times, marker="o", label=name)
    
    ax.set_xscale("log")
    ax.set_yscale("log")
    
    ax.set_title("Время от размера входа (лог-лог)")
    ax.set_xlabel("n, элементов (log)")
    ax.set_ylabel("время, с (log)")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.savefig(SCREENS / "02-log-log.png", dpi=120, bbox_inches="tight")
    plt.close(fig)


def plot_k(ks, times):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(ks, times, marker="o", color="purple")
    
    ax.set_title("Время window_sum_slices от k")
    ax.set_xlabel("k, длина окна")
    ax.set_ylabel("время, с")
    ax.grid(True, alpha=0.3)
    fig.savefig(SCREENS / "03-ot-k.png", dpi=120, bbox_inches="tight")
    plt.close(fig)

if __name__ == "__main__":
    # Читаем данные
    series = read_results()
    ks, times = read_k_results()
    
    # Строим и сохраняем графики
    plot_linear(series)
    plot_log_log(series)
    plot_k(ks, times)
    
    print("Все 3 графика сохранены в папку screens")