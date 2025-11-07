from fuzzywuzzy import fuzz
from tts import TTS
from stt import STT
import sounddevice as sd
import soundfile as sf
from random import randint
import datetime

#---------------------------------------
# проверка на совпадение текста >= 45%
#---------------------------------------
def equ(text, needed):
    return fuzz.ratio(text, needed) >= 45


def execute(text: str):
    try:
        print(f"> {text}")
        if 'джарвис' in text.split(' '):

            if equ(text, "команда"):
                tts.text2speech("ответ-озвучка")
                print(f"- {text}")

            # дальнейшая логика
            elif equ(text, 'спасибо'):
                match randint(1, 2):
                    case 1:
                        filename = 'sounds/jarvis/thanks/always_at_your_service.wav'
                    case 2:
                        filename = 'sounds/jarvis/thanks/at_your_service.wav'

                data, fs = sf.read(filename, dtype='float32')
                sd.play(data, fs)
                status = sd.wait()
                print(f"- {text}")

            elif equ(text, "выключись"):
                match randint(1, 2):
                    case 1:
                        filename = 'sounds/jarvis/bye/turning_off_and_diagn_syst.wav'
                    case 2:
                        filename = 'sounds/jarvis/bye/turning_off.wav'

                data, fs = sf.read(filename, dtype='float32')
                sd.play(data, fs)
                status = sd.wait()
                print(f"- {text}")
                raise SystemExit
            
            elif text == 'джарвис':
                match randint(1, 2):
                    case 1:
                        filename = 'sounds/jarvis/here/yeah_sir.wav'
                    case 2:
                        filename = 'sounds/jarvis/here/yeah_sir_2.wav'
        
                data, fs = sf.read(filename, dtype='float32')
                sd.play(data, fs)
                status = sd.wait()
                print(f"- {text}")

            else:
                if text:
                    print('- неизвестная команда')
                    filename = 'sounds/jarvis/else/question.wav'
                    data, fs = sf.read(filename, dtype='float32')
                    sd.play(data, fs)
                    status = sd.wait()
    except Exception:
        print(f"ERROR: {Exception}")


tts = TTS()
stt = STT(modelpath="vosk-model-small-ru-0.22")
if datetime.time(5, 30) >= datetime.time(datetime.datetime.now().hour, datetime.datetime.now().minute) <= datetime.time(11, 0):
    filename = 'sounds/jarvis/Greetings/good_morning.wav'
else:
    match randint(1, 3):
        case 1:
            filename = 'sounds/jarvis/Greetings/start_diagn_syst.wav'
        case 2:
            filename = 'sounds/jarvis/Greetings/49.wav'
        case 3:
            filename = 'sounds/jarvis/Greetings/greeting_with_music'

data, fs = sf.read(filename, dtype='float32')
sd.play(data, fs)
status = sd.wait()

print("listen...")
stt.listen(execute)
