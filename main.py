import webbrowser

from fuzzywuzzy import fuzz
from tts import TTS
from stt import STT
from WWD import WWD
import sounddevice as sd
import soundfile as sf
from random import randint
import datetime
import os
import time
import yandex
from config import *


# ---------------------------------------
# проверка на совпадение текста >= 60%
# ---------------------------------------
def equ(text, needed):
    return fuzz.ratio(text, needed) >= 60


# ---------------------------------------
# класс ассистента. Параметры:
# speaker - кто будет озвучивать (xenia или aidar),
# jarvis_speak - нужно ли отвечать фразами джарвиса из фильма,
# name - имя ассистента
# ---------------------------------------
class Jarvis:
    def __init__(self, speaker: str, jarvis_speak: bool, name: str, picovoice_keyword_path: str, picovoice_token: str):
        self.jarvis_speak = jarvis_speak
        self.tts = TTS(speaker=speaker)
        self.name = name
        self.picovoice_token = picovoice_token
        self.picovoice_keyword_path = picovoice_keyword_path
        self.is_active = False
        self.wwd = None
        self.is_speaking = False  # Флаг для отслеживания состояния синтеза
        self.synthesis_queue = []  # Очередь для синтеза
        self.current_sentence_index = 0
        self.stt = STT(modelpath="vosk-model-small-ru-0.22")  # Инициализируем STT заранее

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
                if datetime.time(4, 00) <= current_time <= datetime.time(11, 0):
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
                    self.speak_sync('здравствуйте, сэр')
            else:
                self.speak_sync('здравствуйте, сэр')
        except Exception as e:
            print(f'Ошибка приветствия: {e}')
            self.speak_sync('Система запущена')

    def speak_sync(self, text: str):
        return self.tts.text2speech(text)

    def speak_async(self, text: str, callback: callable = None):
        if self.is_speaking:
            print("Ассистент уже говорит, добавляю в очередь...")

        self.is_speaking = True

        def synthesis_callback(audio, synthesis_time):
            print(f"Синтез завершен за {synthesis_time:.2f} сек, начинаю воспроизведение...")

            sd.play(audio, samplerate=self.tts.samplerate)
            sd.wait()

            self.is_speaking = False
            print("Воспроизведение завершено")
            if callback:
                callback()

        self.tts.text2speech_async(text, synthesis_callback)

    def speak_and_listen(self, text: str):

        def start_listening_after_speech():
            print("Запускаю прослушивание команды...")
            self.stt.listen_once(self.commands, timeout=5)

        self.speak_async(text, start_listening_after_speech)

    def speak_multiple_async(self, texts: list, callback: callable = None):
        if not texts:
            if callback:
                callback()
            return

        self.synthesis_queue = texts.copy()
        self.current_sentence_index = 0
        self.is_speaking = True
        self.final_callback = callback

        print(f"Начинаю синтез {len(texts)} фраз...")
        self._process_next_sentence()

    def _process_next_sentence(self):
        if self.current_sentence_index >= len(self.synthesis_queue):
            print("Все фразы синтезированы")
            self.is_speaking = False
            if self.final_callback:
                self.final_callback()
            return

        current_text = self.synthesis_queue[self.current_sentence_index]
        current_index = self.current_sentence_index + 1
        total_count = len(self.synthesis_queue)

        print(f"Синтез фразы {current_index}/{total_count}: {current_text}")

        def callback(audio, synthesis_time):
            print(f"Фраза {current_index} готова за {synthesis_time:.2f} сек")
            sd.play(audio, samplerate=self.tts.samplerate)
            sd.wait()

            self.current_sentence_index += 1
            self._process_next_sentence()

        self.tts.text2speech_async(current_text, callback)

    # Разбиение на предложения
    def _split_into_sentences(self, text: str, max_length: int = 150):
        import re

        sentences = re.split(r'(?<=[.!?])\s+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        result = []
        for sentence in sentences:
            if len(sentence) <= max_length:
                result.append(sentence)
            else:
                parts = re.split(r'(?<=[,;:])\s+', sentence)
                for part in parts:
                    part = part.strip()
                    if part:
                        if len(part) > max_length:
                            words = part.split()
                            current_chunk = ""
                            for word in words:
                                if len(current_chunk) + len(word) + 1 <= max_length:
                                    current_chunk += " " + word if current_chunk else word
                                else:
                                    if current_chunk:
                                        result.append(current_chunk + ".")
                                    current_chunk = word
                            if current_chunk:
                                result.append(current_chunk + ".")
                        else:
                            result.append(part)

        return [s for s in result if s]

    def process_ai_response(self, ai_text: str):
        print(f"\n ИИ ({len(ai_text)} символов):")
        print(f"{ai_text[:100]}...")

        # Разбиваем длинный текст на предложения для более плавного синтеза
        sentences = self._split_into_sentences(ai_text)

        print(f"Разбито на {len(sentences)} предложений")
        if sentences:
            def after_ai_response():
                print("Ответ ИИ завершен, готов к новым командам")

            self.speak_multiple_async(sentences, after_ai_response)
        else:
            print("Не удалось разбить текст на предложения")
            self.speak_async(ai_text)

    def commands(self, text: str):
        text = text.lower()
        try:
            print(f"> Распознано: {text}")

            if equ(text, "команда"):
                self.speak_sync("ответ-озвучка")

            elif equ(text, 'привет'):
                if self.jarvis_speak:
                    filename = 'sounds/jarvis/Greetings/how_are_you.wav'
                    if os.path.exists(filename):
                        data, fs = sf.read(filename, dtype='float32')
                        sd.play(data, fs)
                        sd.wait()
                    else:
                        self.speak_sync('как вы?')
                else:
                    self.speak_sync('как вы?')

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
                        self.speak_sync('к вашим услугам, сер')
                else:
                    self.speak_sync('к вашим услугам, сер')

            elif equ(text, "тест асинхрон"):
                # Тест асинхронного синтеза
                test_phrases = [
                    "Первая тестовая фраза для асинхронного синтеза.",
                    "Вторая фраза обрабатывается параллельно.",
                    "Третья фраза завершает тестирование.",
                ]
                self.speak_multiple_async(test_phrases)

            elif equ(text, "статистика"):
                # Показать статистику TTS
                stats = self.tts.get_performance_stats()
                print(f"\n СТАТИСТИКА ПРОИЗВОДИТЕЛЬНОСТИ TTS:")
                print(f"   Всего синтезов: {stats['total_syntheses']}")
                if stats['total_syntheses'] > 0:
                    print(f"   Среднее время: {stats['avg_synthesis_time']:.2f} сек")
                    print(f"   Минимальное время: {stats['min_synthesis_time']:.2f} сек")
                    print(f"   Максимальное время: {stats['max_synthesis_time']:.2f} сек")
                    print(f"   Общее время синтеза: {stats['total_synthesis_time']:.2f} сек")
                print(f"   Устройство: {stats['device']}")

            elif equ(text, "длинный текст"):
                # Пример длинного текста для тестирования
                long_text = """Это пример длинного текста который будет синтезирован асинхронно. Ассистент разобьет его на несколько предложений и обработает последовательно. Это позволяет не блокировать основной поток во время синтеза длинных ответов."""
                self.process_ai_response(long_text)

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
                        self.speak_sync('до встречи')
                else:
                    self.speak_sync('до встречи')

                # Ожидаем завершения всех синтезов перед выключением
                if self.is_speaking:
                    print("Ожидаю завершения синтеза...")
                    self.tts.wait_queue_empty()

                self.cleanup()
                raise SystemExit


            else:
                print('- неизвестная команда')
                ans = yandex.get_yandex_answer(text)
                print(ans.split(' '))
                if ans.split(' ')[0]=='сайт':
                    print(ans.split(' ')[1])
                    webbrowser.open_new_tab(ans.split(' ')[1])
                else:
                    self.process_ai_response(ans)
                # if self.jarvis_speak:
                #     match randint(1, 3):
                #         case 1:
                #             filename = 'sounds/jarvis/else/question.wav'
                 #         case 2:
                #             filename = 'sounds/jarvis/else/terabytes_of_data_have_not_been_calculated_yet.wav'
                #         case 3:
                #             filename = 'sounds/jarvis/else/no_info.wav'
                #     if os.path.exists(filename):
                #         data, fs = sf.read(filename, dtype='float32')
                #         sd.play(data, fs)
                #         sd.wait()
                #     else:
                #         self.speak_async('чего вы пытаетесь добиться?')
                # else:
                #     self.speak_async('чего вы пытаетесь добиться?')

        except Exception as e:
            print(f"commands: {e}")


    def start_listening_for_wake_word(self):
        if self.wwd:
            self.wwd.start_listening(self.on_wake_word_detected)


    def on_wake_word_detected(self):
        print("WWD распознан")

        def start_listening():
            print("Готов к приему команды...")
            self.stt.listen_once(self.commands, timeout=10)

        import threading
        listen_thread = threading.Thread(target=start_listening, daemon=True)
        listen_thread.start()

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
                self.speak_async('да, сэр?')
        else:
            self.speak_async('да, сэр?')


    def cleanup(self):
        print("Остановка ассистента...")
        if self.is_speaking:
            print("Ожидаю завершения текущего синтеза...")
            self.tts.wait_queue_empty()

        if self.wwd:
            self.wwd.cleanup()

        self.tts.cleanup()
        print("Все ресурсы освобождены")


# Запуск ассистента
if __name__ == "__main__":
    try:
        assistant = Jarvis(
            speaker='aidar',
            jarvis_speak=True,
            name='джарвис',
            picovoice_keyword_path="./jarvis_en_windows_v3_0_0.ppn",
            picovoice_token=picovoice_token
        )
        print("Ассистент запущен")
        assistant.start_listening_for_wake_word()
    except SystemExit:
        print("Ассистент завершает работу...")
    except Exception as e:
        print(f"Начальная ошибка: {e}")
