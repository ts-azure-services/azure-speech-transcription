# azure-speech-transcription
A repo to consolidate a few examples of speech-to-text (STT) and text-to-speech (TTS) with setup and practice
code. Methods and examples shown below that can be run in a python/ipython interpreter. This excludes additional workflows around translation, intent
recognition, speaker and keyword recognition.

```python
# Import the class, with demo code
from speech import speechMethods

# Instantiate the object
t = speechMethods()
```

## Real-time transcription
```python
## REAL TIME TRANSCRIPTION
#----------------------------
# Run a sample transcription from speech in a mic
# To end the session, say "Lincoln", which is the stop keyword
t.from_mic()

# Run a sample transcription from a file
t.from_file(wav_file=t.sample_wav_file)
```

## Batch Transcription
```python
#----------------------------
# Send a batch transcription request
# Take note of the request ID
t.send_batch_transcribe_request()
"""Sample successful response:
response status code: 201
response status: Created
response headers: {...}
Request ID: xxxx
"""

# Use the request id from the prior operation to pulse for links to the transcripts
# Once done, you should get links to the transcripts of each of the files in batch
t.get_batch_transcripts("xxxx")

# Text to speech
# This will narrate out the first few lines of the Gettysburg address
t.speech_from_txt_file()
```
