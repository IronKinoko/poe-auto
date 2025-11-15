import logging
import pyglet
import pyautogui
import sys
from PIL import Image

from src.core.screen import screenshot


class PygletSelector:
    def __init__(self, pil_image: Image.Image):
        self.img = pil_image.convert("RGBA")
        self.screen_w, self.screen_h = pyautogui.size()

        self.window = pyglet.window.Window(
            width=self.screen_w,
            height=self.screen_h + 1,
            style=pyglet.window.Window.WINDOW_STYLE_BORDERLESS,
        )

        if sys.platform == "win32":

            import ctypes

            hwnd = self.window._hwnd
            user32 = ctypes.windll.user32

            GWL_EXSTYLE = -20
            WS_EX_TOOLWINDOW = 0x00000080  # 作为工具窗体，不在任务栏/Alt-Tab显示
            WS_EX_APPWINDOW = 0x00040000  # 在任务栏显示（需要清除）

            # 读/改扩展样式
            ex = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            ex = (ex | WS_EX_TOOLWINDOW) & ~WS_EX_APPWINDOW
            user32.SetWindowLongW(hwnd, GWL_EXSTYLE, ex)

        self.window.set_mouse_visible(True)
        self.window.set_location(0, 0)

        # 将 PIL 数据转换为 pyglet image（使用 pitch 负值可避免垂直翻转问题）
        data = self.img.tobytes()
        self.texture = pyglet.image.ImageData(
            self.img.size[0], self.img.size[1], "RGBA", data, -self.img.size[0] * 4
        ).get_texture()

        # 选择状态
        self.start = None  # (x, y) in window coords (origin=bottom-left)
        self.current = None
        self.result = None

        # 绑定事件
        @self.window.event
        def on_draw():
            self._on_draw()

        @self.window.event
        def on_mouse_press(x, y, button, modifiers):
            if button != pyglet.window.mouse.LEFT:
                return
            # 记录起点
            self.start = (x, y)
            self.current = (x, y)

        @self.window.event
        def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
            # 更新选区
            if self.start:
                self.current = (x, y)

        @self.window.event
        def on_mouse_release(x, y, button, modifiers):
            # 关闭窗口并退出 pyglet 主循环
            if button != pyglet.window.mouse.LEFT:
                return
            try:
                self.result = self.get_screen_box()
                self.window.close()
            except Exception:
                pass
            pyglet.app.exit()

        @self.window.event
        def on_key_press(symbol, modifiers):
            # ESC 取消
            if symbol == pyglet.window.key.ESCAPE:
                self.result = None
                try:
                    self.window.close()
                except Exception:
                    pass
                pyglet.app.exit()

    def _on_draw(self):
        self.window.clear()

        color = (0, 0, 0, 115)
        win_w, win_h = self.window.size
        self.texture.blit(0, 0, width=win_w, height=win_h)

        box = self.get_box()
        if box:
            x, y, w, h = box
            border = pyglet.shapes.Box(x, y, w, h, color=(255, 0, 0))
            border.draw()

            # 绘制遮罩（挖空选区）
            mask_parts = [
                pyglet.shapes.Rectangle(0, 0, win_w, y, color=color),
                pyglet.shapes.Rectangle(0, y, x, h, color=color),
                pyglet.shapes.Rectangle(x + w, y, win_w - (x + w), h, color=color),
                pyglet.shapes.Rectangle(
                    0,
                    y + h,
                    win_w,
                    win_h - (y + h),
                    color=color,
                ),
            ]
            for part in mask_parts:
                part.draw()

            screen_box = self.get_screen_box()
            if screen_box:
                font_size = 12
                sx, sy, sw, sh = screen_box
                pyglet.text.Label(
                    f"{sw}*{sh} ({sx},{sy})",
                    x=x,
                    y=min(y + h + 4, win_h - font_size),
                    color=(255, 255, 255, 255),
                    font_size=font_size,
                ).draw()

        else:
            mask = pyglet.shapes.Rectangle(0, 0, win_w, win_h, color=color)
            mask.draw()

    def get_box(self):
        """返回选区在窗口坐标系中的位置和大小 (x, y, width, height)，原点在左下角。"""
        if self.start and self.current:
            x1 = min(self.start[0], self.current[0])
            y1 = min(self.start[1], self.current[1])
            x2 = max(self.start[0], self.current[0])
            y2 = max(self.start[1], self.current[1])
            width = x2 - x1
            height = y2 - y1
            return (x1, y1, width, height)
        return None

    def get_screen_box(self):
        """返回选区在屏幕坐标系中的位置和大小 (x, y, width, height)，原点在左上角。"""
        box = self.get_box()
        if not box:
            return None
        x, y, w, h = box
        sw, sy = pyautogui.size()
        return (x, max(sy - y - h, 0), w, h)

    def run(self):
        # 运行并阻塞直到关闭
        pyglet.app.run()
        return self.result


def main():
    logging.info("开始截屏并打开选择器（按 ESC 取消）...")
    img = screenshot(0, 0, pyautogui.size().width, pyautogui.size().height)
    sel = PygletSelector(img)
    res = sel.run()
    logging.info(res)
