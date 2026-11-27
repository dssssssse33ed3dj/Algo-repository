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


# 1. Перебор всех пар
def duplicate_pairs(numbers):
    for i in range(len(numbers)):
        for j in range(i + 1, len(numbers)):
            if equal(numbers[i], numbers[j]):
                return True
    return False

# 2. Множество: проверяем, встречалось ли число раньше
def duplicate_set(numbers):
    seen = set()
    for value in numbers:
        if value in seen:
            return True
        seen.add(value)
    return False

# 3. Словарь-счётчик
def duplicate_dict(numbers):
    counts = {}
    for value in numbers:
        counts[value] = counts.get(value, 0) + 1
        if counts[value] > 1:
            return True
    return False

# 4. Сортировка копии и проверка соседних элементов
def duplicate_sorted(numbers):
    copy = sorted(numbers)
    for i in range(1, len(copy)):
        if equal(copy[i - 1], copy[i]):
            return True
    return False

# 5. Сортировка копии методом sort
def duplicate_sort_copy(numbers):
    copy = numbers.copy()
    copy.sort()
    for i in range(1, len(copy)):
        if equal(copy[i - 1], copy[i]):
            return True
    return False

# 6. Проверка через list.count (простой, но медленный способ)
def duplicate_count(numbers):
    for value in numbers:
        if numbers.count(value) > 1:
            return True
    return False

# 7. Рекурсивное разбиение: проверяем половины и совпадения между ними
def duplicate_recursive(numbers):
    def check(part):
        if len(part) <= 1:
            return False
        middle = len(part) // 2
        left = part[:middle]
        right = part[middle:]
        if check(left) or check(right):
            return True
        left_values = set(left)
        for value in right:
            if value in left_values:
                return True
        return False
    return check(numbers)

# 8. Сортировка на месте (изменяет переданный список)
def duplicate_in_place(numbers):
    numbers.sort()
    for i in range(1, len(numbers)):
        if equal(numbers[i - 1], numbers[i]):
            return True
    return False

ALGORITHMS = [
    ("Перебор всех пар", duplicate_pairs),
    ("Множество set", duplicate_set),
    ("Словарь-счётчик", duplicate_dict),
    ("sorted() + соседи", duplicate_sorted),
    ("sort() копии + соседи", duplicate_sort_copy),
    ("list.count()", duplicate_count),
    ("Рекурсивное разделение", duplicate_recursive),
    ("Сортировка исходного списка", duplicate_in_place),
]

def expected(numbers):
    return len(numbers) != len(set(numbers))

def main():
    random.seed(42)
    small = [random.randint(0, 500) for _ in range(1000)]
    large = list(range(100000))
    special = list(range(99999)) + [0]

    examples = [([4, 9, 2, 9],), ([1, 2, 3],), ([7],), ([5, 5],)]
    check_examples(ALGORITHMS, examples, expected)

    # Для изменяющего вход алгоритма передаём отдельную копию при каждом запуске.
    safe_algorithms = []
    for name, function in ALGORITHMS:
        if function is duplicate_in_place:
            def wrapper(numbers, f=function):
                copy = numbers.copy()
                return f(copy)
            safe_algorithms.append((name, wrapper))
        else:
            safe_algorithms.append((name, function))

    show_results("ЗАДАНИЕ 02. ПОВТОР В СПИСКЕ", safe_algorithms, [
        ("1000 случайных чисел", (small,)),
        ("100000 разных чисел", (large,)),
        ("Повтор только в конце", (special,)),
    ], expected, slow_names=("Перебор всех пар", "list.count()", "Рекурсивное разделение"))

if __name__ == "__main__":
    main()
