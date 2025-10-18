import os
import pyautogui
import time
from utils import *
from PIL import Image


def auto_merge(template: Image.Image = None):
    try:
        if os.path.exists("tmp") and os.path.isdir("tmp"):
            os.rmdir("tmp")
    except Exception:
        pass

    pyautogui.PAUSE = 0.025

    if template is None:
        template = screenshot_pyautogui(967, 1391, 34, 34, "tmp/template.png")
    btn_template = Image.open("./assets/hecheng.png").convert("RGB")
    empty_result_template = Image.open("./assets/hecheng.png").convert("RGB")

    _count = 0
    start = time.time()
    now = time.time()
    while True:
        if _count > 0:
            diff = time.time() - now
            now = time.time()
            print(f"------ diff: {diff:.2f}s  sum: {(now - start):.2f}s ------")

        # 检查是否可以合成
        empty_result = screenshot_pyautogui(1190, 750, 140, 140, "tmp/empty_result.png")
        findTargetRegion = find_template_in_pil(
            empty_result,
            empty_result_template,
            threshold=0.8,
            debug_out="tmp/empty_result_debug.png",
        )
        if not findTargetRegion:
            click((1254, 828), ctrl=True)

        btn = screenshot_pyautogui(1085, 1691, 350, 80, "tmp/btn.png")
        findTargetRegion = find_template_in_pil(
            btn, btn_template, threshold=0.9, debug_out="tmp/btn_debug.png"
        )
        if findTargetRegion:
            _count += 1
            print(f"第 {_count} 次合成")
            point = toScreenPoint((1090, 1697), findTargetRegion)
            click(point)

            time.sleep(0.7)
            click((1254, 828), ctrl=True)
            continue

        if not add_material_from_bag(template):
            break


def add_material_from_bag(template: Image.Image):
    bag = screenshot_pyautogui(2537, 1180, 1300, 560, "tmp/bag.png")
    findTargetRegion = find_template_in_pil(
        bag, template, threshold=0.8, debug_out="tmp/bag_debug.png"
    )

    if findTargetRegion:
        point = toScreenPoint((2537, 1180), findTargetRegion)
        click(point, ctrl=True)
        print("添加素材 at:", point)
        return True
    else:
        print("素材已清空，合成结束")
        return False


def ensure_is_login():
    pyautogui.moveTo(100, 100)
    sct = pyautogui.screenshot()
    login_template = Image.open("./assets/login.png").convert("RGB")
    findTargetRegion = find_template_in_pil(
        sct,
        login_template,
        threshold=0.7,
        debug_out="tmp/login_debug.png",
    )
    if not findTargetRegion:
        return False

    point = toScreenPoint((0, 0), findTargetRegion)
    click(point)
    print("登录 at:", point)

    pyautogui.moveTo(100, 100)

    login_step2_template = Image.open("./assets/login_step2.png").convert("RGB")
    while True:
        sct = pyautogui.screenshot()
        findTargetRegion = find_template_in_pil(
            sct,
            login_step2_template,
            threshold=0.7,
            debug_out="tmp/login_step2_debug.png",
        )
        if not findTargetRegion:
            time.sleep(0.5)
            continue

        point = toScreenPoint((0, 0), findTargetRegion)
        click(point)
        print("登录步骤2 at:", point)
        break

    login_step3_template = Image.open("./assets/login_step3.png").convert("RGB")
    while True:
        sct = pyautogui.screenshot()
        findTargetRegion = find_template_in_pil(
            sct,
            login_step3_template,
            threshold=0.7,
            debug_out="tmp/login_step3_debug.png",
        )
        if not findTargetRegion:
            time.sleep(0.5)
            continue
        break

    return True


def auto_merge_delirium():
    template = screenshot_pyautogui(967, 1391, 34, 34, "tmp/template.png")
    click((900, 900))
    while True:
        auto_merge(template)
        time.sleep(1)

        if not ensure_is_login():
            pyautogui.press("esc")
            time.sleep(1)

        sct = pyautogui.screenshot()
        cangku_template = Image.open("./assets/cangku.png").convert("RGB")
        findTargetRegion = find_template_in_pil(
            sct,
            cangku_template,
            threshold=0.7,
            debug_out="tmp/cangku_debug.png",
        )
        if not findTargetRegion:
            print("未找到仓库，结束")
            break
        point = toScreenPoint((0, 0), findTargetRegion)
        click(point)
        print("仓库 at:", point)
        time.sleep(3)

        sct = screenshot_pyautogui(0, 0, 1300, 350, "tmp/box_top.png")
        currency_box = Image.open("./assets/currency_box.png").convert("RGB")
        findTargetRegion = find_template_in_pil(
            sct,
            currency_box,
            threshold=0.7,
            debug_out="tmp/currency_box_debug.png",
        )
        if not findTargetRegion:
            print("未找到通货箱，结束")
            break
        point = toScreenPoint((0, 0), findTargetRegion)
        click(point)
        print("通货箱 at:", point)
        time.sleep(0.5)

        box = screenshot_pyautogui(245, 1300, 860, 260, "tmp/box.png")
        findTargetRegion = find_template_in_pil(
            box,
            template,
            threshold=0.7,
            debug_out="tmp/box_debug.png",
        )
        if findTargetRegion:
            point = toScreenPoint((245, 1300), findTargetRegion)
            # 存
            click((2600, 1240), ctrl=True, Right=True)
            time.sleep(0.5)
            # 取
            click(point, ctrl=True, Right=True)
            time.sleep(0.5)
        else:
            print("仓库内无素材，结束")
            break

        # sct = screenshot_pyautogui(0, 0, 1300, 350, "tmp/box_top.png")
        # miwu_box = Image.open("./assets/miwu_box.png").convert("RGB")
        # findTargetRegion = find_template_in_pil(
        #     sct,
        #     miwu_box,
        #     threshold=0.7,
        #     debug_out="tmp/miwu_box_debug.png",
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

        sct = pyautogui.screenshot()
        chongzhu_template = Image.open("./assets/chongzhu.png").convert("RGB")
        findTargetRegion = find_template_in_pil(
            sct,
            chongzhu_template,
            threshold=0.5,
            debug_out="tmp/chongzhu_debug.png",
        )

        if not findTargetRegion:
            print("未找到重铸，结束")
            break
        point = toScreenPoint((0, 0), findTargetRegion)
        click(point)
        time.sleep(3)

        for i in range(3):
            add_material_from_bag(template)
            time.sleep(0.25)


if __name__ == "__main__":
    auto_merge_delirium()
