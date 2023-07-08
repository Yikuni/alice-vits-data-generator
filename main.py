import fnmatch
import glob
import os.path
import shutil
import time

from tqdm import tqdm

import video
import voice
import vtdgenerator


def initDirs():
    if not os.path.exists("cache"):
        os.mkdir("cache")
        if not os.path.exists("cache/clips"):
            os.mkdir("cache/clips")
        if not os.path.exists("cache/voice"):
            os.mkdir("cache/voice")
        if not os.path.exists("cache/video"):
            os.mkdir("cache/video")
        if not os.path.exists("cache/resampled"):
            os.mkdir("cache/resampled")


def copy_wav_files(source_dir, target_dir):
    # 检查目标目录是否存在，不存在则创建
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    # 遍历源目录下的所有文件和子目录
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            # 获取文件的完整路径
            source_file = os.path.join(root, file)
            # 检查文件是否以.wav结尾
            if file.endswith('.wav'):
                # 构造目标文件的完整路径
                target_file = os.path.join(target_dir, file)
                # 复制文件
                shutil.copy2(source_file, target_file)
                print('复制文件:', source_file, '到', target_file)


def get_video_files(directory):
    video_files = []
    for root, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            if fnmatch.fnmatch(filename, '*.mp4') or fnmatch.fnmatch(filename, '*.flv') or \
                    fnmatch.fnmatch(filename, '*.avi') or fnmatch.fnmatch(filename, '*.mkv'):
                video_files.append(os.path.join(root, filename))
    return video_files


def main():
    choice = input("开始获取音频导航, 请选择从url下载视频[1] or 读取本地音频[2] or 退出[exit]: ")
    choice = choice.strip()
    while '1' != choice and '2' != choice and 'exit' != choice:
        print("无效输入, 请重新输入")
        choice = input("开始获取音频导航, 请选择从url下载视频[1] or 读取本地音频[2] or 读取本地视频[3] or 退出[exit]").strip()
    if choice == 'exit':
        exit(0)
    elif choice == '1':
        urls = []
        while True:
            url = input("请输入URL: ").strip()
            if url.lower() == "end":
                break
            else:
                urls.append(url)

        print("正在下载视频")
        for url in urls:
            video.download(url)

        video_files = get_video_files("cache/video")
        with tqdm(total=len(video_files)) as pBar:
            pBar.set_description('从视频提取音频')
            for v in video_files:
                voice.fromVideo(v)
                pBar.update(1)

    elif choice == '2':
        sourceDir = input("请输入音频文件位置: ").strip()
        if not (os.path.exists(sourceDir) and os.path.isdir(sourceDir)):
            print("目标位置不是文件夹或不存在")
            exit(0)
        target_dir = 'cache/voice'  # 替换为实际的目标目录路径
        copy_wav_files(sourceDir, target_dir)
    elif choice == '3':
        print("正在开发")
        exit(0)

    # 进行背景音剔除
    wav_files = glob.glob('cache/voice/*.wav')
    with tqdm(total=len(wav_files)) as pBar:
        pBar.set_description('剔除背景音中')
        for file in wav_files:
            voice.smoothVoice(file)
            pBar.update(1)

    # resample
    wav_files = glob.glob('cache/voice/*.wav')
    with tqdm(total=len(wav_files)) as pBar:
        pBar.set_description('音频重采样中')
        for file in wav_files:
            voice.resample(file)
            pBar.update(1)

    # slice
    wav_files = glob.glob('cache/resampled/*.wav')
    with tqdm(total=len(wav_files)) as pBar:
        pBar.set_description('音频分割中')
        for file in wav_files:
            voice.sliceAudio(file)
            pBar.update(1)

    lang = input("请输入模型语言 ja/zh/en").strip()
    vtdgenerator.generate(lang)


if __name__ == '__main__':
    main()
