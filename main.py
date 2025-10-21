import sys
import signal

from pynput import keyboard
from src.core.worker import stop_worker, work_in_process
from src.tasks import TASKS

signal.signal(signal.SIGINT, signal.SIG_DFL)


def auto_detect():
    for task in TASKS:
        if task.is_find():
            task.run()
            return

    print("无法识别当前页面，请切换到合成页面或使用迷幻药页面。")


if __name__ == "__main__":
    try:
        with keyboard.GlobalHotKeys(
            {"<f9>": work_in_process(auto_detect), "<f10>": stop_worker}
        ) as h:
            print("Press <f9> to start, <f10> to exit.")
            h.join()
    except KeyboardInterrupt:
        stop_worker()
        sys.exit(0)
