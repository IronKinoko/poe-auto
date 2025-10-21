import os
import time
import functools
import sys
from pathlib import Path

DEBUG = "--debug" in sys.argv


def time_it(log_fn=print):
    def deco(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            t0 = time.perf_counter()
            res = func(*args, **kwargs)
            t1 = time.perf_counter()
            if DEBUG:
                log_fn(f"{func.__name__} took {t1-t0:.6f}s")
            return res

        return wrapper

    return deco


def ensure_dir(path):
    d = os.path.dirname(path)
    if d and not os.path.exists(d):
        os.makedirs(d, exist_ok=True)


def clean_dir(path):
    import shutil

    if os.path.exists(path) and os.path.isdir(path):
        shutil.rmtree(path)


def until(fn, check_interval=0.1, timeout=10.0):
    start_time = time.time()
    while True:
        res = fn()
        if res:
            return res
        if time.time() - start_time > timeout:
            return None
        time.sleep(check_interval)


_PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()


def project_path(*paths):
    """
    返回相对于项目根目录的绝对路径
    示例：project_path("assets", "img.png")
         或 project_path("/assets/img.png")
    """
    # 去掉开头的斜杠，统一处理
    clean_paths = [str(p).lstrip("/") for p in paths]
    return str(_PROJECT_ROOT.joinpath(*clean_paths))


def load_img(path):
    from PIL import Image

    return Image.open(project_path(path)).convert("RGB")
