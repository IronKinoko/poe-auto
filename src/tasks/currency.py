import logging
import time

import pyautogui
from src.core.click import click
from src.core.screen import find_image_in_region, screenshot
from src.tasks.base import Task


class CurrencyTask(Task):
    def execute(self):
        if not self.is_find():
            logging.info("当前页面不是通货交易页面，无法启动。")
            return

        self.auto_collect_currency()

    def is_find(self, loop_check=False):
        point = self.find_top_point(loop_check)
        if point:
            logging.info(f"检测通货交易页面 at: {point}")
        return bool(point)

    def find_top_point(self, loop_check=False):
        anjie_top_template = self.load_img("/assets/currency/top.png")
        point = find_image_in_region(
            (500, 200, 1600, 110),
            anjie_top_template,
            threshold=0.7,
            debug_out_name="anjie_top",
            loop_check=loop_check,
        )
        return point

    def auto_collect_currency(self):
        order_done_template = self.load_img("/assets/currency/order_done.png")
        anjie_name_template = self.load_img("/assets/currency/anjie_name.png")
        start = time.time()
        now = time.time()
        for _count in range(60):
            if _count > 0:
                diff = time.time() - now
                now = time.time()
                ts = time.strftime("%H:%M:%S", time.localtime(now))
                logging.info(
                    f"------ {ts} diff: {diff:.2f}s  sum: {(now - start):.2f}s ------"
                )

            point = find_image_in_region(
                (475, 693, 2246, 1221),
                order_done_template,
                threshold=0.8,
                debug_out_name="order_done",
                loop_check=True,
            )

            if not point:
                logging.info("未找到完成订单，结束")
                return

            logging.info(f"第 {_count+1} 次找到完成的订单，开始收获")
            template = screenshot(
                point[0] - 250, point[1] - 80, 25, 25, "tmp/template.png"
            )
            click((point[0] - 250, point[1] - 80), ctrl=True, right=True)

            pyautogui.press("esc")
            pyautogui.press("esc")

            if not self.open_currency_box():
                break

            point = find_image_in_region(
                (2537, 1180, 1300, 560), template, threshold=0.9, debug_out_name="bag"
            )
            if not point:
                logging.info("未找到对应通货，结束")
                break
            click(point, ctrl=True, right=True)

            pyautogui.press("esc")

            point = find_image_in_region(
                None,
                anjie_name_template,
                threshold=0.7,
                debug_out_name="anjie_name",
                loop_check=True,
                mode="grayscale",
            )
            click(point, ctrl=True)


if __name__ == "__main__":
    task = CurrencyTask()
    if task.is_find():
        task.execute()
