import hashlib
import random

# LCG Generator
def generate_lcg_sequence(seed, a, c, m, length):
    sequence = [seed]
    for _ in range(length - 1):
        next_val = (a * sequence[-1] + c) % m
        sequence.append(next_val)
    return sequence

# PRNG Generator (عشوائي)
def generate_prng_sequence(seed, length):
    random.seed(seed)
    return [random.uniform(1.0, 35.0) for _ in range(length)]

# Hash-based Generator
def generate_hash_sequence(seed, length):
    sequence = []
    current = str(seed)
    for _ in range(length):
        hashed = hashlib.sha256(current.encode()).hexdigest()
        num = int(hashed[:8], 16) % 3500 / 100  # تحويل إلى رقم بين 0 و 35 تقريبًا
        sequence.append(round(max(1.0, min(num, 35.0)), 2))  # تقيده بين 1 و 35
        current = hashed  # استخدم التجزئة كمدخل للجولة التالية
    return sequence
