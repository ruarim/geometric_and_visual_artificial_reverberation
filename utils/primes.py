import numpy as np
from sympy import nextprime, isprime

def calculate_log_range(center, percentage):
    offset = center * (percentage / 100)
    start = int(center - offset)
    end = int(center + offset)
    return start, end

def log_distributed_primes(center, percentage, count):
    start, end = calculate_log_range(center, percentage)
    # logarithmic spaced points
    log_points = np.logspace(np.log10(start), np.log10(end), count)
    
    primes = primes_in_range(count, log_points)
    
    return primes

def primes_in_range(count, points):
    primes = []
    seen = set()
    for point in points:
        prime = nextprime(int(point))
        while prime in seen:
            prime = nextprime(prime + 1)
        if isprime(prime):
            primes.append(prime)
            seen.add(prime)
        if len(primes) == count:
            break
        
    return primes

def is_mutually_prime(numbers):
    from math import gcd
    from itertools import combinations
    for a, b in combinations(numbers, 2):
        if gcd(a, b) != 1:
            return False
    return True

def find_log_mutual_primes(center, count, percentage=50):
    is_valid_set = False
    for p in range(percentage, 99):
        primes = log_distributed_primes(center, p, count)
        is_valid_set = (is_mutually_prime(primes) and len(primes) == count)
        
        if(is_valid_set): return primes
      
def find_closest_primes(points):
    primes = primes_in_range(len(points), points)
    return np.array(primes)
