import speech_recognition as sr

r = sr.Recognizer()
audiofile = sr.AudioFile('audioname.wav')

with audiofile as source:
    audio = r.record(source)

print(r.recognize_google(audio))
