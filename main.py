from fuzzywuzzy import fuzz
from tts import TTS
from stt import STT


def equ(text, needed):
    return fuzz.ratio(text, needed) >= 70


def execute(text: str):
    print(f"> {text}")
    if equ(text, "команда"):
        tts.text2speech("ответ-озвучка")
        print(f"- {text}")
        #дальнейшая логика

    elif equ(text, "выключись"):
        tts.text2speech("слушаюсь, сер!")
        print(f"- {text}")
        raise SystemExit


tts = TTS()
stt = STT(modelpath="vosk-model-small-ru-0.22")

print("listen...")
stt.listen(execute)