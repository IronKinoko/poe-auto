import logging
import time
import pyautogui
from abc import abstractmethod
from src.utils.common import clean_dir, load_img as _load_img
from PIL import Image
from src.core.screen import find_image_in_region
from src.core.click import click


class Task:
    def __init__(self):
        self.template = {}

    def run(self):
        try:
            self.setup()
            self.execute()
        finally:
            self.template = {}

    def setup(self):
        clean_dir("tmp")
        pyautogui.PAUSE = 0.025
        self.template = {}
        self._init_summary()

    @abstractmethod
    def execute(self):
        """执行任务主体逻辑"""
        pass

    @abstractmethod
    def is_find(self) -> bool:
        """检查任务是否适用当前页面"""
        pass

    def load_img(self, path: str) -> Image.Image:
        """加载图片"""
        if path not in self.template:
            self.template[path] = _load_img(path)
        return self.template[path]

    def ensure_is_login(self) -> bool:
        pyautogui.moveTo(100, 100)
        login_template = self.load_img("/assets/login/login.png")
        point = find_image_in_region(
            (1785, 1750, 300, 200),
            login_template,
            threshold=0.7,
            debug_out_name="login_debug",
        )
        if not point:
            return True

        click(point)
        logging.info(f"登录 at: {point}")

        pyautogui.moveTo(100, 100)

        login_step2_template = self.load_img("/assets/login/login_step2.png")
        point = find_image_in_region(
            (1340, 1850, 300, 200),
            login_step2_template,
            threshold=0.7,
            debug_out_name="login_step2",
            loop_check=True,
            check_interval=0.5,
            timeout=60.0,
        )
        if not point:
            raise Exception("登录步骤2 超时")
        click(point)

        login_step3_template = self.load_img("/assets/login/login_step3.png")
        point = find_image_in_region(
            (700, 1900, 300, 200),
            login_step3_template,
            threshold=0.7,
            debug_out_name="login_step3",
            loop_check=True,
            check_interval=0.5,
            timeout=60.0,
        )

        if not point:
            raise Exception("登录步骤3 超时")

        return False

    def add_material_from_bag(self, template: Image.Image) -> bool:
        point = find_image_in_region(
            (2537, 1180, 1300, 560),
            template,
            threshold=0.9,
            debug_out_name="bag",
        )

        if point:
            click(point, ctrl=True)
            logging.info(f"添加素材 at: {point}")
            pyautogui.moveTo(2537, 1180)
            return True
        else:
            return False

    def open_currency_box(self) -> bool:
        cangku_template = self.load_img("/assets/cangku/cangku.png")
        point = find_image_in_region(
            None,
            cangku_template,
            threshold=0.7,
            debug_out_name="cangku",
            loop_check=True,
            mode="grayscale",
        )

        if not point:
            logging.info("未找到仓库，结束")
            return False
        click(point)
        logging.info(f"仓库 at: {point}")

        currency_box = self.load_img("/assets/cangku/currency_box.png")
        point = find_image_in_region(
            (0, 0, 1300, 350),
            currency_box,
            threshold=0.7,
            debug_out_name="currency_box_top",
            loop_check=True,
        )
        if not point:
            logging.info("未找到通货箱，结束")
            return False
        click(point)
        logging.info(f"通货箱 at: {point}")

        return True

    def _init_summary(self):
        self.summary_info = {
            "total_merged": 0,
            "start_time": time.perf_counter(),
            "last_time": time.perf_counter(),
        }

    def report_progress(self):
        self.summary_info["total_merged"] += 1
        current_time = time.perf_counter()
        diff = current_time - self.summary_info["last_time"]
        self.summary_info["last_time"] = current_time
        use_time = self.summary_info["last_time"] - self.summary_info["start_time"]
        count = self.summary_info["total_merged"]

        logging.info(f"Total: {count} Avg: {use_time / count:.2f}/s Diff: {diff:.2f}s")
