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


# 1. Формула суммы: сумма полного диапазона минус сумма списка
def missing_sum(ids, n):
    return n * (n + 1) // 2 - sum(ids)

# 2. XOR: одинаковые числа взаимно уничтожаются
def missing_xor(ids, n):
    result = 0
    for value in range(n + 1):
        result ^= value
    for value in ids:
        result ^= value
    return result

# 3. Множество
def missing_set(ids, n):
    values = set(ids)
    for value in range(n + 1):
        if value not in values:
            return value

# 4. Булев массив
def missing_boolean(ids, n):
    seen = [False] * (n + 1)
    for value in ids:
        seen[value] = True
    for value in range(n + 1):
        if not seen[value]:
            return value

# 5. Байтовый массив: один байт на отметку
def missing_bytearray(ids, n):
    seen = bytearray(n + 1)
    for value in ids:
        seen[value] = 1
    for value in range(n + 1):
        if seen[value] == 0:
            return value

# 6. Сортировка копии и поиск разрыва
def missing_sorted(ids, n):
    data = sorted(ids)
    for index, value in enumerate(data):
        if index != value:
            return index
    return n

# 7. Размещение каждого числа на позицию с таким же индексом
# Функция изменяет список, поэтому в измерениях ей передаётся копия.
def missing_cyclic(ids, n):
    index = 0
    while index < len(ids):
        value = ids[index]
        if value < len(ids) and ids[index] != ids[value]:
            ids[index], ids[value] = ids[value], ids[index]
        else:
            index += 1
    for index, value in enumerate(ids):
        if index != value:
            return index
    return n

# 8. Бинарный поиск пропуска после сортировки
def missing_binary(ids, n):
    data = sorted(ids)
    left, right = 0, len(data)
    while left < right:
        middle = (left + right) // 2
        if data[middle] == middle:
            left = middle + 1
        else:
            right = middle
    return left

ALGORITHMS = [
    ("Формула суммы", missing_sum),
    ("Операция XOR", missing_xor),
    ("Множество", missing_set),
    ("Булев массив", missing_boolean),
    ("Байтовый массив", missing_bytearray),
    ("Сортировка + поиск разрыва", missing_sorted),
    ("Циклическое размещение", missing_cyclic),
    ("Бинарный поиск после сортировки", missing_binary),
]

def expected(ids, n):
    return n * (n + 1) // 2 - sum(ids)

def main():
    random.seed(42)

    def make_case(n, missing):
        values = [value for value in range(n + 1) if value != missing]
        random.shuffle(values)
        return values

    small = make_case(1000, 500)
    large = make_case(100000, 0)
    special = make_case(100000, 0)

    check_examples(ALGORITHMS, [
        ([3, 0, 1], 3),
        ([0, 1], 2),
        ([1], 1),
        ([], 0),
    ], expected)

    # Для циклического размещения создаём копию, чтобы входные данные
    # оставались одинаковыми для каждого запуска.
    safe_algorithms = []
    for name, function in ALGORITHMS:
        if function is missing_cyclic:
            def wrapper(ids, n, f=function):
                return f(ids.copy(), n)
            safe_algorithms.append((name, wrapper))
        else:
            safe_algorithms.append((name, function))

    show_results("ЗАДАНИЕ 06. ПРОПУЩЕННЫЙ НОМЕР", safe_algorithms, [
        ("n=1000, список перемешан", (small, 1000)),
        ("n=100000, список перемешан", (large, 100000)),
        ("n=100000, пропуск в начале", (special, 100000)),
    ], expected)

if __name__ == "__main__":
    main()
