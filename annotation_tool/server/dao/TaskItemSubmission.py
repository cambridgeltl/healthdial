from pydantic import BaseModel

class TaskItemSubmission(BaseModel):


    transcription: str
    audio_name: str
    asr_result: str
    turn_id: int

    def __repr__(self):
        return f'{self.transcription},{self.audio_name},{self.asr_result},{self.turn_id}'