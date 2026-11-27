import heapq
from functools import reduce

import random
import time
import tracemalloc
from statistics import median

# Счётчик явных сравнений. Встроенные функции Python выполняют часть
# сравнений внутри C-кода, поэтому их внутреннее число здесь не видно.
OPERATIONS = 0

def reset_operations():
    global OPERATIONS
    OPERATIONS = 0

def compare(a, b):
    global OPERATIONS
    OPERATIONS += 1
    return a < b

def equal(a, b):
    global OPERATIONS
    OPERATIONS += 1
    return a == b

def measure(function, args, repeats=3):
    times = []
    peaks = []
    result = None

    for _ in range(repeats):
        tracemalloc.start()
        start = time.perf_counter()
        result = function(*args)
        times.append((time.perf_counter() - start) * 1000)
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        peaks.append(peak / 1024)

    return result, median(times), max(peaks)

def show_results(title, algorithms, datasets, expected_function, slow_names=()):
    print("\\n" + "=" * 100)
    print(title)
    print("=" * 100)

    for data_name, args in datasets:
        expected = expected_function(*args)
        size = sum(len(x) for x in args if isinstance(x, list))
        print(f"\\nНабор: {data_name}; размер входа: {size}")
        print(f"{'Алгоритм':<31} {'Время, мс':>12} {'Пик памяти, КБ':>17} {'Проверки':>15}")
        print("-" * 82)

        for name, function in algorithms:
            if size > 5000 and name in slow_names:
                print(f"{name:<31} {'пропущен':>12} {'—':>17} {'—':>15}")
                continue

            reset_operations()
            result, elapsed, memory = measure(function, args)
            operations = OPERATIONS // 3  # три одинаковых запуска; выводим число за один запуск
            if result != expected:
                raise AssertionError(
                    f"{name}: результат {result!r}, ожидался {expected!r}"
                )
            operation_text = str(operations) if operations else "не считается"
            print(f"{name:<31} {elapsed:>12.3f} {memory:>17.2f} {operation_text:>15}")

def check_examples(algorithms, examples, expected_function):
    print("ПРОВЕРКА ОБЩИХ ТЕСТОВ")
    for example in examples:
        expected = expected_function(*example)
        for name, function in algorithms:
            actual = function(*example)
            if actual != expected:
                raise AssertionError(
                    f"{name}: для {example!r} получено {actual!r}, ожидалось {expected!r}"
                )
    print("Все алгоритмы прошли общие тесты.\\n")


# 1. Обычный линейный поиск
def minimum_linear(numbers):
    result = numbers[0]
    for index in range(1, len(numbers)):
        value = numbers[index]
        if compare(value, result):
            result = value
    return result

# 2. Встроенная функция min
def minimum_builtin(numbers):
    return min(numbers)

# 3. Сортировка копии
def minimum_sorted(numbers):
    return sorted(numbers)[0]

# 4. Сортировка отдельной копии методом sort
def minimum_sort_copy(numbers):
    copy = numbers.copy()
    copy.sort()
    return copy[0]

# 5. Рекурсивное разделение списка на половины
def minimum_recursive(numbers):
    def search(left, right):
        if left == right:
            return numbers[left]
        middle = (left + right) // 2
        a = search(left, middle)
        b = search(middle + 1, right)
        return a if compare(a, b) else b
    return search(0, len(numbers) - 1)

# 6. Попарное сравнение
def minimum_pairwise(numbers):
    result = numbers[0]
    index = 1
    while index < len(numbers):
        if index + 1 < len(numbers):
            smaller = numbers[index] if compare(numbers[index], numbers[index + 1]) else numbers[index + 1]
            if compare(smaller, result):
                result = smaller
            index += 2
        else:
            if compare(numbers[index], result):
                result = numbers[index]
            index += 1
    return result

# 7. Мини-куча
def minimum_heap(numbers):
    heap = numbers.copy()
    heapq.heapify(heap)
    return heap[0]

# 8. Поиск через reduce: накопление текущего минимума
def minimum_reduce(numbers):
    def choose(a, b):
        return a if compare(a, b) else b
    return reduce(choose, numbers)

ALGORITHMS = [
    ("Линейный поиск", minimum_linear),
    ("Встроенная min()", minimum_builtin),
    ("sorted() и первый элемент", minimum_sorted),
    ("sort() копии", minimum_sort_copy),
    ("Рекурсивное разделение", minimum_recursive),
    ("Попарное сравнение", minimum_pairwise),
    ("Построение мини-кучи", minimum_heap),
    ("Накопление через reduce()", minimum_reduce),
]

def expected(numbers):
    return min(numbers)

def main():
    random.seed(42)
    small = [random.randint(-100000, 100000) for _ in range(1000)]
    large = [random.randint(-1000000, 1000000) for _ in range(100000)]
    special = [random.randint(1, 1000000) for _ in range(99999)] + [-1000001]

    check_examples(ALGORITHMS, [([8, 3, 11, -2, 5],), ([0],), ([-5, -2, -9],)], expected)
    show_results("ЗАДАНИЕ 01. МИНИМАЛЬНОЕ ЧИСЛО", ALGORITHMS, [
        ("1000 случайных чисел", (small,)),
        ("100000 случайных чисел", (large,)),
        ("100000 чисел, минимум в конце", (special,)),
    ], expected)

if __name__ == "__main__":
    main()
