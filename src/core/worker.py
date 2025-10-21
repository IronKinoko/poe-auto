_worker = None


def work_in_process(fn):
    from multiprocessing import Process

    def starter():
        global _worker
        tmp = Process(target=fn, daemon=True)
        if _worker and _worker.is_alive():
            print("Worker is already running.")
            return
        _worker = tmp
        _worker.start()

    return starter


def stop_worker():
    global _worker
    if _worker and _worker.is_alive():
        _worker.terminate()
        _worker.join(timeout=5)
        _worker = None
        print("Worker process stopped.")
    else:
        print("No worker process to stop.")