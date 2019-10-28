from joblib import Parallel, delayed, cpu_count
import funcy as fp
from multiprocessing import Pool

# Functions for setting up parallelization and data streaming¶

def iter_series(series):
    extracted = 0
    for doc in series:
        yield doc
        extracted += 1

def pool_iter_series(series):
    pool = Pool()
    series = iter_series(series)
    pool.close()
    pool.join()
    return series

def pool_imap(function, generator):
    pool = Pool()
    result_generator = pool.imap(function, generator)
    pool.close()
    pool.join()
    return result_generator

def _series_chunks(s, n_jobs):
    if n_jobs < 0:
        # have n chunks if we are using all n cores/cpus = cpu_count() + 1 + n_jobs
        n_jobs = cpu_count() + 1 + n_jobs
    n = len(s)
    n_chunks = int(n / n_jobs)
    return (s.iloc[ilocs] for ilocs in fp.chunks(n_chunks, range(n)))

def series_pmap(s, f, n_jobs=-1):
    if n_jobs == 0:
        return s.map(f)
    return pd.concat(Parallel(n_jobs=n_jobs)(delayed(series_pmap)(sub_series, f, n_jobs=0) \
                                                 for sub_series in _series_chunks(s, n_jobs)))
