from fuzzywuzzy import fuzz
from tts import TTS
from stt import STT
import sounddevice as sd
import soundfile as sf
from random import randint
import datetime

def equ(text, needed):
    return fuzz.ratio(text, needed) >= 45


def execute(text: str):
    print(f"> {text}")
    if 'джарвис' in text.split(' '):
        if equ(text, "команда"):
            tts.text2speech("ответ-озвучка")
            print(f"- {text}")
            # дальнейшая логика
        elif equ(text, 'спасибо'):
            match randint(1, 2):
                case 1:
                    filename = 'sounds/jarvis/thanks/41.wav'
                case 2:
                    filename = 'sounds/jarvis/thanks/54.wav'
            data, fs = sf.read(filename, dtype='float32')
            sd.play(data, fs)
            status = sd.wait()
            print(f"- {text}")
        elif equ(text, "выключись"):
            match randint(1, 2):
                case 1:
                    filename = 'sounds/jarvis/bye/46.wav'
                case 2:
                    filename = 'sounds/jarvis/bye/45.wav'
            data, fs = sf.read(filename, dtype='float32')
            sd.play(data, fs)
            status = sd.wait()
            print(f"- {text}")
            raise SystemExit
        elif text == 'джарвис':
            match randint(1, 2):
                case 1:
                    filename = 'sounds/jarvis/here/19.wav'
                case 2:
                    filename = 'sounds/jarvis/here/33.wav'
            data, fs = sf.read(filename, dtype='float32')
            sd.play(data, fs)
            status = sd.wait()
            print(f"- {text}")
        else:
            if text:
                print('- неизвестная команда')
                filename = 'sounds/jarvis/else/2.wav'
                data, fs = sf.read(filename, dtype='float32')
                sd.play(data, fs)
                status = sd.wait()


tts = TTS()
stt = STT(modelpath="vosk-model-small-ru-0.22")
if datetime.time(5, 30) >= datetime.time(datetime.datetime.now().hour, datetime.datetime.now().minute) <= datetime.time(11, 0):
    filename = 'sounds/jarvis/Greetings/42.wav'
else:
    match randint(1, 2):
        case 1:
            filename = 'sounds/jarvis/Greetings/13.wav'
        case 2:
            filename = 'sounds/jarvis/Greetings/49.wav'
data, fs = sf.read(filename, dtype='float32')
sd.play(data, fs)
status = sd.wait()

print("listen...")
stt.listen(execute)
