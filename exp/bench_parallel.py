import time
import threading
from multiprocessing import Process
from concurrent.futures import ProcessPoolExecutor

#report: multithreading = sequential. 1-8 reps requires the same time for multiprocessing (due to 8 cores
# supposedly), which is equal to 1 repetition of sequential. Multiprocessing has an additional overhead of ~ 0.15
# secs for forking.

def timer(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} Time: {end - start:.6f} seconds")
        if len(args) > 0:
            print(f"args: {args}")
        if len(kwargs) > 0:
            print(f"kwargs: {kwargs}")
        print("====================================================")
        return result
    return wrapper

def job_power():
    base = 1.000_000_000_1
    result = 1
    for _ in range(100_000_00):
        result *= base
    # print(result)
    return result

def job_add(a):
    for i in range(30000000):
        a[0] += 1


def job_power_param(k):
    return job_power()

@timer
def sequential(job, *args, rep=8):
    for i in range(rep):
        job(*args)

@timer
def multithreading(job, *args, rep=8):
    threads = []
    for i in range(rep):
        thread = threading.Thread(target=job, args=args)
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()


@timer
def multiprocessing(job, *args, rep=8):
    processes = []
    for i in range(rep):
        p = Process(target=job, args=args)
        processes.append(p)
        p.start()
    for p in processes:
        p.join()

@timer
def concurrentfuture(job, rep=8):
    with ProcessPoolExecutor() as executor:
        results = list(executor.map(job, [0 for i in range(rep)]))
    # print("results:", results)

if __name__ == '__main__':
    # sequential_param(job_power, rep=32) #12s with rep == 32
    # multithreading(job_power, rep=32) #same with sequential
    # multiprocessing(job_power, rep=32) #2s with rep == 32, 0.5s with rep <= 8
    # concurrentfuture(job_power_param, rep=32) #1.7s with rep == 32
    a = [0]
    sequential(job_add, a, rep = 32)
    print(a)
    a = [0]
    multithreading(job_add, a, rep = 32)
    print(a)
    a = [0]
    multiprocessing(job_add, a, rep = 32)
    print(a)
