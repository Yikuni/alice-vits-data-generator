import os


# 从url获取视频, 返回保存位置
def download(url):
    # url = 'https://www.bilibili.com/video/BV1Cz4y1n78b'
    savePath = 'cache/video/'
    split = url.split('/')
    name = split[len(split) - 1]
    command = 'you-get -O ' + name + ' -o ' + savePath + ' ' + url
    os.system(command)
    return 'cache/video/' + name
