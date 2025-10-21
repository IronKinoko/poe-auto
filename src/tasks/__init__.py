from .base import Task
from .currency import CurrencyTask
from .merge import MergeTask
from .delirium import DeliriumTask

TASKS: list[Task] = [MergeTask(), CurrencyTask(), DeliriumTask()]

__all__ = ["TASKS"]
