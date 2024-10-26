import sounddevice as sd
import numpy as np

class AudioRecorder:
    def __init__(self, threshold=0.1, silence_duration=1.5, samplerate=44100):
        self.threshold = threshold
        self.silence_duration = silence_duration
        self.samplerate = samplerate
        self.audio_data = []  # Store audio samples in memory
        self.silent_time = 0  # Track the duration of silence
        self.chunk_duration = 0.3  # Duration of each audio chunk in seconds
        self.pre_buffer_duration = 0.5  # Duration to pre-buffer audio in seconds
        self.recording = False  # Track if currently recording
        self.state = "start"
        
    def record(self):
        self.recording = True  # Set recording state
        # Pre-buffering audio
        self.state = "prepare"
        pre_buffer = sd.rec(int(self.pre_buffer_duration * self.samplerate), samplerate=self.samplerate, channels=1, dtype='float64')
        sd.wait()  # Wait for the pre-buffering to finish
        self.audio_data.append(pre_buffer)  # Append pre-buffered audio

        self.state = "record"
        while self.recording:
            # Record a chunk of audio
            chunk = sd.rec(int(self.chunk_duration * self.samplerate), samplerate=self.samplerate, channels=1, dtype='float64')
            sd.wait()  # Wait for the chunk to finish recording

            self.audio_data.append(chunk)  # Append recorded chunk to audio_data
            average_amplitude = np.abs(chunk).mean()  # Calculate the average amplitude
            
            # Check for silence
            if average_amplitude < self.threshold:
                self.silent_time += self.chunk_duration  # Increment silent time
                if self.silent_time >= self.silence_duration:  # Check if silence duration exceeds limit
                    self.state = "silence"
                    self.recording = False  # Stop recording
            else:
                self.silent_time = 0  # Reset silence counter if sound is detected

        # Concatenate recorded audio chunks and convert to int16
        self.audio_data = np.concatenate(self.audio_data)
        self.audio_data = np.clip(self.audio_data * 32767, -32768, 32767).astype(np.int16)  # Clamping values to prevent overflow
        self.state = "done"

    def get_audio_data(self):
        return self.audio_data

    def get_state(self):
        return self.state