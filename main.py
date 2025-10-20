import auto_use_delirium
import auto_merge
import auto_anjie
from pynput import keyboard
from utils import work_in_process, stop_worker, clean_dir
import sys
import signal

signal.signal(signal.SIGINT, signal.SIG_DFL)

clean_dir("tmp")


def auto_detect():
    if auto_merge.is_find():
        auto_merge.start()
    elif auto_use_delirium.is_find():
        auto_use_delirium.start()
    elif auto_anjie.is_find():
        auto_anjie.start()
    else:
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
