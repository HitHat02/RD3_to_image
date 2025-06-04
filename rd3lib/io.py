'''
rd3, rad 파일 읽기 등 I/O 관련 함수
'''
import numpy as np
import os
import matplotlib.pyplot as plt
from rd3lib.utils import normalize_minmax, upscale_image


def readRd3(path, filename):
    """
    지정된 경로에서 .rd3 바이너리 파일을 열어, 신호 데이터를 NumPy 배열로 변환하여 반환합니다.

    :param path: 파일이 저장된 폴더 경로
    :type path: str
    :param filename: 읽을 .rd3 파일명
    :type filename: str
    :return: 1차원 NumPy 배열 형태의 신호 데이터
    :rtype: numpy.ndarray
    """
    with open(os.path.join(path, filename), "rb") as f:
        data = f.read()
    rd3_data = np.frombuffer(data, dtype=np.short)
    return rd3_data


def readRad(path, filename):
    """
    주어진 경로의 .rad 파일을 읽고, 텍스트 헤더 정보를 딕셔너리로 파싱한 후,
    이어지는 바이너리 데이터를 NumPy 배열로 반환합니다.

    :param path: 파일이 저장된 폴더 경로
    :type path: str
    :param filename: 확장자가 .rd3인 파일 이름 (rad 확장자로 자동 변환됨)
    :type filename: str
    :return: 헤더 정보를 담은 딕셔너리
    :rtype: dict
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
    지정된 .rad 파일에서 CH_Y_OFFSETS, DISTANCE INTERVAL, NUMBER_OF_CH 값을 추출하여 반환합니다.

    :param path: 파일이 저장된 폴더 경로
    :type path: str
    :param filename: .rd3 확장자를 가진 파일명 (rad 확장자로 자동 변환됨)
    :type filename: str
    :return: 채널 오프셋 리스트 (CH_Y_OFFSETS)
    :rtype: list[float]
    :return: 거리 간격 값 (DISTANCE INTERVAL)
    :rtype: float
    :return: 채널 개수 (NUMBER_OF_CH)
    :rtype: int
    """
    filename = str(filename)
    radname = filename[:-4] + ".rad"
    infoDict = readRad(path, radname)

    chOffsets_str = infoDict.get("CH_Y_OFFSETS", "")
    distance_interval_str = infoDict.get("DISTANCE INTERVAL", "0")
    ch_str = infoDict.get("NUMBER_OF_CH", "0")

    chOffsets = [float(x) for x in chOffsets_str.split()]
    distance_interval = float(distance_interval_str)
    ch = int(ch_str)

    return chOffsets, distance_interval, ch


def image_save(npdata, filename, number, depth=30):
    """
    RD3 3차원 데이터를 슬라이스하여 정규화 및 업스케일 후,
    각 축에 대한 특정 인덱스 슬라이스 이미지를 저장합니다.

    슬라이스 방향은 (0,1), (1,2), (0,2) 축 기준으로 하며,
    각 슬라이스에 대해 min-max 정규화와 업스케일을 수행한 뒤
    Grayscale 이미지로 저장됩니다.

    :param npdata: 3차원 GPR 데이터 (RD3에서 읽은 NumPy 배열)
    :type npdata: numpy.ndarray
    :param savepath: 이미지 저장 경로 (폴더)
    :type savepath: str

    """
    savepath = "./results"
    name = filename.split('.')[0]
    # 데이터가 3차원인지 확인
    if npdata.ndim != 3:
        raise ValueError("입력 데이터는 반드시 3차원이어야 합니다.")

    os.makedirs(savepath, exist_ok=True)

    slice_configs = [
        (f"{name}_종단면_axis0", 12, lambda i: npdata[i, :, :], npdata.shape[0], (20.0, 5.0)),
        (f"{name}_평단면_axis1", depth, lambda i: npdata[:, i, :], npdata.shape[1], (20.0, 3.0)),
        (f"{name}_횡단면_axis2", 100, lambda i: npdata[:, :, i].T, npdata.shape[2], (3.0, 8.0)),
    ]  # name,       savepoint,     slicer,              max_index,       figsize

    for name, savepoint, slicer, max_index, figsize in slice_configs:
        slice_data = slicer(savepoint)
        norm_img = normalize_minmax(slice_data, vmin=-3000, vmax=3000)
        upscaled = upscale_image(norm_img, scale=4)

        fig = plt.figure(figsize=figsize, dpi=100)
        plt.imshow(upscaled, cmap="gray", aspect='auto')
        plt.axis('off')
        fig.savefig(os.path.join(savepath, f"{name}_{number}.png"), bbox_inches='tight', pad_inches=0)
        plt.close(fig)

    print(f"슬라이스 이미지가 '{savepath}' 디렉토리에 저장되었습니다.")


def road_image_save(road_image, BASENAME, chunk_list):
    name = BASENAME.split('.')[0]
    for n in range(len(chunk_list)):
        start, end = chunk_list[n]
        road_image.crop((start, 0, end, 80)).save(f"results/{name}_도로면_{n}.png", format='PNG')

    print(f"이미지 저장 완료: ./results/{name}_도로면_{n}.png")
