import os
import pyautogui
import time
import random
import functools
import sys
from PIL import Image

DEBUG = "--debug" in sys.argv


def time_it(log_fn=print):
    def deco(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            t0 = time.perf_counter()
            res = func(*args, **kwargs)
            t1 = time.perf_counter()
            if DEBUG:
                log_fn(f"{func.__name__} took {t1-t0:.6f}s")
            return res

        return wrapper

    return deco


def ensure_dir(path):
    d = os.path.dirname(path)
    if d and not os.path.exists(d):
        os.makedirs(d, exist_ok=True)


@time_it()
def _find_template_in_pil(
    pil_image: Image.Image, template: Image.Image, threshold=0.8, debug_out=None
):
    try:
        import cv2
        import numpy as np
    except Exception as e:
        print("需要 opencv-python 和 numpy 用于模板匹配：", e)
        raise

    # PIL -> BGR
    img_bgr = cv2.cvtColor(np.array(pil_image.convert("RGB")), cv2.COLOR_RGB2BGR)
    tpl_bgr = cv2.cvtColor(np.array(template.convert("RGB")), cv2.COLOR_RGB2BGR)

    # 处理透明通道（mask）
    mask = None
    if tpl_bgr.ndim == 3 and tpl_bgr.shape[2] == 4:
        alpha = tpl_bgr[:, :, 3]
        mask = (alpha > 0).astype(np.uint8) * 255
        tpl_bgr = tpl_bgr[:, :, :3]
    elif tpl_bgr.ndim == 2:
        tpl_bgr = cv2.cvtColor(tpl_bgr, cv2.COLOR_GRAY2BGR)

    # 尺寸检查
    ih, iw = img_bgr.shape[:2]
    th, tw = tpl_bgr.shape[:2]
    if th > ih or tw > iw:
        return None

    # 转到 LAB 色彩空间（对颜色感知更准确）
    try:
        img_lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2Lab)
        tpl_lab = cv2.cvtColor(tpl_bgr, cv2.COLOR_BGR2Lab)
    except Exception:
        img_lab = img_bgr.copy()
        tpl_lab = tpl_bgr.copy()

    if mask is not None:
        # 带 mask 的匹配（支持透明背景）
        try:
            res = cv2.matchTemplate(img_lab, tpl_lab, cv2.TM_CCORR_NORMED, mask=mask)
        except TypeError:
            # 旧版本 OpenCV 不支持 mask，回退到普通匹配
            res = cv2.matchTemplate(img_lab, tpl_lab, cv2.TM_CCOEFF_NORMED)
    else:
        # 标准匹配
        res = cv2.matchTemplate(img_lab, tpl_lab, cv2.TM_CCOEFF_NORMED)

    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    if max_val < threshold:
        return None

    left, top = max_loc
    w, h = tw, th

    if DEBUG and debug_out:
        vis = img_bgr.copy()
        cv2.rectangle(vis, (left, top), (left + w, top + h), (0, 255, 255), 2)
        score_text = f"{max_val:.3f}"
        cv2.putText(
            vis,
            score_text,
            (left, max(top - 8, 0)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 255),
            2,
            cv2.LINE_AA,
        )
        ensure_dir(debug_out)
        cv2.imwrite(debug_out, vis)
        print(f"Saved debug image -> {debug_out} (max_val={max_val})")

    return (left, top, w, h)


def _screenshot_pyautogui(left, top, width, height, out):
    img = pyautogui.screenshot(region=(left, top, width, height))

    if DEBUG and out:
        ensure_dir(out)
        img.save(out)

    return img


_MSS_INSTANCE = None


def _get_mss_instance():
    global _MSS_INSTANCE
    if _MSS_INSTANCE is None:
        import mss

        _MSS_INSTANCE = mss.mss()
    return _MSS_INSTANCE


def _screenshot_mss(left, top, width, height, out):
    sct = _get_mss_instance()  # 复用实例，提升性能
    monitor = {"left": left, "top": top, "width": width, "height": height}
    sct_img = sct.grab(monitor)
    # 修正颜色格式
    img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")

    if DEBUG and out:
        ensure_dir(out)
        img.save(out)  # 直接用 PIL 保存

    return img


@time_it()
def screenshot(left, top, width, height, out):
    return _screenshot_mss(left, top, width, height, out)


def click(point, ctrl=False, right=False):
    pyautogui.moveTo(point)
    if ctrl:
        pyautogui.keyDown("ctrl")
    pyautogui.click(button="right" if right else "left")
    if ctrl:
        pyautogui.keyUp("ctrl")


def to_screen_point(offset, region):
    """将区域内坐标转换为屏幕坐标"""
    x, y = offset
    left, top, w, h = region
    return (
        left + x + w / 2 + random.randint(-3, 3),
        top + y + h / 2 + random.randint(-3, 3),
    )


def find_image_in_region(
    region: tuple[int, int, int, int] | None,
    image: Image.Image,
    threshold=0.8,
    debug_out_name=None,
    loop_check=False,
    check_interval=0.1,
    timeout=5.0,
):
    ensure_dir("tmp")
    debug_screenshot_out = f"tmp/{debug_out_name}_screenshot.png"
    debug_find_out = f"tmp/{debug_out_name}_find.png"
    region = region or (0, 0, pyautogui.size().width, pyautogui.size().height)
    left, top, width, height = region

    def _detect_once():
        sct = screenshot(left, top, width, height, debug_screenshot_out)
        result = _find_template_in_pil(
            sct, image, threshold=threshold, debug_out=debug_find_out
        )
        return to_screen_point((region[0], region[1]), result) if result else None

    if loop_check:
        return until(_detect_once, check_interval, timeout)
    else:
        return _detect_once()


def until(fn, check_interval=0.1, timeout=10.0):
    start_time = time.time()
    while True:
        res = fn()
        if res:
            return res
        if time.time() - start_time > timeout:
            return None
        time.sleep(check_interval)
