#================================
# stt - Speech to text
#================================

import sounddevice as sd
import vosk
import sys
import queue
import json


class STT:
    def __init__(self, modelpath: str, samplerate: int = 16000):
        self.model = vosk.Model(modelpath)
        self.samplerate = samplerate
        self.is_listening = False

    # Прослушивание команды с таймаутом
    def listen_once(self, executor: callable, timeout: int = 5):
        rec = vosk.KaldiRecognizer(self.model, self.samplerate)
        q = queue.Queue()

        def callback(indata, frames, time, status):
            if status:
                print(status, file=sys.stderr)
            q.put(bytes(indata))

        self.is_listening = True
        print("Слушаю команду...")

        try:
            with sd.RawInputStream(
                    samplerate=self.samplerate,
                    blocksize=8000,
                    dtype='int16',
                    channels=1,
                    callback=callback
            ):
                # Слушаем в течение timeout секунд
                import time
                start_time = time.time()

                while self.is_listening and (time.time() - start_time) < timeout:
                    try:
                        data = q.get(timeout=1)
                        if rec.AcceptWaveform(data):
                            result = json.loads(rec.Result())
                            text = result["text"].strip()
                            if text:  # Если распознан непустой текст
                                executor(text)
                                return
                    except queue.Empty:
                        continue

                # Если время вышло и ничего не распознано
                print("Время ожидания команды истекло")

        except Exception as e:
            print(f"STT: {e}")
        finally:
            self.is_listening = False

    #Постоянное прослушивание
    def listen(self, executor: callable):
        rec = vosk.KaldiRecognizer(self.model, self.samplerate)
        q = queue.Queue()

        def callback(indata, frames, time, status):
            if status:
                print(status, file=sys.stderr)
            q.put(bytes(indata))

        self.is_listening = True

        with sd.RawInputStream(
                samplerate=self.samplerate,
                blocksize=8000,
                dtype='int16',
                channels=1,
                callback=callback
        ):
            while self.is_listening:
                data = q.get()
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    text = result["text"].strip()
                    if text:
                        executor(text)