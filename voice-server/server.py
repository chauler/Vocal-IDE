import speech_recognition as sr

r = sr.Recognizer()
with sr.Microphone() as source:
    r.adjust_for_ambient_noise(source)
    print("Say something!", flush=True)
    audio = r.listen(source, timeout=7, phrase_time_limit=5)

    try:
        print("Whisper thinks you said " + r.recognize_whisper(audio, language="english", model="tiny"))
    except sr.UnknownValueError:
        print("Whisper could not understand audio")
    except sr.RequestError as e:
        print(f"Could not request results from Whisper; {e}")