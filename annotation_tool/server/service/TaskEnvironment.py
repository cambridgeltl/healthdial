import threading
import json
import logging
import os
from bson import ObjectId
from init import pymongo
from dao.TaskInfo import TaskInfo
from datetime import datetime, timedelta
from pymongo import ReturnDocument


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super(Singleton, cls).__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class TaskEnvironment(metaclass=Singleton):
    def __init__(self):
        self.task_dic = None
        self.lock = threading.Lock()  # Add a lock for thread safety

        current_path = os.path.abspath(os.path.dirname(__file__))
        config_path = current_path + "/../config/task_dic.json"
        task_path = os.getenv("TASK_PATH", config_path)

        with open(task_path, "r", encoding="utf-8") as f:
            self.task_dic = json.load(f)
        assert self.task_dic

        self.language = os.getenv('TASK_LANGUAGE', 'English')
        self.dataset = os.getenv('TASK_DATASET', 'healthcare dialogue')
        self.admin_email = os.getenv('ADMIN_EMAIL', 'admin@example.com')

        logging.info(f'This is the {self.language} language system which is using {self.dataset} dataset.')
        self.all_task_done = False

    def get_all_results(self):
        try:
            collection = pymongo.db['final_submission']
            entries = collection.find({})
            formatted_results = []
            for entry in entries:
                formatted_entry = {k: str(v) if isinstance(v, ObjectId) else v for k, v in entry.items()}
                formatted_results.append(formatted_entry)

            return formatted_results
        except Exception as e:
            logging.error('Error fetching data from result collection', exc_info=True)
            return []

    def count_completed_tasks(self, user_email):
        try:
            collection = pymongo.db['task_info']
            completed_count = collection.count_documents({"user_email": user_email, "complete": True})
            return completed_count
        except Exception as e:
            logging.error(f"Error counting completed tasks for {user_email}: {e}", exc_info=True)
            return 0



    def _format_task_response(self, task, user_email):
        dial_task = json.loads(TaskInfo(**task).task_info)
        return {
            "task_id": task["task_id"],
            "task": dial_task,
            "language": self.language,
            "dataset": self.dataset,
            "completed_tasks": self.count_completed_tasks(user_email)
        }

    def get_task(self, user_email):
        """
        Assign an unfinished task to a user, or return the user's existing locked task.
        Expired locks can be reclaimed after three hours.
        """
        with self.lock:
            try:
                collection = pymongo.db['task_info']
                current_time = datetime.now()
                update_lock = {
                    "$set": {
                        "user_email": user_email,
                        "locked": True,
                        "ttl": current_time
                    }
                }

                existing_task = collection.find_one_and_update(
                    {
                        "complete": False,
                        "locked": True,
                        "user_email": user_email
                    },
                    update_lock,
                    return_document=ReturnDocument.AFTER,
                    sort=[('_id', 1)]
                )
                if existing_task:
                    logging.info(f'Returned existing task {existing_task["task_id"]} to {user_email}')
                    return self._format_task_response(existing_task, user_email)

                task = collection.find_one_and_update(
                    {
                        "complete": False,
                        "$or": [
                            {"locked": False},
                            {"locked": True, "ttl": {"$lt": current_time - timedelta(hours=3)}}
                        ]
                    },
                    update_lock,
                    return_document=ReturnDocument.AFTER,
                    sort=[('_id', 1)]
                )

                if task:
                    logging.info(f'Assigned task {task["task_id"]} to {user_email}')
                    return self._format_task_response(task, user_email)

                return None

            except Exception as e:
                logging.error(f'Error assigning task to {user_email}: {str(e)}', exc_info=True)
                raise
