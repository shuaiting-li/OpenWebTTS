import wave
from piper import PiperVoice
from functions.audio import normalize_audio
from config import DEVICE


def piper_process_audio(voice, lang, text, output):
    piper_voice = PiperVoice.load(voice, use_cuda=(DEVICE == 'cuda'))
    with wave.open(output, "wb") as wav_file:
        piper_voice.synthesize_wav(text, wav_file)

    normalize_audio(output)
