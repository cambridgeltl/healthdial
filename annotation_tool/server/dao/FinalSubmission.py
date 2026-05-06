from pydantic import BaseModel
from dao.TaskItemSubmission import TaskItemSubmission
from typing import List
from datetime import datetime  # Import datetime for timestamp

class FinalSubmission(BaseModel):


    result_list: List[TaskItemSubmission]
    task_id: str
    user_email: str
    language: str
    submission_time: datetime  # Add a new field for the timestamp
    start_time: str


    def __repr__(self):
        return f'{self.user_email},{self.task_id},{self.language},{self.result_list}'