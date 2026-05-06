import os


def get_task_threshold():
    return int(os.getenv("TASK_THRESHOLD", "75"))
