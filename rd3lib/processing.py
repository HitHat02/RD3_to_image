'''
데이터 전처리 및 slicing, filtering 등을 담당하는 모듈
'''

import numpy as np

def reshapeRd3(raw_rd3):
    """
    1차원 GPR 바이너리 데이터를 (채널, 깊이, 트레이스 수) 형태의 3차원 배열로 변환합니다.
    내부적으로 reshape 및 transpose 과정을 통해 RD3 데이터를 재구성합니다.

    :param raw_rd3: 1차원으로 읽은 RD3 원본 GPR 데이터
    :type raw_rd3: numpy.ndarray
    :return: (채널, 깊이, 트레이스 수)의 형태로 재배열된 3차원 GPR 데이터
    :rtype: numpy.ndarray
    """
    trace_count = len(raw_rd3) // (25 * 256)
    gpr = raw_rd3.reshape(trace_count, 25, 256)

    gpr_reshaped = np.zeros((25, 256, trace_count), dtype=np.int16)
    for ch in range(25):
        gpr_reshaped[ch] = gpr[:, ch, :].T

    return gpr_reshaped

def cutRd3(rd3, start_idx, length):
    """
    3차원 RD3 GPR 데이터를 지정된 시작 인덱스와 길이에 따라 슬라이싱합니다.

    :param rd3: 원본 3차원 GPR 데이터 (채널, 깊이, 트레이스 수)
    :type rd3: numpy.ndarray
    :param start_idx: 잘라낼 시작 위치 (트레이스 방향)
    :type start_idx: int
    :param length: 자를 길이 (트레이스 개수)
    :type length: int
    :return: 잘라낸 범위의 3차원 GPR 데이터
    :rtype: numpy.ndarray
    """
    end_idx = min(start_idx + length, rd3.shape[2])
    return rd3[:, :, start_idx:end_idx]
