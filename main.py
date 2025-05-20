import numpy as np
import os
import matplotlib.pyplot as plt
from rd3lib import readRd3, reshapeRd3, cutRd3, plot_gpr_image, apply_filter

path = "C:\\Users\\admin\\Desktop\\SBR_013\\00\\"
filename = "SBR_013.rd3"

def fileRead(path, filename):
    """
    .rd3 파일을 numpy로 읽어오는 함수
from rd3lib import readRd3, reshapeRd3, cutRd3, plot_gpr_image, apply_filter

    :param path : local의 파일 경로 , string 형태
    :param filename : 파일 경로에 있는 확장자가(.rd3)인 파일

    """
    with open(os.path.join(path, filename), "rb") as f:
        data = f.read()
    rd3 = np.frombuffer(data, dtype=np.short)
    return rd3


def readRad(path, filename):
    """
    파일 확장자를 rad로 바꾸고, 텍스트 헤더와 binary 신호 데이터를 모두 읽어오는 함수

    :param path: local에서의 파일 경로 (string)
    :param filename: 파일경로에 있는, '.rd3' 확장자를 가진 파일명

    :return: rad (np.array)
    :return: infoDict (dict)
    """
    nameRad = filename[:-3] + "rad"
    with open(os.path.join(path, nameRad), "rb") as f:
        data = f.read()

    decoded_rad = data.decode("utf-8", errors="ignore")

    lines = decoded_rad.splitlines()
    list_rad = [line.strip().replace("'", "\"") for line in lines]

    infoDict = {}
    header_byte_len = 0

    for line in list_rad:
        if ':' not in line:
            break
        colonIdx = line.find(':')
        key = line[:colonIdx].strip()
        value = line[colonIdx + 1:].strip()
        infoDict[key] = value

        header_byte_len += len((line + "\n").encode("utf-8"))

    rad = np.frombuffer(data[header_byte_len:], dtype=np.short)

    return rad, infoDict

def extractionRad(path, filename):
    """
    .rad 파일 내부의 CH_Y_OFFSETS과 DISTANCE INTERVAL의 값을 추출해 내는 함수

    :param path : local의 파일 경로 , string 형태
    :param filename : 파일 경로에 있는 확장자가(.rd3)인 파일

    :return chOffsets : rad 내부에 있는 CH_Y_OFFSETS 리스트 값
    :return distance_interval : rad 내부에 있는 distance interval int 값
    :return ch : rad 내부에 있는 NUMBER_OF_CH의 int 값
    """
    rad, infoDict = readRad(path, filename)

    chOffsets_str = infoDict.get("CH_Y_OFFSETS", "")
    distance_interval_str = infoDict.get("DISTANCE INTERVAL", "0")
    ch_str = infoDict.get("NUMBER_OF_CH", "0")

    chOffsets = [float(x) for x in chOffsets_str.split()]
    distance_interval = float(distance_interval_str)
    ch = int(ch_str)


    return chOffsets, distance_interval, ch


def alignChannel(path, filename):
    """
     - 0.044, 2.58 으로 거리가 차이나는 채널을 일정하게 맞춰주는 함수
    """
    chOffsets = extractionRad(path, filename)
    chOffsets = np.array(chOffsets)
    chOffsets -= np.min(chOffsets)

    for i, value in enumerate(chOffsets):
        if value == 0:
            continue


    # 2. 제일 첫 번째 거를 0으로 만들어야하니까? 평균을 빼야함?(최소값을 뺴야하나? )
    # 3.
