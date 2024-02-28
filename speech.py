import os
import time
import requests
import json
from dotenv import load_dotenv
import azure.cognitiveservices.speech as speechsdk
from scipy.io import wavfile


class speechMethods:
    def __init__(self):
        self.access_variables = self.load_variables()
        self.sample_wav_file = './data-feeds/wav-files/martha.wav'
        self.text_to_speech_file = './data-feeds/gettysburg-short.txt'
        self.text_to_speak = self.load_text(filename=self.text_to_speech_file)
        self.location = self.access_variables['speech_location']
        self.transcription_path = f'https://{self.location}.api.cognitive.microsoft.com/speechtotext/v3.0/transcriptions'
        self.headers = {'Content-Type': 'application/json', 'Ocp-Apim-Subscription-Key': self.access_variables['speech_key']}

    # Load sub, tenant ID variables 
    def load_variables(self):
        """Load access variables"""
        load_dotenv('./variables.env')
        auth_dict = {
                "speech_key":os.environ['SPEECH_KEY'],
                "speech_endpoint":os.environ['SPEECH_ENDPOINT'],
                "speech_location":os.environ['SPEECH_LOCATION'],
                "blob_container_sas_url":os.environ['BLOB_CONTAINER_SAS_URL']
                }
        return auth_dict

    def from_file(self, conversationfilename=None):

        speech_config = speechsdk.SpeechConfig(subscription=self.access_variables['speech_key'],
                                               region=self.access_variables['speech_location'])

        audio_config = speechsdk.audio.AudioConfig(filename=conversationfilename)
        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

        done = False

        def stop_cb(evt: speechsdk.SessionEventArgs):
            """callback that signals to stop continuous recognition upon receiving an event `evt`"""
            print('CLOSING on {}'.format(evt))
            nonlocal done
            done = True

        text_results = []

        def get_final_text(evt):
            text_results.append(evt.result.text)

        # Connect callbacks to the events fired by the speech recognizer
        speech_recognizer.recognizing.connect(lambda evt: print('RECOGNIZING: {}'.format(evt)))
        speech_recognizer.recognized.connect(lambda evt: print('RECOGNIZED: {}'.format(evt)))
        speech_recognizer.session_started.connect(lambda evt: print('SESSION STARTED: {}'.format(evt)))
        speech_recognizer.session_stopped.connect(lambda evt: print('SESSION STOPPED {}'.format(evt)))
        speech_recognizer.canceled.connect(lambda evt: print('CANCELED {}'.format(evt)))
        speech_recognizer.recognized.connect(get_final_text)
        # Stop continuous recognition on either session stopped or canceled events
        speech_recognizer.session_stopped.connect(stop_cb)
        speech_recognizer.canceled.connect(stop_cb)

        # Start continuous speech recognition
        speech_recognizer.start_continuous_recognition()
        while not done:
            time.sleep(.5)

        speech_recognizer.stop_continuous_recognition()
        print(text_results)

    def from_mic(self):
        # Create a speech configuration
        speech_config= speechsdk.SpeechConfig(subscription=self.access_variables['speech_key'],
                region=self.access_variables['speech_location'])
        transcriber = speechsdk.transcription.ConversationTranscriber(speech_config)
        # speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)
        print('Start saying something...When you need to finish, pause for 2 seconds and say "Comcast".')
        # speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)

        done = False

        def stop_cb(evt: speechsdk.SessionEventArgs):
            """callback that signals to stop continuous transcription upon receiving an event `evt`"""
            print('CLOSING {}'.format(evt))
            nonlocal done
            done = True

        # Subscribe to the events fired by the conversation transcriber
        transcriber.transcribed.connect(lambda evt: print('TRANSCRIBED: {}'.format(evt)))
        transcriber.session_started.connect(lambda evt: print('SESSION STARTED: {}'.format(evt)))
        transcriber.session_stopped.connect(lambda evt: print('SESSION STOPPED {}'.format(evt)))
        transcriber.canceled.connect(lambda evt: print('CANCELED {}'.format(evt)))
        transcriber.session_stopped.connect(stop_cb)
        transcriber.canceled.connect(stop_cb)

        transcriber.start_transcribing_async()

        while not done:
            # No real sample parallel work to do on this thread, so just wait for user to type stop.
            # Can't exit function or transcriber will go out of scope and be destroyed while running.
            print('type "stop" then enter when done')
            stop = input()
            if (stop.lower() == "stop"):
                print('Stopping async recognition.')
                transcriber.stop_transcribing_async()
                break


    def send_batch_transcribe_request(self):
        body = {
                #"contentUrls":[<specific SAS URL to file>],
                 "contentContainerUrl": self.access_variables['blob_container_sas_url'],
          "properties": {
            "diarizationEnabled": "false",
            "wordLevelTimestampsEnabled": "true",
            "punctuationMode": "DictatedAndAutomatic",
            "profanityFilterMode": "Masked"
          },
          "locale": "en-US",
          "displayName": "Transcription using default model for en-US"}

        response = requests.post(self.transcription_path, headers=self.headers, json=body)
        status, reason, resp_headers = response.status_code, response.reason, response.headers
        print(f"response status code: {status}")
        print(f"response status: {reason}")
        print(f"response headers: {resp_headers}")
        resp_headers_dict = dict(resp_headers)
        request_id = resp_headers_dict['Location'].split('/transcriptions/')[1]
        print(f'Request ID: {request_id}')

    def get_batch_transcripts(self, request_id=None):
        """Get transcription result; do this manually in an ipython terminal"""

        # Get request id, and use this to pulse a while loop
        path = self.transcription_path + '/' + str(request_id) + '/files'
        response = requests.get(path, headers=self.headers)
        status, reason, resp_headers, resp_content = response.status_code, response.reason, response.headers, response.content
        print(f"response status code: {status}")
        print(f"response status: {reason}")
        print(f"response headers: {resp_headers}")
        print(f"response content: {resp_content}")
        resp_content_json = json.loads(resp_content.decode('utf-8'))
        #print(resp_content_json)

        if resp_content_json['values'] == []:
            print('Request still processing......')
        else:
            returned_values = resp_content_json['values']
            for i,v in enumerate(returned_values):
                contentUrl = v['links']['contentUrl']
                print(f'Returned content URL: {contentUrl}')
                # Pending, add code to fetch and download transcript

    def load_text(self, filename=None):
        """Load text to speak"""
        with open(filename) as f:
            data = f.read()
        return data

    def speech_from_txt_file(self):
        text = self.text_to_speak #input()
        print(f"Text to speak: {text}")
        # Create a speech configuration
        speech_config= speechsdk.SpeechConfig(subscription=self.access_variables['speech_key'],
                endpoint=self.access_variables['speech_endpoint'])
        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
        result = speech_synthesizer.speak_text_async(text).get()

        # Check result
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print("Speech synthesized to speaker for text [{}]".format(text))
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            print("Speech synthesis canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                if cancellation_details.error_details:
                    print("Error details: {}".format(cancellation_details.error_details))
            print("Did you update the subscription info?")
