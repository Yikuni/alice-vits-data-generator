import os
import shutil
import time

from slicer2 import Slicer
from moviepy.editor import AudioFileClip
import librosa
import soundfile

# 第一次运行会下载spleeter预测模型, 需要使用能连github的网络
# os.environ["http_proxy"] = "http://yikuni.com:52514"
# os.environ["https_proxy"] = "http://yikuni.com:52514"


def fromVideo(path: str):
    my_audio_clip = AudioFileClip(path)
    path = path.replace('\\', '/')
    voicePath = 'cache/voice' + path[path.rfind('/'):path.rfind('.')] + ".wav"
    print(voicePath)
    my_audio_clip.write_audiofile(voicePath, progress_bar=False)
    return voicePath


def smoothVoice(path):
    path = path.replace('\\', '/')
    command = "spleeter separate -p spleeter:2stems -o cache/voice " + path
    os.system(command)


def resample(path):
    path = path.replace('\\', '/')
    outputPath = "cache/resampled" + path[path.rfind('/'):]
    command = "ffmpeg -i " + path + " -ac 1 -ar 22050 -sample_fmt s16 -y " + outputPath
    os.system(command)
    return outputPath


def sliceAudio(path):
    path = path.replace('\\', '/')
    prefix = path[path.rfind('/') + 1: path.rfind('.')]
    audio, sr = librosa.load(path, sr=None, mono=False)  # Load an audio file with librosa.
    slicer = Slicer(
        sr=sr,
        threshold=-40,
        min_length=5000,
        min_interval=300,
        hop_size=10,
        max_sil_kept=500
    )
    chunks = slicer.slice(audio)
    for i, chunk in enumerate(chunks):
        if len(chunk.shape) > 1:
            chunk = chunk.T  # Swap axes if the audio is stereo.
        soundfile.write(f'cache/clips/{prefix}_{i}.wav', chunk, sr)  # Save sliced audio files with soundfile.