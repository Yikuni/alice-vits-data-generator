import glob
import math
import os

import whisper
import ffmpeg
from tqdm import tqdm


def generate(lang):
    # 获取目录下以.wav结尾的文件
    audioFiles = glob.glob('cache/clips/*.wav')

    # 加载whisper的模型
    model = whisper.load_model("base")
    split_index = math.ceil(len(audioFiles) * 4 / 5)
    with tqdm(total=len(audioFiles)) as pBar:
        pBar.set_description('音频识别中')
        def writeFile(path, start, end):
            if lang == 'ja':
                reg = '、'
                endReg = '。'
            elif lang == 'zh':
                reg = '，'
                endReg = '。'
            else:
                reg = ','
                endReg = '.'
            with open(path, "a+") as file:
                for audio in audioFiles[start:end]:
                    audio = audio.replace('\\', '/')
                    result = model.transcribe(audio)
                    file.write(audio)
                    file.write('|')
                    text = result["text"].replace(' ', reg)
                    file.write(text)
                    file.write(endReg)
                    pBar.update(1)
                    if audio != audioFiles[end - 1]:
                        file.write('\n')

        writeFile("cache/list.txt", 0, split_index)
        writeFile("cache/list.txt", split_index, len(audioFiles))
