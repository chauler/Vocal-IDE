import speech_recognition as sr
from server import send_message

"""
Sends the text of the voice input to the server.
"""
def basic_listen():
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