from multiprocessing import Pool, cpu_count
from typing import Iterable, Callable, Optional, Any

def run_in_pool(
    func: Callable,
    data_iter: Iterable[Any],
    init: Optional[Callable] = None,
    init_args: tuple = (),
    workers: Optional[int] = None,
    chunksize: int = 100,
):
    """
    Run a function in a multiprocessing pool and yield results.
    """
    with Pool(
        processes=workers or max(1, cpu_count()-1),
        initializer=init,
        initargs=init_args
    ) as pool:
        for result in pool.imap_unordered(func, data_iter, chunksize=chunksize):
            yield result
