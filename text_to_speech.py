import pyttsx3

class TextToSpeech:
    def __init__(self):
        # Initialize the TTS engine
        self.engine = pyttsx3.init()
        self.set_properties()

    def set_properties(self, rate=150, volume=1.0, voice_id=None):
        """Set the speech rate, volume, and voice."""
        self.engine.setProperty('rate', rate)       # Speed of speech in words per minute
        self.engine.setProperty('volume', volume)   # Volume (0.0 to 1.0)
        if voice_id:
            self.engine.setProperty('voice', voice_id)  # Set specific voice ID

    def read_aloud(self, text):
        """Read the given text aloud."""
        self.engine.say(text)
        self.engine.runAndWait()

    def list_voices(self):
        """List available voices on the system."""
        voices = self.engine.getProperty('voices')
        for voice in voices:
            print(f"ID: {voice.id}, Name: {voice.name}")

    def set_voice(self, voice_id):
        """Set the voice by its ID."""
        self.engine.setProperty('voice', voice_id)
