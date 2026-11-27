import random
import time
import tracemalloc
from statistics import median

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


# 1. Сравнение с уже найденными уникальными значениями
def distinct_list(numbers):
    unique = []
    for value in numbers:
        if value not in unique:
            unique.append(value)
    return len(unique)

# 2. Множество
def distinct_set(numbers):
    return len(set(numbers))

# 3. Словарь
def distinct_dict(numbers):
    counts = {}
    for value in numbers:
        counts[value] = 1
    return len(counts)

# 4. Сортировка копии и подсчёт переходов
def distinct_sorted(numbers):
    data = sorted(numbers)
    if not data:
        return 0
    count = 1
    for i in range(1, len(data)):
        if not equal(data[i], data[i - 1]):
            count += 1
    return count

# 5. Сортировка копии методом sort
def distinct_sort_copy(numbers):
    data = numbers.copy()
    data.sort()
    if not data:
        return 0
    count = 1
    for i in range(1, len(data)):
        if data[i] != data[i - 1]:
            count += 1
    return count

# 6. Частотный словарь
def distinct_frequency(numbers):
    frequency = {}
    for value in numbers:
        frequency[value] = frequency.get(value, 0) + 1
    return len(frequency)

# 7. Булев массив для диапазона значений
def distinct_boolean_array(numbers):
    if not numbers:
        return 0
    low = min(numbers)
    high = max(numbers)
    seen = [False] * (high - low + 1)
    count = 0
    for value in numbers:
        index = value - low
        if not seen[index]:
            seen[index] = True
            count += 1
    return count

# 8. Перебор уникальных значений через последовательную проверку
def distinct_count_scan(numbers):
    count = 0
    for i in range(len(numbers)):
        found_before = False
        for j in range(i):
            if equal(numbers[i], numbers[j]):
                found_before = True
                break
        if not found_before:
            count += 1
    return count

ALGORITHMS = [
    ("Список уникальных значений", distinct_list),
    ("Множество set", distinct_set),
    ("Словарь", distinct_dict),
    ("sorted() + подсчёт переходов", distinct_sorted),
    ("sort() копии + переходы", distinct_sort_copy),
    ("Словарь частот", distinct_frequency),
    ("Булев массив по диапазону", distinct_boolean_array),
    ("Проверка предыдущих элементов", distinct_count_scan),
]

def expected(numbers):
    return len(set(numbers))

def main():
    random.seed(42)
    small = [random.randint(-500, 500) for _ in range(1000)]
    large = [random.randint(-100000, 100000) for _ in range(100000)]
    special = [random.randint(0, 99) for _ in range(100000)]

    check_examples(ALGORITHMS, [([5, 2, 5, 5, 9, 2],), ([1, 2, 3],), ([7, 7, 7],), ([],)], expected)
    show_results("ЗАДАНИЕ 04. КОЛИЧЕСТВО РАЗНЫХ ЧИСЕЛ", ALGORITHMS, [
        ("1000 случайных чисел", (small,)),
        ("100000 случайных чисел", (large,)),
        ("100000 чисел от 0 до 99", (special,)),
    ], expected, slow_names=("Список уникальных значений", "Проверка предыдущих элементов"))

if __name__ == "__main__":
    main()
