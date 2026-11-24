"""Домашнее задание № 5. Скользящее окно фиксированного размера.

Заполните тела функций. Проверка из корня репозитория:

    pytest practice/05-fixed-sliding-window -q
"""


def step_score(steps, k, lower, upper):
    """Задача 1. Очки фитнес-браслета (LeetCode 1176)."""
    n = len(steps)
    if n < k:
        return 0
        

    current_sum = sum(steps[:k])
    score = 0
    
    if current_sum < lower:
        score -= 1
    elif current_sum > upper:
        score += 1
        
    for i in range(k, n):
        current_sum += steps[i] - steps[i - k]
        if current_sum < lower:
            score -= 1
        elif current_sum > upper:
            score += 1
            
    return score


def decrypt(code, k):
    """Задача 2. Кодовый замок (LeetCode 1652)."""
    n = len(code)
    if k == 0:
        return [0] * n
        
    res = [0] * n
    
    if k > 0:
        window_sum = sum(code[1:k+1])
        for i in range(n):
            res[i] = window_sum
            window_sum -= code[(i + 1) % n]
            window_sum += code[(i + k + 1) % n]
    else:
        K = -k
        window_sum = sum(code[n-K:])
        for i in range(n):
            res[i] = window_sum
            window_sum -= code[(i - K) % n]
            window_sum += code[i % n]
            
    return res