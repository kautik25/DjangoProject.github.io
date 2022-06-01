from django.test import TestCase

# Create your tests here.

# speech to text for otp

import speech_recognition as sr

r = sr.Recognizer()

with sr.Microphone() as source:
    print('Speak Anything')
    audio = r.listen(source)

    try:
        text = r.recognize_google(audio)
        print('You said :{}'.format(text))
        print(''.join(text))
    except:
        print('Sorry, could not hear')