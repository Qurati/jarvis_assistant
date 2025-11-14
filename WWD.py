import pvporcupine
import sounddevice as sd
import numpy as np
import os

# Wake Word Detection
class WWD:
    def __init__(self, access_key, ppn_file_path):
        if not os.path.exists(ppn_file_path):
            raise FileNotFoundError(f"PPN файл не найден: {ppn_file_path}")

        self.porcupine = pvporcupine.create(
            access_key=access_key,
            keyword_paths=[ppn_file_path]
        )

        self.sample_rate = self.porcupine.sample_rate
        self.frame_length = self.porcupine.frame_length
        self.is_listening = False
        self.callback_function = None

        self.keyword_name = os.path.splitext(os.path.basename(ppn_file_path))[0]

        print(f"Загружен PPN файл: {self.keyword_name}")
        print(f"Sample rate: {self.sample_rate}")
        print(f"Frame length: {self.frame_length}")

    def audio_callback(self, indata, frames, time, status):
        if status:
            print(f"Audio status: {status}")

        if self.is_listening and self.callback_function:
            try:
                # Конвертируем аудио
                pcm = np.int16(indata[:, 0] * 32767).flatten().tolist()

                # Проверяем длину данных
                if len(pcm) == self.frame_length:
                    keyword_index = self.porcupine.process(pcm)

                    # Если распознано ключевое слово
                    if keyword_index >= 0:
                        print(f"Wake word '{self.keyword_name}' распознан!")
                        self.callback_function()

            except Exception as e:
                print(f"audio_callback: {e}")

    def start_listening(self, callback_function):
        self.callback_function = callback_function
        self.is_listening = True

        try:
            print("Слушаю wake word...")

            with sd.InputStream(
                    samplerate=self.sample_rate,
                    channels=1,
                    dtype='float32',
                    blocksize=self.frame_length,
                    callback=self.audio_callback
            ):
                # Бесконечный цикл прослушивания
                while self.is_listening:
                    sd.sleep(1000)

        except KeyboardInterrupt:
            print("\n Остановлено пользователем")
        except Exception as e:
            print(f"audio stream: {e}")
        finally:
            self.cleanup()

    def cleanup(self):
        self.is_listening = False
        if hasattr(self, 'porcupine') and self.porcupine:
            try:
                self.porcupine.delete()
                print("Ресурсы WWD освобождены")
            except Exception as e:
                print(f"Ошибка при очистке Porcupine: {e}")