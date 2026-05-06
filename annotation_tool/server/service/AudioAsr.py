import logging
from openai import OpenAI
import os
from datetime import datetime



from init import pymongo
from utils.GridFs import GridFs
from dao.TaskItemSubmission import TaskItemSubmission
from dao.TaskSubmission import TaskSubmission
from dao.FinalSubmission import FinalSubmission


class AudioAsr:

    def __init__(self):
        self.client = self.load_model(Online_model='small')
        self.GridFs = GridFs('AudioFile')

    


    def load_model(self,whisper_model = None,Online_model= None):
        if whisper_model:
            import whisper
            model = whisper.load_model(whisper_model)
            return model
        elif Online_model:
            return self.load_openai_key()
        else:
            return self.client.models.list()


    def load_openai_key(self):
        """
        This function loads the OpenAI API key from the environment variable KEY_PATH.
        """
        key_path = os.getenv("KEY_PATH",'/server/key/openai.key')
        # key_path = os.getenv("KEY_PATH",'/Users/hu/Documents/key/openai.key')
        if os.path.exists(key_path):
            with open(key_path, 'r') as file:
                openai_api_key = file.read().strip()
                os.environ['OPENAI_API_KEY'] = openai_api_key
                logging.info("API Key has been set successfully.")
        return OpenAI()
    
    def get_asr_result(self, audio_file_path, whisper_model = None):
        """
        This function takes an audio file as a byte object and returns the transcription result from OpenAI's Whisper model.

        :param audio_file_byte: Byte object of the audio file
        :return: Transcription result from OpenAI's Whisper model

        """
        
        try:
            if whisper_model:
                result = self.client.transcribe(audio_file_path)
                transcription = result['text']
            else:
                with open(audio_file_path, "rb") as audio_file_byte:
                    result = self.client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file_byte
                    )
                    transcription = result.text
            return transcription
        except Exception as e:
            logging.info(f"An error occurred",exc_info=True)
            return None


    

    def audio_result_insert(self, audio_file, user, asr_string, origin_asr,task_id, turn_id, language):
        """
        This function stores the transcription and audio result in the MongoDB database as TaskSubmission and TaskItemSubmission.

        :param audio_file: Byte object of the audio file
        :param user: the user object from User.py
        :param asr_string: Transcription result from user modify
        :param origin_asr: Transcription result from OpenAI's Whisper model
        :param task_id: Task ID of the task for which the transcription result is needed
        :param turn_id: Turn ID of the turn for which the transcription result is needed
        :param language: Language of the audio file
        :return: None
        """
        try:
            user_id = user.id
            user_email = user.email
            with open(audio_file, 'rb') as audio_file:
                file_id = self.GridFs.insertFile(audio_file,filename = f"{user_id}_{task_id}_{turn_id}.wav")

            new_submit_taskitem = TaskItemSubmission(asr_result=origin_asr,transcription=asr_string,
                                                    audio_name=f"{user_id}_{task_id}_{turn_id}.wav",turn_id = turn_id)
            now_datetime = datetime.now()
            user_task = pymongo.db['task_submission'].find_one({'user_email': user_email, 'task_id': task_id})
            if user_task is None:
                user_task = TaskSubmission(user_email=user_email, task_id=task_id,
                                        submission_list=[new_submit_taskitem], create_time=now_datetime,language =language)
            else:
                user_task["submission_list"].append(new_submit_taskitem)
                user_task = TaskSubmission(user_email=user_task["user_email"], task_id=user_task["task_id"],
                                            submission_list=user_task["submission_list"], create_time=now_datetime,language =user_task["language"])
            pymongo.db['task_submission'].update_one({'user_email': user_email, 'task_id': task_id},
                                                    {'$set': user_task.model_dump()}, upsert=True)

            return 'audio_result_insert success'
            
        except Exception as e:
            logging.info(f"An error occurred",exc_info=True)
            return 'audio_result_insert fail'


    def final_result_submission(self, asr_result_list, transcription_list, audio_file_list,task_id,user_id,language,user_email, start_time):
        """
        This function stores the final transcription result in the MongoDB database as TaskSubmission and TaskItemSubmission.
        """
        result_list = []
        for i in range(len(audio_file_list)):
            filename = 'final_' + str(user_id) + '_' + audio_file_list[i].filename
            filepath = 'final_submit/' + str(user_id) + '_' + str(task_id)
            if not os.path.exists(filepath):
                os.makedirs(filepath)
            audio_file_list[i].save(os.path.join(filepath, filename))
            transcription_name = str(i) + '_transcription.txt'
            asr_result_name = str(i) + '_asr_result.txt'
            if transcription_list[i]:
                with open(os.path.join(filepath, transcription_name), 'w') as f:
                    f.write(transcription_list[i])
            if asr_result_list[i]:
                with open(os.path.join(filepath, asr_result_name), 'w') as f:
                    f.write(asr_result_list[i])

            new_submit_taskitem = TaskItemSubmission(asr_result=asr_result_list[i],transcription=transcription_list[i],
                                                     audio_name=filename,turn_id = i)
            result_list.append(new_submit_taskitem)
            with open(os.path.join(filepath, filename), 'rb') as audio_file:
                self.GridFs.insertFile(audio_file,filename = filename)

        new_final_submission = FinalSubmission(language=language,result_list=result_list,task_id=task_id,user_email=user_email, submission_time=datetime.now(), start_time = start_time)
        pymongo.db['final_submission'].insert_one(new_final_submission.model_dump())

        return 'final_result_submission success'


    


    def mongodb_asr_result_collect(self, user_name,task_id):
        """
        This function retrieves the transcription result from the MongoDB database for a given user and task.

        :param user_name: User name of the user who uploaded the audio file
        :param task_id: Task ID of the task for which the transcription result is needed
        :return: task result from the MongoDB database
        """
        user_task = pymongo.db['task_submission'].find_one({'user': user_name, 'task_id': task_id})
        if user_task is not None:
            return user_task['task_item']
        else:
            return None
        
    

    
