#================================
# tts - Text to Speech
#================================

import torch
import time
import sounddevice as sd


class TTS:
    def __init__(self, speaker="aidar", device="cpu", samplerate=48000):
        self.speaker = speaker
        self.samplerate = samplerate
        self.device = torch.device(device)
        self.model = torch.package.PackageImporter("v4_ru.pt").load_pickle("tts_models", "model")
        self.model.to(self.device)

    def text2speech(self, text: str):
        audio = self.model.apply_tts(
            text=text,
            speaker=self.speaker,
            sample_rate=self.samplerate,
            put_accent=True,
            put_yo=True
        )

        sd.play(audio, samplerate=self.samplerate)
        time.sleep((len(audio) / self.samplerate))
        sd.stop()