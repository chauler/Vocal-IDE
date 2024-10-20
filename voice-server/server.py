import sys
import speech_recognition as sr

r = sr.Recognizer()

with sr.Microphone() as source:
    input = ""
    while input.lower() != "exit":
        r.adjust_for_ambient_noise(source)
        print("Say something!", flush=True)
        audio = r.listen(source, timeout=7, phrase_time_limit=5)
        try:
            input = r.recognize_google(audio, language="en-US")
            print(f"Data:{input}", flush=True)
        except sr.UnknownValueError:
            print("Could not understand audio", file=sys.stderr)
        except sr.RequestError as e:
            print(f"Could not request results from recognizer; {e}", file=sys.stderr)