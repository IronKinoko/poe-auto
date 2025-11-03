import logging

_worker = None


def work_in_process(fn):
    from multiprocessing import Process

    def starter():
        global _worker
        tmp = Process(target=fn, daemon=True)
        if _worker and _worker.is_alive():
            logging.info("Worker is already running.")
            return _worker
        _worker = tmp
        _worker.start()

        return _worker

    return starter


def stop_worker():
    global _worker
    if _worker and _worker.is_alive():
        _worker.terminate()
        _worker.join(timeout=5)
        _worker = None
        logging.info("Worker process stopped.")
    else:
        logging.info("No worker process to stop.")
