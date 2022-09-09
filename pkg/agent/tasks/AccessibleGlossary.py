import json
import os
import requests
import time

from .AbstractTask import AbstractTask, TaskNames

from pkg.agent.tasks.lib import accessibleglossary

VIDEO_GLOSSARY_KEY = 'glossary'
VIDEO_PHRASEHINTS_KEY = 'phraseHints'

class AccessibleGlossary(AbstractTask):

    @staticmethod
    def get_name():
        return TaskNames.AccessibleGlossary
    
    def generate_accessible_glossary(self, video_id, video, phrase_hints, readonly):
        # Look up definitions for generated phrases
        self.logger.info(' [%s] AccessibleGlossary looking up terms...' % video_id)
        
        ''' 
        TODO: 829 Check if terms has been looked up
        all_phrases = [str(scene[SCENE_PHRASES_KEY]) for scene in scenes]
        self.logger.debug(' [%s] PhraseHinter found phrases' % (video_id))
        '''

        try:
            self.logger.info(' [%s] AccessibleGlossary generating term descriptions...' % video_id)
            terms, descriptions = accessibleglossary.look_up(phrase_hints)

            if readonly:
                self.logger.info(' [%s] AccessibleGlossary running as READONLY.. term descriptions have not been saved: %s' % (video_id, terms.join('')))
            else:
                # save generated terms to glossary table in api
                resp = requests.post(url='%s/api/Task/UpdateGlossary?videoId=%s' % (self.target_host, video_id),
                                     headers={'Content-Type': 'application/json', 'Authorization': 'Bearer %s' % self.jwt},
                                     data=json.dumps({"Terms": terms, "Descriptions": descriptions}))
                resp.raise_for_status()

            return video
        except Exception as e:
            self.logger.error(
                ' [%s] AccessibleGlossary failed to look up terms in videoId=%s: %s' % (video_id,
                    video_id, str(e)))
            return
    
    def run_task(self, body, emitter):
        self.logger.info(' [.] AccessibleGlossary message recv\'d: %s' % body)
        video_id = body['Data']
        parameters = body.get('TaskParameters', {})
        force = parameters.get('Force', False)
        readonly = parameters.get('ReadOnly', False)
        self.logger.info(' [%s] AccessibleGlossary started on videoId=%s...' % (video_id, video_id))

        # fetch video metadata by id to get path
        video = self.get_video(video_id=video_id)

        # short-circuit if we already have phrase hints
        if not force and VIDEO_GLOSSARY_KEY in video and video[VIDEO_GLOSSARY_KEY]:
            # TODO: trigger TranscriptionTask
            self.logger.warning(' [%s] Skipping AccessibleGlossary: glossary already exist' % video_id)
            return

        if video is None:
            self.logger.error(' [%s] AccessibleGlossary FAILED to lookup terms in videoId=%s' % (video_id, video_id))
            return

        # TODO: Check for empty phrases / error-handling
        phrases = video[VIDEO_PHRASEHINTS_KEY]
        if len(phrases) == 0:
            self.logger.error(' [%s] AccessibleGlossary FAILED for videoId=%s: no detected phrases found' % (video_id, video_id))

        self.generate_accessible_glossary(video_id, video, phrases, readonly)

        self.logger.info(' [%s] AccessibleGlossary complete!' % video_id)

        return