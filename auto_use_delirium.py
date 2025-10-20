import os
import pyautogui
import time
from utils import *
from PIL import Image
from auto_common import *


def _find_top_point(loop_check=False):
    use_delirium_top_template = Image.open(
        "./assets/delirium/use_delirium_top.png"
    ).convert("RGB")
    point = find_image_in_region(
        (800, 500, 800, 300),
        use_delirium_top_template,
        threshold=0.7,
        debug_out_name="use_delirium_top",
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
    print("检测使用迷幻药页面 at:", point)
    return bool(point)


def _use_delirium():
    try:
        if os.path.exists("tmp") and os.path.isdir("tmp"):
            os.rmdir("tmp")
    except Exception:
        pass

    pyautogui.PAUSE = 0.025

    # 清空所有内容
    for fn in [_find_delirium_point, _find_result_point]:
        points = fn()
        for point in points if isinstance(points, list) else [points]:
            click(point, ctrl=True)

    template1 = screenshot(2550, 1200, 30, 80, "tmp/template1.png")
    template2 = screenshot(2676, 1237, 50, 30, "tmp/template2.png")
    template3 = screenshot(2784, 1237, 50, 30, "tmp/template3.png")
    template4 = screenshot(2892, 1237, 50, 30, "tmp/template4.png")
    btn_template = Image.open("./assets/delirium/dizhu.png").convert("RGB")

    start = time.time()
    now = time.time()
    for _count in range(60):
        if _count > 0:
            diff = time.time() - now
            now = time.time()
            ts = time.strftime("%H:%M:%S", time.localtime(now))
            print(f"------ {ts} diff: {diff:.2f}s  sum: {(now - start):.2f}s ------")

        for template in [template1, template2, template3, template4]:
            added = add_material_from_bag(template)
            if not added:
                print("素材已清空，使用迷幻药结束")
                return

        point = find_image_in_region(
            (1030, 1633, 400, 100),
            btn_template,
            threshold=0.9,
            debug_out_name="dizhu",
        )

        if point:
            print(f"第 {_count+1} 次使用迷幻药")
            click(point)

            result_point = _find_result_point()
            click(result_point, ctrl=True)
        else:
            print("未找到使用按钮，使用迷幻药结束")
            return


def start():
    if not is_find():
        print("当前页面不是使用迷幻药页面，无法启动。")
        return

    print("将要涂油的物品放到背包前四格，分别是<物品><迷幻药1><迷幻药2><迷幻药3>")

    click((900, 900))

    _use_delirium()


if __name__ == "__main__":
    start()
