import logging
import time

from PIL import Image
import pyautogui
from src.core.click import click
from src.core.screen import find_image_in_region, screenshot
from src.tasks.base import Task
from src.utils.common import until


class MergeTask(Task):
    def execute(self):
        template = screenshot(967, 1391, 34, 34, "tmp/template.png")

        self._init_summary()
        while True:
            self.auto_merge(template)
            time.sleep(1)

            if self.ensure_is_login():
                pyautogui.press("esc")
                time.sleep(1)

            if not self.open_currency_box():
                break

            point = find_image_in_region(
                (245, 1300, 860, 260),
                template,
                threshold=0.8,
                debug_out_name="currency_box_bottom",
                loop_check=True,
                timeout=1,
            )
            if point:
                # 存
                click((2600, 1240), ctrl=True, right=True)
                time.sleep(0.5)
                # 取
                click(point, ctrl=True, right=True)
                time.sleep(0.5)
            else:
                logging.info("仓库内无素材，结束")
                break

                # 查找迷雾箱
                # miwu_box = Image.open("./assets/miwu_box.png").convert("RGB")
                # point = find_image_in_region(
                #     (0, 0, 1300, 350),
                #     miwu_box,
                #     threshold=0.7,
                #     debug_out_name="miwu_box_top",
                #     loop_check=True,
                # )
                # if not findTargetRegion:
                #     logging.info("未找到迷雾箱，结束")
                #     break
                # point = toScreenPoint((0, 0), findTargetRegion)
                # click(point)
                # logging.info("迷雾箱 at:", point)
                # time.sleep(1)

                # box = screenshot_pyautogui(325, 673, 681, 276, "tmp/box.png")
                # findTargetRegion = find_template_in_pil(
                #     box,
                #     template,
                #     threshold=0.7,
                #     debug_out="tmp/box_debug.png",
                # )
                # if not findTargetRegion:
                #     logging.info("仓库内无素材，结束")
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

            chongzhu_template = self.load_img("/assets/chongzhu/chongzhu.png")
            point = find_image_in_region(
                None,
                chongzhu_template,
                threshold=0.7,
                debug_out_name="chongzhu",
                mode="grayscale",
            )

            if not point:
                logging.info("未找到重铸，结束")
                break
            click(point)

            point = self.find_top_point(loop_check=True)
            if not point:
                logging.info("未找到重铸界面，结束")
                break

    def is_find(self, loop_check=False):
        point = self.find_top_point(loop_check)
        if point:
            logging.info(f"检测合成页面 at: {point}")
        return bool(point)

    def find_top_point(self, loop_check=False):
        chongzhu_top_template = self.load_img("/assets/chongzhu/chongzhu_top.png")
        point = find_image_in_region(
            (1080, 320, 380, 80),
            chongzhu_top_template,
            threshold=0.7,
            debug_out_name="chongzhu_top",
            loop_check=loop_check,
        )
        return point

    def _init_summary(self):
        self.summary_info = {
            "total_merged": 0,
            "start_time": time.time(),
            "total_time": 0.0,
        }

    def report_progress(self):
        self.summary_info["total_merged"] += 1
        self.summary_info["total_time"] = time.time() - self.summary_info["start_time"]
        logging.info(
            f"------ total: {self.summary_info['total_merged']} avg: {self.summary_info['total_time'] / self.summary_info['total_merged']:.2f}/s ------"
        )

    def auto_merge(self, template: Image.Image):
        btn_template = self.load_img("/assets/chongzhu/hecheng.png")

        while True:
            # 检查是否可以合成
            if not self.check_result_empty():
                self.collect_result()

            point = find_image_in_region(
                (1085, 1691, 350, 80),
                btn_template,
                threshold=0.9,
                debug_out_name="hecheng",
            )
            if point:
                click(point)

                self.collect_result()
                self.report_progress()

                continue

            if not self.add_material_from_bag(template):
                break

    def check_result_empty(self) -> bool:
        point = find_image_in_region(
            (1190, 750, 140, 140),
            self.load_img("/assets/chongzhu/empty_result.png"),
            debug_out_name="empty_result_check",
            mode="grayscale",
        )
        return bool(point)

    def collect_result(self):
        is_empty = False
        while True:
            if not self.check_result_empty():
                is_empty = True
                click((1254, 828), ctrl=True)
            else:
                if is_empty:
                    break


if __name__ == "__main__":
    task = MergeTask()
    if task.is_find():
        task.execute()
