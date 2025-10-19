import pyautogui
from utils import *
from PIL import Image


def ensure_is_login():
    pyautogui.moveTo(100, 100)
    login_template = Image.open("./assets/login/login.png").convert("RGB")
    point = find_image_in_region(
        (1785, 1750, 300, 200),
        login_template,
        threshold=0.7,
        debug_out_name="login_debug",
    )
    if not point:
        return True

    click(point)
    print("登录 at:", point)

    pyautogui.moveTo(100, 100)

    login_step2_template = Image.open("./assets/login/login_step2.png").convert("RGB")
    point = find_image_in_region(
        (1340, 1850, 300, 200),
        login_step2_template,
        threshold=0.7,
        debug_out_name="login_step2",
        loop_check=True,
        check_interval=0.5,
        timeout=60.0,
    )
    if not point:
        raise Exception("登录步骤2 超时")
    click(point)

    login_step3_template = Image.open("./assets/login/login_step3.png").convert("RGB")
    point = find_image_in_region(
        (700, 1900, 300, 200),
        login_step3_template,
        threshold=0.7,
        debug_out_name="login_step3",
        loop_check=True,
        check_interval=0.5,
        timeout=60.0,
    )

    if not point:
        raise Exception("登录步骤3 超时")

    return False


def add_material_from_bag(template: Image.Image):
    point = find_image_in_region(
        (2537, 1180, 1300, 560), template, threshold=0.9, debug_out_name="bag"
    )

    if point:
        click(point, ctrl=True)
        print("添加素材 at:", point)
        pyautogui.moveTo(2537, 1180)
        return True
    else:
        print("素材已清空，合成结束")
        return False
