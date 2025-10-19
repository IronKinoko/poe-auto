import os
import pyautogui
import time
from utils import *
from PIL import Image
from auto_common import *


def _find_top_point(loop_check=False):
    chongzhu_top_template = Image.open("./assets/chongzhu/chongzhu_top.png").convert("RGB")
    point = find_image_in_region(
        (1080, 320, 380, 80),
        chongzhu_top_template,
        threshold=0.7,
        debug_out_name="chongzhu_top",
        loop_check=loop_check,
    )
    return point


def is_find(loop_check=False):
    point = _find_top_point(loop_check)
    print("检测合成页面 at:", point)
    return bool(point)


def _auto_merge(template: Image.Image = None):
    try:
        if os.path.exists("tmp") and os.path.isdir("tmp"):
            os.rmdir("tmp")
    except Exception:
        pass

    pyautogui.PAUSE = 0.025

    template = template or screenshot(967, 1391, 34, 34, "tmp/template.png")
    btn_template = Image.open("./assets/chongzhu/hecheng.png").convert("RGB")
    empty_result_template = Image.open("./assets/chongzhu/empty_result.png").convert("RGB")

    _count = 0
    start = time.time()
    now = time.time()
    while True:
        if _count > 0:
            diff = time.time() - now
            now = time.time()
            ts = time.strftime("%H:%M:%S", time.localtime(now))
            print(f"------ {ts} diff: {diff:.2f}s  sum: {(now - start):.2f}s ------")

        # 检查是否可以合成
        point = find_image_in_region(
            (1190, 750, 140, 140),
            empty_result_template,
            threshold=0.8,
            debug_out_name="empty_result",
        )
        if not point:
            click((1254, 828), ctrl=True)

        point = find_image_in_region(
            (1085, 1691, 350, 80),
            btn_template,
            threshold=0.9,
            debug_out_name="hecheng",
        )
        if point:
            _count += 1
            print(f"第 {_count} 次合成")
            click(point)

            time.sleep(0.7)
            click((1254, 828), ctrl=True)
            continue

        if not add_material_from_bag(template):
            break


def start():
    template = screenshot(967, 1391, 34, 34, "tmp/template.png")
    click((900, 900))
    while True:
        _auto_merge(template)
        time.sleep(1)

        if ensure_is_login():
            pyautogui.press("esc")
            time.sleep(1)

        cangku_template = Image.open("./assets/cangku/cangku.png").convert("RGB")
        point = find_image_in_region(
            None,
            cangku_template,
            threshold=0.7,
            debug_out_name="cangku",
            loop_check=True,
        )

        if not point:
            print("未找到仓库，结束")
            break
        click(point)
        print("仓库 at:", point)

        currency_box = Image.open("./assets/cangku/currency_box.png").convert("RGB")
        point = find_image_in_region(
            (0, 0, 1300, 350),
            currency_box,
            threshold=0.7,
            debug_out_name="currency_box_top",
            loop_check=True,
        )
        if not point:
            print("未找到通货箱，结束")
            break
        click(point)
        print("通货箱 at:", point)

        point = find_image_in_region(
            (245, 1300, 860, 260),
            template,
            threshold=0.8,
            debug_out_name="currency_box_bottom",
            loop_check=True,
            timeout=1,
        )
        if point:
            # 存
            click((2600, 1240), ctrl=True, right=True)
            time.sleep(0.5)
            # 取
            click(point, ctrl=True, right=True)
            time.sleep(0.5)
        else:
            print("仓库内无素材，结束")
            break

            # 查找迷雾箱
            # miwu_box = Image.open("./assets/miwu_box.png").convert("RGB")
            # point = find_image_in_region(
            #     (0, 0, 1300, 350),
            #     miwu_box,
            #     threshold=0.7,
            #     debug_out_name="miwu_box_top",
            #     loop_check=True,
            # )
            # if not findTargetRegion:
            #     print("未找到迷雾箱，结束")
            #     break
            # point = toScreenPoint((0, 0), findTargetRegion)
            # click(point)
            # print("迷雾箱 at:", point)
            # time.sleep(1)

            # box = screenshot_pyautogui(325, 673, 681, 276, "tmp/box.png")
            # findTargetRegion = find_template_in_pil(
            #     box,
            #     template,
            #     threshold=0.7,
            #     debug_out="tmp/box_debug.png",
            # )
            # if not findTargetRegion:
            #     print("仓库内无素材，结束")
            #     break
            # point = toScreenPoint((325, 673), findTargetRegion)
            # # 存
            # click((2600, 1240), ctrl=True, Right=True)
            # time.sleep(0.5)
            # # 取
            # click(point, ctrl=True, Right=True)
            # time.sleep(0.5)

        pyautogui.press("esc")
        time.sleep(0.5)

        chongzhu_template = Image.open("./assets/chongzhu/chongzhu.png").convert("RGB")
        point = find_image_in_region(
            None,
            chongzhu_template,
            threshold=0.7,
            debug_out_name="chongzhu",
        )

        if not point:
            print("未找到重铸，结束")
            break
        click(point)

        point = _find_top_point(loop_check=True)
        if not point:
            print("未找到重铸界面，结束")
            break

        for i in range(3):
            add_material_from_bag(template)
            time.sleep(0.25)


if __name__ == "__main__":
    start()
