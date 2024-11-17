import json
import sys
import speech_recognition as sr
import copilot
import os
from server import send_message


def copilot_listen():
    r = sr.Recognizer()

    with sr.Microphone() as source:
        input = ""
        while True:
            # Grab initial input
            r.adjust_for_ambient_noise(source, duration=2)
            send_message({"route": "message",
                          "data": {"message": 'Say something! Say "Exit" to stop.'}})
            audio = r.listen(source, timeout=7, phrase_time_limit=5)
            try:
                input = r.recognize_google(audio, language="en-US")
            except sr.UnknownValueError:
                print("Could not understand audio", file=sys.stderr)

            if input == "exit":
                print("Exiting...", flush=True)
                break

            prompt = input
            while True:
                # Continue existing prompt
                print(prompt, flush=True)
                completion = copilot.HandleInput(prompt)
                prompt += completion
                print(f"Data:{{{completion}\n}}", flush=True)
                send_message({"route": "message",
                              "data": {"message": 'Continue? ("Yes"/"No")'}})
                while True:
                    try:
                        audio = r.listen(source, timeout=10,
                                         phrase_time_limit=3)
                        input = r.recognize_google(audio, language="en-US")
                    except sr.UnknownValueError:
                        print("Could not understand audio", file=sys.stderr)
                        continue
                    break
                if input == "no":
                    break


def Listen():
    r = sr.Recognizer()

    try:
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source)
            while (True):
                send_message({"route": "message",
                              "data": {"message": 'Please give your command. Listening...'}})

                try:
                    audio = r.listen(source, timeout=7, phrase_time_limit=5)
                    cmd = r.recognize_google(audio)
                    send_message({"route": "data",
                                  "data": {"text": cmd}})
                    return

                except (Exception, sr.exceptions.WaitTimeoutError) as e:
                    if type(e) != sr.exceptions.WaitTimeoutError and type(e) != sr.exceptions.UnknownValueError:
                        send_message({"route": "message",
                                      "data": {"message": 'There was an issue with the microphone input.'}})
    except OSError:
        send_message({"route": "message",
                      "data": {"message": 'Microphone not detected. Please check your microphone connection.'}})
        exit(0)


if __name__ == "__main__":
    if os.environ.get("MODE") == "COPILOT":
        copilot.watch_authentication(copilot_listen)
        copilot.authenticate()
    elif os.environ.get("MODE") == "OTHER":
        Listen()
