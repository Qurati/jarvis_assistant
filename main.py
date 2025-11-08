from helper import helper_for_commands as HC 

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

#---------------------------------------
# класс ассистента. Параметры:
# speaker - кто будет озвучивать (xenia или aidar),
# jarvis_speak - нужно ли отвечать фразами джарвиса из фильма,
# name - имя ассистента
#---------------------------------------
class Jarvis:
    def __init__(self, speaker: str, jarvis_speak: bool, name: str):
        self.jarvis_speak = jarvis_speak
        self.tts = TTS(speaker=speaker)
        self.name = name

        #---------------------------------------
        # приветствие при запуске
        #---------------------------------------
        try:
            if jarvis_speak:
                if (datetime.time(5, 30) >=
                    datetime.time(datetime.datetime.now().hour, datetime.datetime.now().minute) <=
                    datetime.time(11, 0)):
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
            else:
                self.tts.text2speech('здравствуйте, сэр')

        except Exception as e:
            print(f'err: {e}')
            # Использую рекурсию чтоб при ошибке воспроизведения аудио Джарвиса класс 
            # инициализировался снова и пытался проиграть аудио
            self.__init__(speaker, jarvis_speak, name)

    def execute(self, text: str):
        try:
            print(f"> {text}")
            if self.name in text.split(' ') or text:
                if equ(text, "команда"):
                    print('команда')

                # дальнейшая логика
                elif equ(text, 'спасибо'):
                    if self.jarvis_speak:
                        match randint(1, 2):
                            case 1:
                                filename = 'sounds/jarvis/thanks/always_at_your_service.wav'
                            case 2:
                                filename = 'sounds/jarvis/thanks/at_your_service.wav'
                    else:
                        self.tts.text2speech('к вашим услугам, сэр')

                # при приветствии
                elif equ(text, 'привет'):
                    if self.jarvis_speak:
                        filename = 'sounds/jarvis/Greetings/how_are_you.wav'
                    else:
                        self.tts.text2speech('как вы?')
                elif equ(text, 'доброе утро'):
                    if self.jarvis_speak:
                        filename = 'sounds/jarvis/Greetings/good_morning.wav'
                    else:
                        self.tts.text2speech('Доброе Утро')


                # хз зачем, пока пусть будет (можно
                # будет использовать при команде создай
                # новый файл или папку или что-то другое)
                elif equ(text, 'создай новый элемент'):
                    if self.jarvis_speak:
                        match randint(1, 2):
                            case 1:
                                filename = 'sounds/jarvis/created/image_created.wav'
                            case 2:
                                filename = 'sounds/jarvis/created/you_have_created_a_new_element.wav'

                # показывает все команды
                elif equ(text, 'напиши все комманды') or equ(text, 'напиши все твои комманды'):
                    filename = 'sounds/jarvis/request/request_completed.wav'
                    HC.helper_commands.write_all_commands()

                # отвечает людям на неудовлетворительный ответ
                elif equ(text, 'неправильно') or equ(text, 'что за фигня') or equ(text, 'неверно') or equ(text, 'не смешно'):
                    if self.jarvis_speak:
                        filename = 'sounds/jarvis/else/What_was_I_thinking_about.wav'
                    else:
                        self.tts.text2speech('о чем я только думал')

                # если просто скажешь его имя
                elif text == self.name:
                    if self.jarvis_speak:
                        match randint(1, 2):
                            case 1:
                                filename = 'sounds/jarvis/here/yeah_sir.wav'
                            case 2:
                                filename = 'sounds/jarvis/here/yeah_sir_2.wav'
                    else:
                        self.tts.text2speech('да, сэр?')

                elif equ(text, "выключись") or equ(text, 'пока'):
                    if self.jarvis_speak:
                        match randint(1, 2):
                            case 1:
                                filename = 'sounds/jarvis/bye/turning_off_and_diagn_syst.wav'
                            case 2:
                                filename = 'sounds/jarvis/bye/turning_off.wav'
                        data, fs = sf.read(filename, dtype='float32')
                        sd.play(data, fs)
                        sd.wait()

                    else:
                        self.tts.text2speech('до встречи')

                    raise SystemExit

                elif equ(text, 'почему так мало команд') or equ(text, 'это все что ты умеешь?'):
                    if self.jarvis_speak:
                        filename = 'sounds/jarvis/else/terabytes_of_data_have_not_been_calculated_yet.wav'
                    else:
                        print('да')

                else:
                    if text:
                        print('- неизвестная команда')

                        if self.jarvis_speak:
                            match randint(1, 3):
                                case 1: 
                                    filename = 'sounds/jarvis/else/question.wav'
                                case 2:
                                    filename = 'sounds/jarvis/else/terabytes_of_data_have_not_been_calculated_yet.wav' 
                                case 3:
                                    filename = 'sounds/jarvis/else/no_info.wav'   
                        else:
                            self.tts.text2speech('чего вы пытаетесь добиться?')

                if self.jarvis_speak:
                    data, fs = sf.read(filename, dtype='float32')
                    sd.play(data, fs)
                    status = sd.wait()
        except Exception as e:
            print(f"ERROR: {e}")

stt = STT(modelpath="vosk-model-small-ru-0.22")
print("listen...")
assistant = Jarvis(speaker = 'aidar', jarvis_speak=True, name = 'джарвис')
stt.listen(assistant.execute)