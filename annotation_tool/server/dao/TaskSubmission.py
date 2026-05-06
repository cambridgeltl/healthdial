
from pydantic import BaseModel
from datetime import datetime
from typing import List
from dao.TaskItemSubmission import TaskItemSubmission

class TaskSubmission(BaseModel):

    submission_list: List[TaskItemSubmission]
    create_time: datetime
    user_email: str
    task_id: str
    language: str

    def __repr__(self):
        return f'{self.task_id},{self.user_email},{self.create_time},{self.submission_list},{self.language}'


