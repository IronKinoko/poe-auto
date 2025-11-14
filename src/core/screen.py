import pyautogui
import logging
import random
from typing import Optional, Tuple, Literal
from PIL import Image
import cv2
import numpy as np

from src.utils.common import time_it, ensure_dir, until, DEBUG


@time_it()
def _find_template_in_pil(
    pil_image: Image.Image,
    template: Image.Image,
    threshold=0.8,
    debug_out=None,
    mode: Literal["color", "grayscale", "both"] = "both",
):
    tpl = cv2.cvtColor(np.array(template.convert("RGB")), cv2.COLOR_RGB2BGR)
    # 如果模板是 4 通道（含 alpha），丢弃 alpha 通道，转换为 3 通道 BGR
    if tpl.ndim == 3 and tpl.shape[2] == 4:
        tpl = tpl[:, :, :3]
    elif tpl.ndim == 2:
        tpl = cv2.cvtColor(tpl, cv2.COLOR_GRAY2BGR)

    def _smooth(mat, bilateral=False, blur_kernel=0):
        if bilateral:
            return cv2.bilateralFilter(mat, d=7, sigmaColor=50, sigmaSpace=5)
        if blur_kernel and blur_kernel >= 3:
            k = blur_kernel if blur_kernel % 2 else blur_kernel + 1
            return cv2.GaussianBlur(mat, (k, k), 0)
        return mat

    tpl = _smooth(tpl, blur_kernel=3)
    source_bgr = cv2.cvtColor(np.array(pil_image.convert("RGB")), cv2.COLOR_RGB2BGR)
    source_bgr = _smooth(source_bgr, blur_kernel=3)

    # 如果模板比截图大，直接返回 None
    ih, iw = source_bgr.shape[:2]
    th, tw = tpl.shape[:2]
    if th > ih or tw > iw:
        return None

    def _grayscale():
        img_gray = cv2.cvtColor(source_bgr, cv2.COLOR_BGR2GRAY)
        tpl_gray = cv2.cvtColor(tpl, cv2.COLOR_BGR2GRAY)
        res = cv2.matchTemplate(img_gray, tpl_gray, cv2.TM_CCOEFF_NORMED)
        return res

    def _color():
        img_cs = cv2.cvtColor(source_bgr, cv2.COLOR_BGR2HSV)
        tpl_cs = cv2.cvtColor(tpl, cv2.COLOR_BGR2HSV)
        res = cv2.matchTemplate(img_cs, tpl_cs, cv2.TM_CCOEFF_NORMED)
        return res

    if mode == "grayscale":
        res = _grayscale()

    if mode == "color":
        res = _color()

    if mode == "both":
        res = _grayscale()
        if cv2.minMaxLoc(res)[1] >= threshold - 0.1:
            res = _color()

    # 查找最佳匹配
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    top_left = max_loc
    left, top = int(top_left[0]), int(top_left[1])
    w, h = tw, th

    if DEBUG and debug_out:
        logging.debug(f"Template {debug_out} match max_val: {max_val:.4f}")

        vis = cv2.cvtColor(np.array(pil_image.convert("RGB")), cv2.COLOR_RGB2BGR)
        loc = np.where(res >= 0.5)
        pts = list(zip(*loc[::-1]))
        if pts:
            rects = [[pt[0], pt[1], w, h] for pt in pts]
            grouped, _ = cv2.groupRectangles(rects + rects, groupThreshold=1, eps=0.5)
            if len(grouped):
                pts = [(int(x), int(y)) for x, y, _, _ in grouped]
        for pt in pts:
            _max_val = cv2.minMaxLoc(res[pt[1] : pt[1] + h, pt[0] : pt[0] + w])[1]
            color = (0, 255, 0) if _max_val >= threshold else (0, 255, 255)
            cv2.rectangle(vis, pt, (pt[0] + w, pt[1] + h), color, 1)
            cv2.putText(
                vis,
                f"{_max_val:.3f}",
                (pt[0], max(pt[1] - 8, 16)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                1,
                cv2.LINE_AA,
            )
        ensure_dir(debug_out)
        cv2.imwrite(debug_out, vis)
        logging.debug(f"Saved debug image -> {debug_out} (max_val={max_val})")

    if max_val < threshold:
        return None

    return (int(left), int(top), w, h)


_MSS_INSTANCE = None


def _get_mss_instance():
    global _MSS_INSTANCE
    if _MSS_INSTANCE is None:
        import mss

        _MSS_INSTANCE = mss.mss()
    return _MSS_INSTANCE


@time_it()
def _screenshot_mss(left, top, width, height):
    sct = _get_mss_instance()  # 复用实例，提升性能
    monitor = {"left": left, "top": top, "width": width, "height": height}
    sct_img = sct.grab(monitor)
    # 修正颜色格式
    img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")

    return img


def screenshot(left, top, width, height, out):
    img = _screenshot_mss(left, top, width, height)

    if DEBUG and out:
        ensure_dir(out)
        img.save(out)  # 直接用 PIL 保存
        logging.debug(f"Saved debug image -> {out}")

    return img


def to_screen_point(offset, region):
    """将区域内坐标转换为屏幕坐标"""
    x, y = offset
    left, top, w, h = region
    return (
        int(left + x + w / 2 + random.randint(-3, 3)),
        int(top + y + h / 2 + random.randint(-3, 3)),
    )


def find_image_in_region(
    region: Optional[Tuple[int, int, int, int]],
    image: Image.Image,
    threshold=0.8,
    debug_out_name=None,
    loop_check=False,
    check_interval=0.1,
    timeout=5.0,
    mode: Literal["color", "grayscale", "both"] = "both",
):
    """在指定区域内查找图像模板，返回屏幕坐标点或 None"""
    debug_screenshot_out = f"tmp/{debug_out_name}_screenshot.png"
    debug_find_out = f"tmp/{debug_out_name}_find.png"
    region = region or (0, 0, pyautogui.size().width, pyautogui.size().height)
    left, top, width, height = region

    def _detect_once():
        sct = screenshot(left, top, width, height, debug_screenshot_out)
        result = _find_template_in_pil(
            sct, image, threshold=threshold, debug_out=debug_find_out, mode=mode
        )
        return to_screen_point((region[0], region[1]), result) if result else None

    if loop_check:
        return until(_detect_once, check_interval=check_interval, timeout=timeout)
    else:
        return until(_detect_once, check_interval=0.05, retry_count=3)
