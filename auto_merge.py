import os
import pyautogui
import time
from utils import *


def auto_merge():
    try:
        if os.path.exists("tmp") and os.path.isdir("tmp"):
            os.rmdir("tmp")
    except Exception:
        pass

    pyautogui.PAUSE = 0.025

    template = screenshot_pyautogui(967, 1391, 34, 34, "tmp/template.png")
    btn_template = screenshot_pyautogui(1190, 1707, 120, 50, "tmp/btn_template.png")
    empty_result_template = screenshot_pyautogui(
        1244, 818, 20, 20, "tmp/empty_result_template.png"
    )

    _count = 0
    start = time.time()
    now = time.time()
    while True:
        if _count > 0:
            diff = time.time() - now
            now = time.time()
            print(f"------ diff: {diff:.2f}s  sum: {(now - start):.2f}s ------")

        # 检查是否可以合成
        empty_result = screenshot_pyautogui(1244, 818, 20, 20, "tmp/empty_result.png")
        findTargetRegion = find_template_in_pil(
            empty_result,
            empty_result_template,
            threshold=0.95,
            debug_out="tmp/empty_result_debug.png",
        )
        if not findTargetRegion:
            ctrl_click((1254, 828))

        btn = screenshot_pyautogui(1090, 1697, 350, 80, "tmp/btn.png")
        findTargetRegion = find_template_in_pil(
            btn, btn_template, threshold=0.95, debug_out="tmp/btn_debug.png"
        )
        if findTargetRegion:
            _count += 1
            print(f"第 {_count} 次合成")
            point = toScreenPoint((1090, 1697), findTargetRegion)
            click(point)
            time.sleep(0.6)
            ctrl_click((1254, 828))
            continue

        bag = screenshot_pyautogui(2537, 1180, 1300, 560, "tmp/bag.png")

        findTargetRegion = find_template_in_pil(
            bag, template, threshold=0.8, debug_out="tmp/bag_debug.png"
        )

        if findTargetRegion:
            point = toScreenPoint((2537, 1180), findTargetRegion)
            ctrl_click(point)
            print("添加素材 at:", point)
        else:
            print("Not found")
            break
