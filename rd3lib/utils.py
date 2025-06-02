import numpy as np
from PIL import Image
from rd3lib import alignSignal, alignGround, alignChannel
from rd3lib import readRd3, extractionRad
from rd3lib import reshapeRd3, apply_filter

def upscale_image(data_uint8, scale=4):
    """
    정규화된 uint8 이미지 배열을 지정된 배율로 확대하여,
    부드러운 경계 처리를 위한 LANCZOS 보간법으로 PIL 이미지로 반환합니다.

    :param data_uint8: 확대할 원본 2차원 uint8 배열 (정규화된 이미지)
    :type data_uint8: numpy.ndarray
    :param scale: 확대 배율 (기본값: 4배)
    :type scale: int
    :return: 확대된 PIL 이미지 객체
    :rtype: PIL.Image.Image
    """
    img = Image.fromarray(data_uint8)
    new_size = (img.width * scale, img.height * scale)
    return img.resize(new_size, resample=Image.LANCZOS)

def normalize_minmax(data, vmin=-3000, vmax=3000):
    """
    입력된 2차원 배열 데이터를 지정한 최소/최대값 기준으로 클리핑한 뒤,
    0부터 255 사이의 범위로 정규화하여 uint8 타입의 이미지 데이터로 반환합니다.

    :param data: 정규화할 2차원 NumPy 배열 (예: RD3 슬라이스)
    :type data: numpy.ndarray
    :param vmin: 정규화할 하한값 (기본값: -3000)
    :type vmin: int
    :param vmax: 정규화할 상한값 (기본값: 3000)
    :type vmax: int
    :return: 0~255 범위로 정규화된 uint8 형식의 2차원 배열
    :rtype: numpy.ndarray
    """
    data_clipped = np.clip(data, vmin, vmax)
    norm = ((data_clipped - vmin) / (vmax - vmin)) * 255
    return norm.astype(np.uint8)

def chunk_range(datalength, distance_interval):
    chunk_list = []

    chunk_size = round(200 / distance_interval)
    start = 0
    while start <= datalength:
        end = start + chunk_size
        if end > datalength:
            end = datalength
        chunk_list.append([start, end])
        start = end + 1

    return chunk_list

def rd3_process(DIRNAME, BASENAME):
    chOffsets, distance_interval, ch = extractionRad(DIRNAME, BASENAME)
    rd3 = readRd3(DIRNAME, BASENAME)
    rd3 = reshapeRd3(rd3)
    rd3 = alignSignal(rd3, ch)
    rd3 = alignGround(rd3, ch)
    rd3 = alignChannel(rd3, chOffsets, distance_interval)
    rd3 = apply_filter(rd3)

    return rd3