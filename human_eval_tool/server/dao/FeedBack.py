from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class FeedBack(BaseModel):
    """
    A Pydantic model for representing user feedback in dialogue systems.

    Attributes:
        usefulness (int): The usefulness rating comparing the dialogue system to the WHO website.
        easeOfUse (int): Ease of use rating comparing the dialogue system to the WHO website.
        outputQuality (int): Output quality rating comparing the dialogue system to the WHO website.
        intentionToUse (int): User's future intention to use the dialogue system over WHO website.
        overall (int): Overall satisfaction rating for the dialogue system.
        goal (int): Indicator if the system helped the user achieve their information goal (1: Yes, 2: Partially, 3: No).
        trust (int): Level of trust in the dialogue system compared to WHO website.
        preferredTool (str): User's preferred tool for future health information needs.
        preferredReason (Optional[str]): Optional reason for user's preferred tool choice.
        whoOverall (int): Overall satisfaction rating for the WHO website.
        taskCompletion (int): Level of task completion achieved by using the WHO website (1: All, 2: Most, 3: Some, 4: Little/None).
        feedback (Optional[str]): Additional textual feedback provided by the user.
        create_time (datetime): The timestamp when the feedback was created.
        feedback_user (str): The email of the user providing the feedback.
    """

    usefulness: int
    easeOfUse: int
    outputQuality: int
    intentionToUse: int
    overall: int
    goal: int
    trust: int
    preferredTool: str
    preferredReason: Optional[str] = None
    whoOverall: int
    taskCompletion: int
    feedback: Optional[str] = None
    create_time: datetime
    feedback_user: str

    def __repr__(self):
        return (f'FeedBack(user={self.feedback_user}, overall={self.overall}, goal={self.goal}, '
                f'usefulness={self.usefulness}, easeOfUse={self.easeOfUse}, outputQuality={self.outputQuality})')
