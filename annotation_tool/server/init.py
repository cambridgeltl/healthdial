from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_pymongo import PyMongo
from flask_cors import CORS
import os
import json
from datetime import datetime
from dao.TaskInfo import TaskInfo
from pymongo import ReturnDocument


bcrypt = Bcrypt()
pymongo = PyMongo()
jwt = JWTManager()
cors = CORS()

def init_app(app):
    bcrypt.init_app(app)
    jwt.init_app(app)
    pymongo.init_app(app)
    cors.init_app(app)
    create_task_info_indexes()
    push_all_tasks_to_database()
    assign_all_finished_tasks()


def create_task_info_indexes():
    task_collection = pymongo.db.task_info
    task_collection.create_index("task_id", unique=True)
    task_collection.create_index([("complete", 1), ("locked", 1), ("ttl", 1)])
    task_collection.create_index([("user_email", 1), ("complete", 1), ("locked", 1)])




def push_all_tasks_to_database():
    """Push all tasks to `task_info`, ensuring only one process runs this function and releasing the lock afterward."""
    task_collection = pymongo.db.task_info
    lock_collection = pymongo.db.locks

    # Attempt to acquire the lock
    lock = lock_collection.find_one_and_update(
        {"name": "init_task_lock"},
        {"$setOnInsert": {"locked": True, "timestamp": datetime.now()}},
        upsert=True,
        return_document=ReturnDocument.BEFORE
    )

    if lock:  # Lock already exists
        print("Another process is initializing tasks. Skipping initialization.")
        return False

    print("Initializing tasks...")

    try:
        task_path = os.getenv("TASK_PATH")
        if not task_path:
            raise ValueError("TASK_PATH is not configured.")

        with open(task_path, 'r', encoding='utf-8') as f:
            tasks = json.load(f)

        for task_id, task_data in tasks.items():
            task = TaskInfo(
                task_id=task_data['task_id'],
                task_info=json.dumps(task_data, ensure_ascii=False),
                user_email=None,
                complete=False,
                locked=False,
                ttl=None,
            )

            task_collection.update_one(
                {"task_id": task.task_id},
                {"$setOnInsert": task.model_dump()},
                upsert=True
            )

        print("Task initialization completed.")

    except Exception as e:
        print(f"Error during task initialization: {e}")

    finally:
        # Ensure the lock is released no matter what
        lock_collection.delete_one({"name": "init_task_lock"})
        print("Lock released.")

    return True


def assign_all_finished_tasks():
    """
    Mark all finished tasks as complete, ensuring atomic updates.
    """
    submission_collection = pymongo.db.final_submission
    task_collection = pymongo.db.task_info

    submissions = submission_collection.find()

    for sub in submissions:
        result = task_collection.update_one(
            {
                "task_id": sub["task_id"],
                "$or": [
                    {"complete": {"$exists": False}},  # Task has no "complete" field
                    {"complete": False}  # Task is marked incomplete
                ]
            },
            {
                "$set": {
                    "complete": True,
                    "user_email": sub["user_email"],
                }
            }
        )

        if result.modified_count == 0:
            print(f"Task {sub['task_id']} was not updated (possibly already completed).")
        else:
            print(f"Task {sub['task_id']} updated successfully.")

    return True
