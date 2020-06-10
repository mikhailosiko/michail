from _operator import mod
import sys
import numpy as np
from itertools import islice
from sympy import primerange
# for test:
from time import perf_counter_ns

# /////////////////////////// extremely slow but interesting to learn how coroutines work
sys.setrecursionlimit(10**4)

def sieve():
    """
    eternal prime numbers generator
    it's lazy recursion - number of levels = number of prime numbers
    """
    #print("Entering sieve")
    pn = start = yield
    primes = sieve()
    next(primes)         # initialize coroutin
    while True:
        n = (yield pn)
        if n and mod(n, start):        # we can get nothing in yield
            primes.send(n)
            pn = next(primes)
        #else:
        #    pn = -1    # I didn't find out how to skip yield here

def eratosthenes_generator(upper_bound):
    primes = sieve()
    next(primes)     # initialize coroutin
    i = 3
    primes.send(i)   # send initial value
    yield 2
    prev_n = 0
    for n in primes:
        i += 2
        primes.send(i)
        if n > upper_bound:
            primes.close()
            return
        if n != prev_n:
            yield n
            prev_n = n    # I didn't find out how to skip yield in sieve
# ///////////////////////////            
            
            

# /////////////////////  numpy version - the best:
"""  mod is bad idea, slicing is better
def numpy_eratosthenes(upper_bound):
    numbers = np.array(list(range(3, upper_bound, 2)))
    numbers2 = numbers.copy()
    mask = numbers != 0
    n = 3
    yield 2
    while True:
        np.mod(numbers, n, out=numbers2)
        mask &= numbers2 != 0
        #print(mask)
        yield n
        numbers = numbers[1:]
        mask = mask[1:]
        numbers2 = numbers2[1:]
        #print(numbers[mask])
        if not len(numbers[mask]): return
        n = numbers[mask][0]
        #np.argmax(myArray > 0)    first non zero
"""

def numpy_eratosthenes(upper_bound):   # with slicing
    p = 5
    max_p = int(upper_bound ** 0.5)    # it's faster than check p * p in cycle
    upper_bound += 1
    all_numbers = np.array(list(range(upper_bound)), dtype=np.bool)
    all_numbers[0] = False
    all_numbers[1] = False
    all_numbers[4: upper_bound: 2] = False
    all_numbers[9: upper_bound: 3] = False

    while p <= max_p:
        all_numbers[p * p: upper_bound: p] = False        
        p = np.nonzero(all_numbers[p + 1: 2 * p - 2])[0][0] + p + 1    # Bertrand's postulate  n<p<2n-2  if n > 3
        # numpy lack of find first  https://github.com/numpy/numpy/issues/2269

    yield from np.nonzero(all_numbers)[0]
# ///////////////////////////                



# /////////////////////  my simple version :
def my_eratosthenes(upper_bound):
    upper_bound += 1
    p = 3
    max_p = int(upper_bound ** 0.5)    # it's faster than check p * p in cycle
    all_numbers = [True] * upper_bound  # list(range(upper_bound))
    all_numbers[0] = False
    all_numbers[1] = False
    for i in range(4, upper_bound, 2): all_numbers[i] = False
    #print("max p ", max_p)
    while p <= max_p:
        #print(p)
        for i in range(p*p, upper_bound, p): all_numbers[i] = False
        for i in range(p + 1, upper_bound):
            if all_numbers[i]:
                p = i
                break
        #p = next(filter(lambda x: x, islice(all_numbers, p + 1, upper_bound)))   # doesn't work for bool array  
    #return filter(lambda n: n, all_numbers)                                      # doesn't work for bool array 
    for i in range(upper_bound):
        if all_numbers[i]: yield i
# ///////////////////////////            



# /////////////////////  my new generator stream version  :
# idea: generate the stream of odd numbers and then sift it without memory consuption
# try 2

#def sieve2():

#def eratosthenes_generator2(upper_bound):
    #prime_numbers_flow = {}
#    upper_bound += 1
#    p = 3
#    max_p = int(upper_bound ** 0.5)    # it's faster than check p * p in cycle
# ///////////////////////////            



#  //////////////// version from internet:
# Python program to print all primes smaller than or equal to
# n using Sieve of Eratosthenes
#Time complexity : O(n*log(log(n)))

def SieveOfEratosthenes_from_internet(n):
    # Create a boolean array "prime[0..n]" and initialize
    #  all entries it as true. A value in prime[i] will
    # finally be false if i is Not a prime, else true.
    prime = [True for i in range(n+1)]
    p = 2
    while (p * p <= n):

        # If prime[p] is not changed, then it is a prime
        if (prime[p] == True):

            # Update all multiples of p
            for i in range(p * p, n+1, p):
                prime[i] = False
        p += 1

    # Print all prime numbers
    for p in range(2, n+1):
        if prime[p]:
            yield p   # was print
# ///////////////////////////            



test = 19997
#test = 500000

if test < 21000:
    start_time = perf_counter_ns()
    result = list(eratosthenes_generator(test))
    print(f"My generator version ms: {(perf_counter_ns() - start_time)/10e6}")
    print(result)

start_time = perf_counter_ns()
result = list(SieveOfEratosthenes_from_internet(test))
print(f"version from internet ms: {(perf_counter_ns() - start_time)/10e6}")
if test < 500000: print(result)

start_time = perf_counter_ns()
result = list(numpy_eratosthenes(test))
print(f"my numpy ms: {(perf_counter_ns() - start_time)/10e6}")
if test < 500000: print(result)

start_time = perf_counter_ns()
result = list(my_eratosthenes(test))
print(f"my Eratosthenes ms: {(perf_counter_ns() - start_time)/10e6}")
if test < 500000: print(result)

start_time = perf_counter_ns()
result = list(primerange(0, test+1))
print(f"sympy prime range ms: {(perf_counter_ns() - start_time)/10e6}")
if test < 500000: print(list(result))
