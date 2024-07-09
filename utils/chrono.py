import time

def chrono(f, *args, **kwargs):
    """
    A short helper function to measure running time
    
    Usage:
        runtime_foo, result_foo = chrono(foo(bar))
    """
    t = time.perf_counter()
    ret = f(*args, **kwargs)
    runtime = time.perf_counter() - t
    return runtime, ret