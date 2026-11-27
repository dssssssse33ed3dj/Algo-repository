import bisect

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


# 1. Перебор элементов первого списка и проверка во втором
def common_nested(left, right):
    result = []
    for value in left:
        if value in right and value not in result:
            result.append(value)
    return sorted(result)

# 2. Пересечение множеств
def common_sets(left, right):
    return sorted(set(left) & set(right))

# 3. Словарь для второго списка
def common_dict(left, right):
    available = {}
    for value in right:
        available[value] = True
    result = set()
    for value in left:
        if value in available:
            result.add(value)
    return sorted(result)

# 4. Два указателя для отсортированных копий
def common_two_pointers(left, right):
    a = sorted(left)
    b = sorted(right)
    i = j = 0
    result = []
    while i < len(a) and j < len(b):
        if a[i] == b[j]:
            if not result or result[-1] != a[i]:
                result.append(a[i])
            i += 1
            j += 1
        elif a[i] < b[j]:
            i += 1
        else:
            j += 1
    return result

# 5. Бинарный поиск каждого уникального элемента
def common_binary_search(left, right):
    data = sorted(set(right))
    result = []
    for value in set(left):
        position = bisect.bisect_left(data, value)
        if position < len(data) and data[position] == value:
            result.append(value)
    return sorted(result)

# 6. Сортировка объединённого списка и подсчёт соседних групп
def common_merge_sort(left, right):
    a = sorted(left)
    b = sorted(right)
    result = []
    i = j = 0
    while i < len(a) and j < len(b):
        if a[i] == b[j]:
            value = a[i]
            if not result or result[-1] != value:
                result.append(value)
            while i < len(a) and a[i] == value:
                i += 1
            while j < len(b) and b[j] == value:
                j += 1
        elif a[i] < b[j]:
            i += 1
        else:
            j += 1
    return result

# 7. Частотный словарь с отметкой общих значений
def common_frequency(left, right):
    counts = {}
    for value in left:
        counts[value] = 1
    result = set()
    for value in right:
        if value in counts:
            result.add(value)
    return sorted(result)

# 8. Последовательный поиск с удалением найденного значения из множества
def common_remove(left, right):
    remaining = set(right)
    result = set()
    for value in left:
        if value in remaining:
            result.add(value)
            remaining.remove(value)
    return sorted(result)

ALGORITHMS = [
    ("Вложенный перебор", common_nested),
    ("Пересечение множеств", common_sets),
    ("Словарь для правого списка", common_dict),
    ("Два указателя", common_two_pointers),
    ("Бинарный поиск", common_binary_search),
    ("Слияние отсортированных списков", common_merge_sort),
    ("Словарь общих значений", common_frequency),
    ("Множество с удалением", common_remove),
]

def expected(left, right):
    return sorted(set(left) & set(right))

def main():
    random.seed(42)
    left_small = [random.randint(0, 1500) for _ in range(1000)]
    right_small = [random.randint(0, 1500) for _ in range(1000)]
    left_large = [random.randint(0, 150000) for _ in range(100000)]
    right_large = [random.randint(0, 150000) for _ in range(100000)]
    left_special = list(range(100000))
    right_special = list(range(50000, 150000))

    check_examples(ALGORITHMS, [
        ([1, 2, 2, 4], [2, 2, 3]),
        ([1, 3, 5], [2, 4, 6]),
        ([], [1, 2]),
    ], expected)

    show_results("ЗАДАНИЕ 05. ОБЩИЕ ЧИСЛА ДВУХ СПИСКОВ", ALGORITHMS, [
        ("Два списка по 1000 чисел", (left_small, right_small)),
        ("Два списка по 100000 чисел", (left_large, right_large)),
        ("Два отсортированных списка по 100000", (left_special, right_special)),
    ], expected, slow_names=("Вложенный перебор",))

if __name__ == "__main__":
    main()
