import sys, threading
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=1000)

def fib_ref(n):
    if n <= 1:
        return n

    return fib_ref(n-1) + fib_ref(n-2)

def fib_futures(n):
    if n <= 1:
        return n

    future_n1 = executor.submit(fib_futures, n-1)
    future_n2 = executor.submit(fib_futures, n-2)
    print "Active threads: ", threading.active_count()
    return future_n1.result() + future_n2.result()

if __name__ == '__main__':
    n = int(sys.argv[1])
    print "Reference: ", fib_ref(n)

    res = fib_futures(n)
    print "Futures: ", res

