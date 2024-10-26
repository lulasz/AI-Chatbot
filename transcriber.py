import json
from vosk import SetLogLevel, Model, KaldiRecognizer

class Transcriber:
    def __init__(self, model_path):
        """Initialize the Transcriber with the Vosk model."""
        SetLogLevel(-1)
        self.model = Model(model_path)

    def transcribe_audio_data(self, audio_data, sample_rate=44100):
        """Transcribe the audio data provided as a numpy array."""
        # Initialize the recognizer with the model and sample rate
        recognizer = KaldiRecognizer(self.model, sample_rate)
        
        # Convert audio data to byte format as KaldiRecognizer requires bytes input
        audio_bytes = audio_data.tobytes()

        # Transcription result
        transcript = ""

        # Feed the audio bytes in chunks
        chunk_size = 4000
        for start in range(0, len(audio_bytes), chunk_size):
            chunk = audio_bytes[start:start + chunk_size]
            if recognizer.AcceptWaveform(chunk):
                result = recognizer.Result()
                transcript += json.loads(result)["text"] + " "
            else:
                recognizer.PartialResult()
        
        # Get the final transcription result
        final_result = recognizer.FinalResult()
        transcript += json.loads(final_result)["text"]

        return transcript.strip()
