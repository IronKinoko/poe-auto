import time
import pyautogui
import random
from typing import Optional, Tuple
from PIL import Image
import cv2
import numpy as np

from src.utils.common import time_it, ensure_dir, until, DEBUG


@time_it()
def _find_template_in_pil(
    pil_image: Image.Image, template: Image.Image, threshold=0.8, debug_out=None
):
    # 始终使用 3 通道 BGR（忽略 alpha）
    tpl = cv2.cvtColor(np.array(template.convert("RGB")), cv2.COLOR_RGB2BGR)

    # PIL -> BGR (OpenCV 使用 BGR)
    img_bgr = cv2.cvtColor(np.array(pil_image.convert("RGB")), cv2.COLOR_RGB2BGR)

    # 如果模板比截图大，直接返回 None
    ih, iw = img_bgr.shape[:2]
    th, tw = tpl.shape[:2]
    if th > ih or tw > iw:
        return None

    # 直接在 BGR 空间匹配
    img_cs = img_bgr
    tpl_cs = tpl

    # 等权通道加权
    weights = [1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0]

    # 逐通道 TM_CCOEFF_NORMED 匹配（无 mask）
    res = None
    for c in range(3):
        img_ch = img_cs[:, :, c]
        tpl_ch = tpl_cs[:, :, c]
        res_c = cv2.matchTemplate(img_ch, tpl_ch, cv2.TM_CCOEFF_NORMED)
        res = res_c * weights[c] if res is None else res + res_c * weights[c]

    # 查找最佳匹配
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    top_left = max_loc
    left, top = int(top_left[0]), int(top_left[1])
    w, h = tw, th

    if DEBUG and debug_out:
        print(f"Template {debug_out} match max_val: {max_val:.4f}")
        vis = cv2.cvtColor(np.array(pil_image.convert("RGB")), cv2.COLOR_RGB2BGR)
        loc = np.where(res >= threshold - 0.2)
        for pt in zip(*loc[::-1]):
            cv2.rectangle(vis, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)
            score_text = f"{max_val:.3f}"
            cv2.putText(
                vis,
                score_text,
                (pt[0], max(pt[1] - 8, 0)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 255),
                1,
                cv2.LINE_AA,
            )
        ensure_dir(debug_out)
        cv2.imwrite(debug_out, vis)
        print(f"Saved debug image -> {debug_out} (max_val={max_val})")

    if max_val < threshold:
        return None

    return (left, top, w, h)


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
        print(f"Saved debug image -> {out}")

    return img


@time_it()
def screenshot(left, top, width, height, out):
    return _screenshot_mss(left, top, width, height, out)


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
):
    """在指定区域内查找图像模板，返回屏幕坐标点或 None"""
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
        return until(_detect_once, check_interval=check_interval, timeout=timeout)
    else:
        return until(_detect_once, check_interval=0.05, retry_count=3)
