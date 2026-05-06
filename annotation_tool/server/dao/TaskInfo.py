from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TaskInfo(BaseModel):


    task_id: str
    task_info: str
    user_email: Optional[str]
    complete: bool
    locked: bool
    ttl: Optional[datetime]

    def __repr__(self):
        return f'{self.task_id},{self.task_info},{self.user_email},{self.complete},{self.locked}'