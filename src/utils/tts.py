import pyttsx3

# Initialize the pyttsx3 engine
engine = pyttsx3.init()

# Get the list of voices
voices = engine.getProperty('voices')

# Iterate through the voices and print their properties
for voice in voices:
    print(f"Voice ID: {voice.id}")
    print(f"Voice Name: {voice.name}")
    print(f"Voice Age: {voice.age}")
    print(f"Voice Gender: {voice.gender}")
    print(f"Voice Languages: {voice.languages}")
    print("-" * 20)

# Stop the engine
engine.stop()