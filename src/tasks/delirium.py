import logging
import time

from src.core.click import click
from src.core.screen import find_image_in_region, screenshot
from src.tasks.base import Task


class DeliriumTask(Task):
    def execute(self):
        if not self.is_find():
            logging.info("当前页面不是使用迷幻药页面，无法启动。")
            return

        logging.info(
            "将要涂油的物品放到背包前四格，分别是<物品><迷幻药1><迷幻药2><迷幻药3>"
        )

        self.use_delirium()

    def is_find(self, loop_check=False):
        point = self.find_top_point(loop_check)
        if point:
            logging.info(f"检测使用迷幻药页面 at: {point}")
        return bool(point)

    def find_top_point(self, loop_check=False):
        use_delirium_top_template = self.load_img(
            "/assets/delirium/use_delirium_top.png"
        )
        point = find_image_in_region(
            (800, 500, 800, 300),
            use_delirium_top_template,
            threshold=0.7,
            debug_out_name="use_delirium_top",
            loop_check=loop_check,
        )
        return point

    def find_result_point(self):
        x, y = self.find_top_point()
        return (x, y + 300)

    def find_delirium_point(self):
        x, y = self.find_top_point()
        return [
            (x - 180, y + 600),
            (x, y + 600),
            (x + 180, y + 600),
        ]

    def use_delirium(self):
        # 清空所有内容
        for fn in [self.find_delirium_point, self.find_result_point]:
            points = fn()
            for point in points if isinstance(points, list) else [points]:
                click(point, ctrl=True)

        template1 = screenshot(2550, 1200, 30, 80, "tmp/template1.png")
        template2 = screenshot(2676, 1237, 50, 30, "tmp/template2.png")
        template3 = screenshot(2784, 1237, 50, 30, "tmp/template3.png")
        template4 = screenshot(2892, 1237, 50, 30, "tmp/template4.png")
        btn_template = self.load_img("/assets/delirium/dizhu.png")

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

            for template in [template1, template2, template3, template4]:
                added = self.add_material_from_bag(template)
                if not added:
                    logging.info("素材已清空，使用迷幻药结束")
                    return

            point = find_image_in_region(
                (1030, 1633, 400, 100),
                btn_template,
                threshold=0.9,
                debug_out_name="dizhu",
            )

            if point:
                logging.info(f"第 {_count+1} 次使用迷幻药")
                click(point)

                result_point = self.find_result_point()
                click(result_point, ctrl=True)
            else:
                logging.info("未找到使用按钮，使用迷幻药结束")
                return


if __name__ == "__main__":
    task = DeliriumTask()
    if task.is_find():
        task.execute()
