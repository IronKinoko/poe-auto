import os
import json
import time
import pyautogui
import tkinter as tk
from PIL import Image, ImageTk

def capture_fullscreen():
    # 直接使用 pyautogui 截取全屏，返回 PIL.Image
    return pyautogui.screenshot()

class SelectorApp:
    def __init__(self, pil_image):
        self.img = pil_image
        self.root = tk.Tk()
        self.root.title("屏幕选择器 - 按 ESC 取消")
        self.root.configure(background="black")
        # 绑定 ESC 取消
        self.root.bind("<Escape>", lambda e: self._cancel())

        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()

        # 根据屏幕缩放/居中显示截图，并保存映射关系
        img_w, img_h = self.img.size
        # 仅当截图大于屏幕时按比例缩小显示，避免超出屏幕
        scale = min(1.0, screen_w / img_w, screen_h / img_h)
        self.display_scale = scale
        if scale < 1.0:
            disp_w = int(img_w * scale)
            disp_h = int(img_h * scale)
            display_img = self.img.resize((disp_w, disp_h), Image.LANCZOS)
        else:
            disp_w, disp_h = img_w, img_h
            display_img = self.img

        # 非全屏：窗口大小与显示图像一致，并居中于屏幕
        self.offset_x = 0
        self.offset_y = 0
        self.photo = ImageTk.PhotoImage(display_img)

        # 设置窗口大小并居中
        win_x = (screen_w - disp_w) // 2
        win_y = (screen_h - disp_h) // 2
        self.root.geometry(f"{disp_w}x{disp_h}+{win_x}+{win_y}")
        self.root.resizable(False, False)
        # 保持在最前（可选）
        self.root.attributes("-topmost", True)

        # Canvas 使用显示图像尺寸
        self.canvas = tk.Canvas(self.root, width=disp_w, height=disp_h, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        # 将截图放到 canvas 背景（左上角）
        self.canvas.create_image(0, 0, anchor="nw", image=self.photo)

        # 选择相关
        self.start_x = None
        self.start_y = None
        self.rect_id = None

        # 绑定鼠标事件
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

        # 用于结果
        self.result = None

    def _display_to_image(self, x, y):
        """
        将 canvas（显示）坐标转换为原始截图（屏幕像素）坐标。
        返回 (x_image, y_image)，并裁剪到图片范围内。
        """
        # 减去图片在 canvas 上的偏移
        dx = x - self.offset_x
        dy = y - self.offset_y
        # 限制在显示图片范围内
        disp_w = int(self.img.size[0] * self.display_scale)
        disp_h = int(self.img.size[1] * self.display_scale)
        dx = max(0, min(dx, disp_w))
        dy = max(0, min(dy, disp_h))
        # 映射回原始像素坐标
        if self.display_scale > 0:
            ix = int(round(dx / self.display_scale))
            iy = int(round(dy / self.display_scale))
        else:
            ix, iy = int(dx), int(dy)
        # 再次裁剪到原始图片范围
        ix = max(0, min(ix, self.img.size[0]))
        iy = max(0, min(iy, self.img.size[1]))
        return ix, iy

    def on_button_press(self, event):
        # 使用 canvas 坐标，然后在后续映射为原始坐标
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)
        # 新建矩形（基于显示坐标）
        if self.rect_id:
            self.canvas.delete(self.rect_id)
        self.rect_id = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y,
                                                    outline="red", width=2)

    def on_move(self, event):
        if not self.rect_id:
            return
        cur_x = self.canvas.canvasx(event.x)
        cur_y = self.canvas.canvasy(event.y)
        # 更新矩形（显示坐标）
        self.canvas.coords(self.rect_id, self.start_x, self.start_y, cur_x, cur_y)

    def on_release(self, event):
        if not self.rect_id:
            return
        end_x = self.canvas.canvasx(event.x)
        end_y = self.canvas.canvasy(event.y)
        # 将显示坐标转换为原始截图坐标
        sx, sy = self._display_to_image(self.start_x, self.start_y)
        ex, ey = self._display_to_image(end_x, end_y)
        x0 = int(min(sx, ex))
        y0 = int(min(sy, ey))
        x1 = int(max(sx, ex))
        y1 = int(max(sy, ey))
        w = x1 - x0
        h = y1 - y0
        self.result = (x0, y0, w, h)
        # 关闭窗口并返回
        self.root.quit()

    def _cancel(self):
        print("已取消")
        self.result = None
        self.root.quit()

    def run(self):
        self.root.mainloop()
        self.root.destroy()
        return self.result

def main():
    print("正在截取全屏...")
    time.sleep(0.05)
    img = capture_fullscreen()
    app = SelectorApp(img)
    result = app.run()
    if result:
        print("选区结果:", result)
    else:
        print("未选择任何区域。")

if __name__ == "__main__":
    main()