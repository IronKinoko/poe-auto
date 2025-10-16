import os
import pyautogui
import time
import random
import functools

def timeit_func(log_fn=print):
    def deco(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            t0 = time.perf_counter()
            res = func(*args, **kwargs)
            t1 = time.perf_counter()
            log_fn(f"{func.__name__} took {t1-t0:.6f}s")
            return res

        return wrapper

    return deco


def ensure_dir(path):
    d = os.path.dirname(path)
    if d and not os.path.exists(d):
        os.makedirs(d, exist_ok=True)


def find_template_in_pil(pil_image, template, threshold=0.8, debug_out=None):
    try:
        import cv2
        import numpy as np
    except Exception as e:
        print("需要 opencv-python 和 numpy 用于模板匹配：", e)
        raise

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

    if max_val < threshold:
        return None

    top_left = max_loc
    left, top = int(top_left[0]), int(top_left[1])
    w, h = tw, th

    # if debug_out:
    #     vis = cv2.cvtColor(np.array(pil_image.convert("RGB")), cv2.COLOR_RGB2BGR)
    #     cv2.rectangle(vis, (left, top), (left + w, top + h), (0, 255, 255), 2)
    #     score_text = f"{max_val:.3f}"
    #     cv2.putText(
    #         vis,
    #         score_text,
    #         (left, max(top - 8, 0)),
    #         cv2.FONT_HERSHEY_SIMPLEX,
    #         0.6,
    #         (0, 255, 255),
    #         2,
    #         cv2.LINE_AA,
    #     )
    #     ensure_dir(debug_out)
    #     cv2.imwrite(debug_out, vis)
    #     print(f"Saved debug image -> {debug_out} (max_val={max_val})")

    return (left, top, w, h, float(max_val))


def screenshot_pyautogui(left, top, width, height, out):
    img = pyautogui.screenshot(region=(left, top, width, height))

    # ensure_dir(out)
    # img.save(out)

    return img


def click(point):
    pyautogui.moveTo(point)
    pyautogui.click()


def ctrl_click(point):
    pyautogui.keyDown("ctrl")
    click(point)
    pyautogui.keyUp("ctrl")


def toScreenPoint(offset, region):
    """将区域内坐标转换为屏幕坐标"""
    x, y = offset
    left, top, w, h, _ = region
    return (
        left + x + w / 2 + random.randint(-3, 3),
        top + y + h / 2 + random.randint(-3, 3),
    )

