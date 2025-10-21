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
    tpl = cv2.cvtColor(np.array(template.convert("RGB")), cv2.COLOR_RGB2BGR)

    # 提取 alpha（如果有），并把模板变成 3 通道 BGR
    mask = None
    if tpl.ndim == 3 and tpl.shape[2] == 4:
        alpha = tpl[:, :, 3]
        mask = (alpha > 0).astype(np.uint8) * 255
        tpl = tpl[:, :, :3]
    elif tpl.ndim == 2:
        tpl = cv2.cvtColor(tpl, cv2.COLOR_GRAY2BGR)

    # PIL -> BGR (OpenCV 使用 BGR)
    img_bgr = cv2.cvtColor(np.array(pil_image.convert("RGB")), cv2.COLOR_RGB2BGR)

    # 如果模板比截图大，直接返回 None
    ih, iw = img_bgr.shape[:2]
    th, tw = tpl.shape[:2]
    if th > ih or tw > iw:
        return None

    # 转到 LAB 色彩空间以获得对颜色感知更稳健的结果
    try:
        img_cs = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2Lab)
        tpl_cs = cv2.cvtColor(tpl, cv2.COLOR_BGR2Lab)
    except Exception:
        # 回退到 BGR（极少出现）
        img_cs = img_bgr.copy()
        tpl_cs = tpl.copy()

    # 转为 float32 并归一化到 [0,1]
    img_cs = img_cs.astype(np.float32) / 255.0
    tpl_cs = tpl_cs.astype(np.float32) / 255.0

    # 固定等权通道（保持不改变接口）
    weights = [1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0]

    # 选择匹配方法：优先 TM_CCOEFF_NORMED（对去均值敏感，通常更鲁棒）
    # 若存在 mask，会尝试使用 TM_CCORR_NORMED 并传入 mask（部分 OpenCV 版本支持）
    res = None
    use_mask = mask is not None
    for c in range(3):
        img_ch = (img_cs[:, :, c] * 255).astype(np.uint8)
        tpl_ch = (tpl_cs[:, :, c] * 255).astype(np.uint8)

        try:
            if use_mask and mask is not None:
                # 一些 OpenCV 版本支持在 matchTemplate 中传入 mask（TM_CCORR_NORMED 支持）
                res_c = cv2.matchTemplate(
                    img_ch, tpl_ch, cv2.TM_CCORR_NORMED, mask=mask
                )
            else:
                res_c = cv2.matchTemplate(img_ch, tpl_ch, cv2.TM_CCOEFF_NORMED)
        except TypeError:
            # 某些版本的 Python 绑定不接受 mask 参数，回退到无 mask 的方法
            res_c = cv2.matchTemplate(img_ch, tpl_ch, cv2.TM_CCOEFF_NORMED)

        if res is None:
            res = weights[c] * res_c
        else:
            res = res + weights[c] * res_c

    # 查找最佳匹配
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    top_left = max_loc
    left, top = int(top_left[0]), int(top_left[1])
    w, h = tw, th

    if DEBUG and debug_out:
        print(f"Template {debug_out} match max_val: {max_val:.4f}")
        vis = cv2.cvtColor(np.array(pil_image.convert("RGB")), cv2.COLOR_RGB2BGR)
        loc = np.where(res >= threshold)
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

    return (int(left), int(top), w, h)


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
        left + x + w / 2 + random.randint(-3, 3),
        top + y + h / 2 + random.randint(-3, 3),
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
