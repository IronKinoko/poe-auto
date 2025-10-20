import os
import pyautogui
import time
from utils import *
from PIL import Image
from auto_common import *


def _find_top_point(loop_check=False):
    anjie_top_template = Image.open("./assets/anjie/top.png").convert("RGB")
    point = find_image_in_region(
        (500, 200, 1600, 110),
        anjie_top_template,
        threshold=0.7,
        debug_out_name="anjie_top",
        loop_check=loop_check,
    )
    return point


def _find_result_point():
    x, y = _find_top_point()
    return (x, y + 300)


def _find_delirium_point():
    x, y = _find_top_point()
    return [
        (x - 180, y + 600),
        (x, y + 600),
        (x + 180, y + 600),
    ]


def is_find(loop_check=False):
    point = _find_top_point(loop_check)
    print("检测通货交易页面 at:", point)
    return bool(point)


def _auto_anjie():
    try:
        if os.path.exists("tmp") and os.path.isdir("tmp"):
            os.rmdir("tmp")
    except Exception:
        pass

    pyautogui.PAUSE = 0.025

    order_done_template = Image.open("./assets/anjie/order_done.png").convert("RGB")
    anjie_name_template = Image.open("./assets/anjie/anjie_name.png").convert("RGB")
    start = time.time()
    now = time.time()
    for _count in range(60):
        if _count > 0:
            diff = time.time() - now
            now = time.time()
            ts = time.strftime("%H:%M:%S", time.localtime(now))
            print(f"------ {ts} diff: {diff:.2f}s  sum: {(now - start):.2f}s ------")

        point = find_image_in_region(
            None,
            order_done_template,
            threshold=0.8,
            debug_out_name="order_done",
            loop_check=True,
        )

        if not point:
            print("未找到完成订单，结束")
            return

        print(f"第 {_count+1} 次找到完成的订单，开始收获")
        template = screenshot(
            int(point[0] - 250), int(point[1] - 80), 25, 25, "tmp/template.png"
        )
        click((point[0] - 250, point[1] - 80), ctrl=True, right=True)

        pyautogui.press("esc")
        pyautogui.press("esc")

        if not open_currency_box():
            break

        point = find_image_in_region(
            (2537, 1180, 1300, 560), template, threshold=0.9, debug_out_name="bag"
        )
        if not point:
            print("未找到对应通货，结束")
            break
        click(point, ctrl=True, right=True)

        pyautogui.press("esc")

        point = find_image_in_region(
            None,
            anjie_name_template,
            threshold=0.7,
            debug_out_name="anjie_name",
            loop_check=True,
        )
        click(point, ctrl=True)


def start():
    if not is_find():
        print("当前页面不是通货交易页面，无法启动。")
        return

    click(_find_top_point())

    _auto_anjie()


if __name__ == "__main__":
    start()
