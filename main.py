from fuzzywuzzy import fuzz
from tts import TTS
from stt import STT
from WWD import WWD
import sounddevice as sd
import soundfile as sf
from random import randint
import datetime
import os


#---------------------------------------
# проверка на совпадение текста >= 45%
#---------------------------------------
def equ(text, needed):
    return fuzz.ratio(text, needed) >= 45


#---------------------------------------
# класс ассистента. Параметры:
# speaker - кто будет озвучивать (xenia или aidar),
# jarvis_speak - нужно ли отвечать фразами джарвиса из фильма,
# name - имя ассистента
#---------------------------------------
class Jarvis:
    def __init__(self, speaker: str, jarvis_speak: bool, name: str, picovoice_keyword_path: str, picovoice_token: str):
        self.jarvis_speak = jarvis_speak
        self.tts = TTS(speaker=speaker)
        self.name = name
        self.picovoice_token = picovoice_token
        self.picovoice_keyword_path = picovoice_keyword_path
        self.is_active = False
        self.wwd = None

        # Инициализация WWD
        self.initialize_wwd()

        # Приветствие
        self.greet()

    def initialize_wwd(self):
        try:
            self.wwd = WWD(self.picovoice_token, self.picovoice_keyword_path)
            print("WWD инициализирован")
        except Exception as e:
            print(f"Ошибка WWD: {e}")
            raise

    def greet(self):
        try:
            if self.jarvis_speak:
                current_time = datetime.datetime.now().time()
                if datetime.time(5, 30) <= current_time <= datetime.time(11, 0):
                    filename = 'sounds/jarvis/Greetings/good_morning.wav'
                else:
                    match randint(1, 3):
                        case 1:
                            filename = 'sounds/jarvis/Greetings/start_diagn_syst.wav'
                        case 2:
                            filename = 'sounds/jarvis/Greetings/49.wav'
                        case 3:
                            filename = 'sounds/jarvis/Greetings/greeting_with_music.wav'

                if os.path.exists(filename):
                    data, fs = sf.read(filename, dtype='float32')
                    sd.play(data, fs)
                    sd.wait()
                else:
                    self.tts.text2speech('здравствуйте, сэр')
            else:
                self.tts.text2speech('здравствуйте, сэр')
        except Exception as e:
            print(f'Ошибка приветствия: {e}')
            self.tts.text2speech('Система запущена')

    def commands(self, text: str):
        text = text.lower()
        try:
            print(f"> Распознано: {text}")

            if equ(text, "команда"):
                self.tts.text2speech("ответ-озвучка")

            elif equ(text, 'привет'):
                if self.jarvis_speak:
                    filename = 'sounds/jarvis/Greetings/how_are_you.wav'
                    if os.path.exists(filename):
                        data, fs = sf.read(filename, dtype='float32')
                        sd.play(data, fs)
                        sd.wait()
                else:
                    self.tts.text2speech('как вы?')

            elif equ(text, 'спасибо'):
                if self.jarvis_speak:
                    match randint(1, 2):
                        case 1:
                            filename = 'sounds/jarvis/thanks/always_at_your_service.wav'
                        case 2:
                            filename = 'sounds/jarvis/thanks/at_your_service.wav'
                    if os.path.exists(filename):
                        data, fs = sf.read(filename, dtype='float32')
                        sd.play(data, fs)
                        sd.wait()
                    else:
                        self.tts.text2speech('к вашим услугам, сер')
                else:
                    self.tts.text2speech('к вашим услугам, сер')

            elif equ(text, "выключись"):
                if self.jarvis_speak:
                    match randint(1, 2):
                        case 1:
                            filename = 'sounds/jarvis/bye/turning_off_and_diagn_syst.wav'
                        case 2:
                            filename = 'sounds/jarvis/bye/turning_off.wav'
                    if os.path.exists(filename):
                        data, fs = sf.read(filename, dtype='float32')
                        sd.play(data, fs)
                        sd.wait()
                else:
                    self.tts.text2speech('до встречи')
                self.cleanup()
                raise SystemExit

            else:
                if text.strip():
                    print('- неизвестная команда')
                    if self.jarvis_speak:
                        match randint(1, 3):
                            case 1:
                                filename = 'sounds/jarvis/else/question.wav'
                            case 2:
                                filename = 'sounds/jarvis/else/terabytes_of_data_have_not_been_calculated_yet.wav'
                            case 3:
                                filename = 'sounds/jarvis/else/no_info.wav'
                        if os.path.exists(filename):
                            data, fs = sf.read(filename, dtype='float32')
                            sd.play(data, fs)
                            sd.wait()
                        else:
                            self.tts.text2speech('чего вы пытаетесь добиться?')
                    else:
                        self.tts.text2speech('чего вы пытаетесь добиться?')

        except Exception as e:
            print(f"commands: {e}")

    def start_listening_for_wake_word(self):
        if self.wwd:
            self.wwd.start_listening(self.on_wake_word_detected)

    def on_wake_word_detected(self):
        print("WWD распознан")
        if self.jarvis_speak:
            match randint(1, 2):
                case 1:
                    filename = 'sounds/jarvis/here/yeah_sir.wav'
                case 2:
                    filename = 'sounds/jarvis/here/yeah_sir_2.wav'
            if os.path.exists(filename):
                data, fs = sf.read(filename, dtype='float32')
                sd.play(data, fs)
                sd.wait()
            else:
                self.tts.text2speech('да, сэр?')
        else:
            self.tts.text2speech('да, сэр?')

        # Запускаем прослушивание команды
        stt = STT(modelpath="vosk-model-small-ru-0.22")
        stt.listen_once(self.commands)

    def cleanup(self):
        if self.wwd:
            self.wwd.cleanup()


# Запуск ассистента
if __name__ == "__main__":
    try:
        assistant = Jarvis(
            speaker='aidar',
            jarvis_speak=True,
            name='джарвис',
            picovoice_keyword_path="./jarvis_en_windows_v3_0_0.ppn",
            picovoice_token='YOUR_TOKEN'
        )

        print("Ассистент запущен")
        assistant.start_listening_for_wake_word()

    except Exception as e:
        print(f"Начальная ошибка: {e}")