# ================================
# tts - Text to Speech
# ================================


import torch
import time
import sounddevice as sd
import threading
from queue import Queue
import numpy as np


class TTS:
    def __init__(self, speaker="aidar", device="cpu", samplerate=24000):
        self.speaker = speaker
        self.samplerate = samplerate
        self.device = torch.device(device)

        print('Загрузка TTS')
        start_time = time.time()
        self.model = torch.package.PackageImporter("v4_ru.pt").load_pickle("tts_models", "model")
        self.model.to(self.device)


        print(f"Модель загружена за {time.time() - start_time:.2f} секунд на устройство: {self.device}")

        self.synthesis_queue = Queue()
        self.is_processing = True
        self.processing_thread = threading.Thread(target=self._process_queue, daemon=True)
        self.processing_thread.start()

        # Статистика
        self.synthesis_times = []

    def _process_queue(self):
        while self.is_processing:
            try:
                item = self.synthesis_queue.get(timeout=1)
                if item is None:  # Сигнал остановки
                    break

                text, callback = item
                start_time = time.time()

                with torch.no_grad():
                    audio = self.model.apply_tts(
                        text=text,
                        speaker=self.speaker,
                        sample_rate=self.samplerate,
                        put_accent=True,
                        put_yo=True
                    )

                synthesis_time = time.time() - start_time
                self.synthesis_times.append(synthesis_time)

                self._print_synthesis_stats(text, synthesis_time, len(audio))

                if callback:
                    callback(audio, synthesis_time)

                self.synthesis_queue.task_done()

            except Exception as e:
                continue

    def text2speech_async(self, text: str, callback: callable = None):

        self.synthesis_queue.put((text, callback))
        print(f"Текст добавлен в очередь синтеза: '{text[:50]}{'...' if len(text) > 50 else ''}'")

    def text2speech(self, text: str):
        start_time = time.time()

        with torch.no_grad():
            audio = self.model.apply_tts(
                text=text,
                speaker=self.speaker,
                sample_rate=self.samplerate,
                put_accent=True,
                put_yo=True
            )

        synthesis_time = time.time() - start_time
        self.synthesis_times.append(synthesis_time)

        self._print_synthesis_stats(text, synthesis_time, len(audio))

        sd.play(audio, samplerate=self.samplerate)
        sd.wait()

        return synthesis_time

    def _print_synthesis_stats(self, text: str, synthesis_time: float, audio_length: int):
        audio_duration = audio_length / self.samplerate
        chars_per_second = len(text) / synthesis_time if synthesis_time > 0 else 0

        print(f"\nСТАТИСТИКА СИНТЕЗА:")
        print(f"   Текст: '{text[:60]}{'...' if len(text) > 60 else ''}'")
        print(f"   Длина текста: {len(text)} символов")
        print(f"   Время синтеза: {synthesis_time:.2f} сек")
        print(f"   Длительность аудио: {audio_duration:.2f} сек")
        print(f"   Скорость: {chars_per_second:.1f} сим/сек")

        # Средняя статистика
        if self.synthesis_times:
            avg_time = np.mean(self.synthesis_times)
            print(f"   Среднее время: {avg_time:.2f} сек")
        print("─" * 50)

    def wait_queue_empty(self):
        self.synthesis_queue.join()
        print("Все задачи синтеза завершены")

    def get_performance_stats(self):
        if not self.synthesis_times:
            return {
                "total_syntheses": 0,
                "avg_synthesis_time": 0,
                "total_synthesis_time": 0,
                "device": str(self.device)
            }

        return {
            "total_syntheses": len(self.synthesis_times),
            "avg_synthesis_time": np.mean(self.synthesis_times),
            "min_synthesis_time": np.min(self.synthesis_times),
            "max_synthesis_time": np.max(self.synthesis_times),
            "total_synthesis_time": sum(self.synthesis_times),
            "device": str(self.device)
        }

    def cleanup(self):
        self.is_processing = False
        self.synthesis_queue.put(None)
        if hasattr(self, 'processing_thread'):
            self.processing_thread.join(timeout=5)
        print("TTS модуль остановлен")