import json
import os
import requests
import whisper
from .AbstractTask import AbstractTask, TaskNames

class WhisperTranscribe(AbstractTask):
    @staticmethod
    def get_name():
        return TaskNames.WhisperTranscribe

    def transcribe(self, video_id, video, language, model):


    def run_task(self, body, emitter):
        self.logger.info(' [.] WhisperTask message recv\'d: %s' % body)
        video_id = body['Data']
        parameters = body.get('TaskParameters', {})
        # TODO check if I can get custom params
        language = parameters.get('Language', 'en')
        model = parameters.get('Model', 'small')
        self.logger.info(' [%s] Whisper transcription started on videoId=%s...' % (video_id, video_id))

        # Fetch video metadata by id to get path
        video = self.get_video(video_id=video_id)

        # TODO short circuit if transcription already exists

        if video is None:
            self.logger.error(' [%s] WhisperTranscribe FAILED to fetch video with videoId=%s' % (video_id, video_id))
            return

        transcription = self.transcribe(video_id, video, language, model)




