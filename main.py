from auto_merge import auto_merge_delirium
from pynput import keyboard
from utils import work_in_process, stop_worker
import sys
import signal

signal.signal(signal.SIGINT, signal.SIG_DFL)

if __name__ == "__main__":
    try:
        with keyboard.GlobalHotKeys(
            {"<f9>": work_in_process(auto_merge_delirium), "<f10>": stop_worker}
        ) as h:
            print("Press <f9> to start, <f10> to exit.")
            h.join()
    except KeyboardInterrupt:
        stop_worker()
        sys.exit(0)
