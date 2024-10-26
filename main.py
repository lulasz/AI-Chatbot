import os
import json
import time
import readline
import requests
import subprocess
import threading
import syntax_highlighter
from spinner import Spinner
from audio_recorder import AudioRecorder
from transcriber import Transcriber
from text_to_speech import TextToSpeech

# Load configuration from config.json
with open("config.json", "r") as f:
    config = json.load(f)

# Constants from config file
APP_NAME = config["APP"]["name"]
VERSION = config["APP"]["version"]

MODEL_NAME = config["OLLAMA"]["model_name"]
TEMPERATURE = config["OLLAMA"]["temperature"]
SEED = config["OLLAMA"]["seed"]
TYPING_DELAY = config["OLLAMA"]["typing_delay"]
OLLAMA_ADDRESS = config["OLLAMA"]["address"]

VOSK_PATH = config["VOSK"]["path"]
VOSK_MODEL_NAME = config["VOSK"]["model_name"]

AUDIO_REC_THRESHOLD = config["AUDIO_RECORDER"]["threshold"]
AUDIO_REC_SILENCE_DURATION = config["AUDIO_RECORDER"]["silence_duration"]
AUDIO_REC_SAMPLERATE = config["AUDIO_RECORDER"]["samplerate"]

VOICE_ID = config["VOICE"]["id"]
VOICE_RATE = config["VOICE"]["rate"]
VOICE_VOLUME = config["VOICE"]["volume"]

# Instances
highlighter = syntax_highlighter.SyntaxHighlighter()
tts = TextToSpeech()
spinner = Spinner("...")

# Initialize conversation history
conversation_history = []
is_voice = False

def get_models():
    """List available models using the 'ollama' command."""
    output = subprocess.check_output(['ollama', 'list'], text=True)
    return [line.split()[0] for line in output.strip().split('\n')]

def generate_response(model_name, conversation_history, seed, temperature):
    """Generate a response from the model based on the conversation history."""
    global is_voice

    data = {
        "model": model_name,
        "messages": conversation_history,
        "stream": False,
        "suffix": "return result",
        "options": {
            "seed": seed,
            "temperature": temperature
        }
    }

    headers = {'Content-Type': 'application/json'}

    # Start the streaming response
    response = requests.post(OLLAMA_ADDRESS, json=data, headers=headers, stream=True)

    spinner.stop() 
    time.sleep(0.5)

    if response.status_code == 200:
        complete_message = ""

        # Processing the streaming response
        for line in response.iter_lines():
            if line:
                try:
                    model_response = json.loads(line)

                    # Check for 'message' or 'response'
                    if "message" in model_response:
                        message_content = model_response["message"].get("content", "")
                        done = model_response["message"].get("done", False)
                    elif "response" in model_response:
                        message_content = model_response["response"].get("content", "")
                        done = model_response["response"].get("done", False)
                    else:
                        done = False
                
                    # Read aloud
                    if is_voice:
                        # Read the text aloud
                        tts.read_aloud(message_content)
                        is_voice = False
                    message_content = "[ollama]:: " + highlighter.highlight_code(message_content)

                    # Print each part of the response with a typing effect
                    for char in message_content:
                        print(char, end='', flush=True)  # Print char without newline
                        time.sleep(TYPING_DELAY)  # Delay between each character

                    # If 'done' is True, break the loop
                    if done:
                        break

                except json.JSONDecodeError:
                    print("\nFailed to parse JSON response.")
                    return None

        print()  # New line after finishing the response
        return complete_message.strip() if complete_message else "Couldn't process it."
    else:
        print("\nFailed to get response from the model.")
        return None

def clear_console():
    """Clear the console based on the operating system."""
    os.system('cls' if os.name == 'nt' else 'clear')

def show_help():
    """Display available commands."""
    help_text = """
Available commands:
- /voice: Start voice assistant
- /voice list: List all available voices
- /voice set "value": Sets the voice by ID
- /help: Show this help message
- /clear: Clear the console
- /exit: End the conversation
"""
    print(help_text)

def record_voice():
    """Record audio and transcribe it."""
    # Initialize and record audio
    audio_recorder = AudioRecorder(threshold=AUDIO_REC_THRESHOLD, silence_duration=AUDIO_REC_SILENCE_DURATION, samplerate=AUDIO_REC_SAMPLERATE)
    
    # Show that it is doing something
    spinner.set_text("Recording ...", True)
    
    # Start spinner in a separate thread
    spinner_thread = threading.Thread(target=spinner.loading_circle)
    spinner_thread.start()
    
    # Start recording
    audio_recorder.record()

    audio_data = audio_recorder.get_audio_data()
    
    # Initialize the transcriber and transcribe the audio data
    transcriber = Transcriber(VOSK_PATH + VOSK_MODEL_NAME)
    transcription = transcriber.transcribe_audio_data(audio_data)

    spinner.stop()

    # Print the transcription result
    print("[voice]::", transcription)

    return transcription

def conversation(user_input):
    """Handle the conversation flow."""
    conversation_history.append({"role": "user", "content": user_input})
    assistant_response = generate_response(MODEL_NAME, conversation_history, SEED, TEMPERATURE)

    if assistant_response:
        # Append assistant response to conversation history after printing
        conversation_history.append({"role": "assistant", "content": assistant_response})

def main():
    """Main function to run the console chatbot."""

    global is_voice

    clear_console()

    tts.set_properties(VOICE_RATE, VOICE_VOLUME, VOICE_ID)

    # List available models
    models = get_models()
    # Select model from the list or use the predefined one
    if MODEL_NAME not in models:
        print(f"{APP_NAME}\nWarning: The specified model '{MODEL_NAME}' is not available.")
        return
    else:
        print(f"{APP_NAME} {VERSION} [Ollama:{MODEL_NAME}] [Vosk:{VOSK_MODEL_NAME}] [TTS:{VOICE_ID}]")

    # Contextual priming
    pre_prompt = "Always answer very short, but act like a professional. Start over."
    conversation_history.append({"role": "user", "content": pre_prompt})
    conversation_history.append({"role": "assistant", "content": "Alright"})
 
    print("Type '/help' for a list of commands")
    show_help()
    
    # Initialize readline to enable command history
    history_file = os.path.expanduser(".chatbot_history")
    
    # Load the command history from file at startup
    try:
        readline.read_history_file(history_file)
    except FileNotFoundError:
        pass  # No history file exists yet

    while True:
        user_input = input("[you]:: ")

        # Voice assistant once
        if user_input.lower() == '/voice':
            is_voice = True
            user_input = record_voice()
        
        if user_input.lower() == "/voice list":
            # List available voices
            print("Available voices:")
            tts.list_voices()
            continue
                
        if user_input.lower().startswith("/voice set "):
            value = user_input[len("/voice set "):].strip()
            tts.set_voice(value)
            continue

        # Check for help command
        if user_input.lower() == '/help':
            show_help()
            continue
        
        # Check for clear command
        if user_input.lower() == '/clear':
            clear_console()
            continue
        
        if user_input.lower() == '/exit':
            print("Ending the chat.")
            break
        
        # Show that it is doing something
        spinner.set_text("Generating ...", True)

        # Start spinner in a separate thread
        spinner_thread = threading.Thread(target=spinner.loading_circle)
        spinner_thread.start()

        # Update conversation history
        conversation(user_input)
        
        # Wait for the spinner thread to finish
        spinner_thread.join()

        # Save input to history
        # readline.add_history(user_input)

    # Save history on exit
    readline.write_history_file(history_file)

if __name__ == "__main__":
    main()
