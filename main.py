import sys
import signal
import logging
import threading

from pynput import keyboard
from src.core.worker import stop_worker, work_in_process
from src.tasks import TASKS
from src.utils.common import init_logs
import src.core.region_selector as region_selector

signal.signal(signal.SIGINT, signal.SIG_DFL)

init_logs()


def auto_detect():
    for task in TASKS:
        if task.is_find():
            task.run()
            return

    logging.info("无法识别当前页面，请切换到合成页面或使用迷幻药页面。")


def listen_console_input():
    logging.info('Type "start" to start.')
    while True:
        command = input(">>> ")
        if command.strip().lower() == "start":
            logging.info("手动启动 auto_detect.")
            worker = work_in_process(auto_detect)()
            worker.join()


if __name__ == "__main__":
    try:
        with keyboard.GlobalHotKeys(
            {
                "<f7>": work_in_process(region_selector.main),
                "<f9>": work_in_process(auto_detect),
                "<f10>": stop_worker,
            }
        ) as h:
            logging.info("Press <f7> to select region, <f9> to start, <f10> to stop.")

            console_thread = threading.Thread(target=listen_console_input, daemon=True)
            console_thread.start()

            h.join()
    except KeyboardInterrupt:
        stop_worker()
        sys.exit(0)
