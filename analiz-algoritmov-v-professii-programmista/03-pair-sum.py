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


# 1. Перебор всех пар
def pair_bruteforce(numbers, target):
    for i in range(len(numbers)):
        for j in range(i + 1, len(numbers)):
            if numbers[i] + numbers[j] == target:
                return True
    return False

# 2. Множество уже просмотренных чисел
def pair_set(numbers, target):
    seen = set()
    for value in numbers:
        if target - value in seen:
            return True
        seen.add(value)
    return False

# 3. Словарь количества чисел
def pair_dict(numbers, target):
    counts = {}
    for value in numbers:
        other = target - value
        if counts.get(other, 0) > 0:
            return True
        counts[value] = counts.get(value, 0) + 1
    return False

# 4. Сортировка копии + два указателя
def pair_two_pointers(numbers, target):
    data = sorted(numbers)
    left, right = 0, len(data) - 1
    while left < right:
        total = data[left] + data[right]
        if total == target:
            return True
        if total < target:
            left += 1
        else:
            right -= 1
    return False

# 5. Бинарный поиск дополнения для каждого элемента
def pair_binary_search(numbers, target):
    data = sorted(numbers)
    for i, value in enumerate(data):
        needed = target - value
        position = bisect.bisect_left(data, needed, i + 1)
        if position < len(data) and data[position] == needed:
            return True
    return False

# 6. Частотный словарь, построенный заранее
def pair_frequency(numbers, target):
    counts = {}
    for value in numbers:
        counts[value] = counts.get(value, 0) + 1
    for value, count in counts.items():
        needed = target - value
        if needed in counts:
            if needed != value or count >= 2:
                return True
    return False

# 7. Сортировка исходного списка + два указателя
def pair_sort_in_place(numbers, target):
    numbers.sort()
    left, right = 0, len(numbers) - 1
    while left < right:
        total = numbers[left] + numbers[right]
        if total == target:
            return True
        if total < target:
            left += 1
        else:
            right -= 1
    return False

# 8. Рекурсивный перебор пар
def pair_recursive(numbers, target):
    def search(start, end):
        # В маленьком участке проверяем пары обычными циклами.
        if end - start <= 1:
            for i in range(start, end):
                for j in range(i + 1, end):
                    if numbers[i] + numbers[j] == target:
                        return True
            return False

        middle = (start + end) // 2

        # Сначала проверяем пары внутри каждой половины.
        if search(start, middle):
            return True
        if search(middle, end):
            return True

        # Затем проверяем пары, где один элемент в каждой половине.
        for i in range(start, middle):
            for j in range(middle, end):
                if numbers[i] + numbers[j] == target:
                    return True
        return False

    return search(0, len(numbers))

ALGORITHMS = [
    ("Перебор всех пар", pair_bruteforce),
    ("Множество дополнений", pair_set),
    ("Словарь за один проход", pair_dict),
    ("Два указателя после сортировки", pair_two_pointers),
    ("Бинарный поиск дополнения", pair_binary_search),
    ("Частотный словарь", pair_frequency),
    ("Сортировка входа + указатели", pair_sort_in_place),
    ("Рекурсивный перебор", pair_recursive),
]

def expected(numbers, target):
    seen = set()
    for value in numbers:
        if target - value in seen:
            return True
        seen.add(value)
    return False

def main():
    random.seed(42)
    small = [random.randint(-500, 500) for _ in range(1000)]
    large = [random.randint(-100000, 100000) for _ in range(100000)]
    special = list(range(99998)) + [500000, 700000]
    target_special = 1200000

    examples = [([2, 7, 11, 15], 9), ([1, 2, 3], 20), ([3, 3], 6), ([1], 2)]
    check_examples(ALGORITHMS, examples, expected)

    safe_algorithms = []
    for name, function in ALGORITHMS:
        if function is pair_sort_in_place:
            def wrapper(numbers, target, f=function):
                copy = numbers.copy()
                return f(copy, target)
            safe_algorithms.append((name, wrapper))
        else:
            safe_algorithms.append((name, function))

    show_results("ЗАДАНИЕ 03. ПАРА С ЗАДАННОЙ СУММОЙ", safe_algorithms, [
        ("1000 случайных чисел", (small, 500)),
        ("100000 случайных чисел", (large, 123456)),
        ("Подходящая пара в конце", (special, target_special)),
    ], expected, slow_names=("Перебор всех пар", "Рекурсивный перебор"))

if __name__ == "__main__":
    main()
