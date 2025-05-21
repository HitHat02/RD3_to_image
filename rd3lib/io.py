'''
rd3, rad 파일 읽기 등 I/O 관련 함수
'''
import numpy as np
import os

def readRd3(filepath):
    with open(filepath, "rb") as f:
        data = f.read()
    rd3_data = np.frombuffer(data, dtype=np.short)
    return rd3_data

def readRad(path, filename):
    """
    파일 확장자를 rad로 바꾸고, 텍스트 헤더와 binary 신호 데이터를 모두 읽어오는 함수

    :param path: local에서의 파일 경로 (string)
    :param filename: 파일경로에 있는, '.rd3' 확장자를 가진 파일명

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


    return infoDict

def extractionRad(path, filename):
    """
    .rad 파일 내부의 CH_Y_OFFSETS과 DISTANCE INTERVAL의 값을 추출해 내는 함수

    :param path : local의 파일 경로 , string 형태
    :param filename : 파일 경로에 있는 확장자가(.rd3)인 파일

    :return chOffsets : rad 내부에 있는 CH_Y_OFFSETS 리스트 값
    :return distance_interval : rad 내부에 있는 distance interval int 값
    :return ch : rad 내부에 있는 NUMBER_OF_CH의 int 값
    """
    infoDict = readRad(path, filename)

    chOffsets_str = infoDict.get("CH_Y_OFFSETS", "")
    distance_interval_str = infoDict.get("DISTANCE INTERVAL", "0")
    ch_str = infoDict.get("NUMBER_OF_CH", "0")

    chOffsets = [float(x) for x in chOffsets_str.split()]
    distance_interval = float(distance_interval_str)
    ch = int(ch_str)


    return chOffsets, distance_interval, ch