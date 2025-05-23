'''
데이터 전처리 및 slicing, filtering 등을 담당하는 모듈
'''

import numpy as np
from rd3lib.io import extractionRad

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

def cutRd3(rd3, start_m, length_m,path, filename):
    """
    3차원 RD3 GPR 데이터를 지정된 시작 인덱스와 길이에 따라 슬라이싱합니다.

    :param rd3: 원본 3차원 GPR 데이터 (채널, 깊이, 트레이스 수)
    :type rd3: numpy.ndarray
    :param start_m:시작 거리(미터 단위)
    :param length_m: 자르고 싶은 거리 길이(미터 단위)
    :return: 잘라낸 범위의 3차원 GPR 데이터
    :rtype: numpy.ndarray
    """
    _, distance_interval, _ = extractionRad(path, filename)

    start_idx = int(start_m / distance_interval)
    length = int(length_m / distance_interval)
    end_idx = min(start_idx + length, rd3.shape[2])
    return rd3[:, :, start_idx:end_idx]

def detect_min_max(signal, neg_thresh=-1000, pos_thresh=1000):
    """
    하나의 채널 평균 신호에서 최소/최대값 위치 반환
    alignGround에 사용하는 함수
    """
    min_idx = max_idx = None
    for i in range(len(signal) - 1):
        if min_idx is None and signal[i] < neg_thresh and signal[i+1] - signal[i] > 0:
            min_idx = i
        if min_idx is not None and signal[i] > pos_thresh and signal[i+1] - signal[i] < 0:
            max_idx = i
            break
    return min_idx, max_idx

def alignSignal(path, filename, gpr_data, depth=256):
    """
    GPR 데이터를 채널 간 정렬 및 정규화하는 함수

    :param path: .rad 파일이 존재하는 디렉토리 경로, 문자열(str) 형식
    :param filename: 처리 대상 .rd3 파일 이름, 문자열(str) 형식
    :param gpr_data: (채널 수, 깊이, 거리) 형태의 GPR 데이터 3차원 배열 (np.ndarray)

    :return gpr_normalized: 채널 간 정규화가 적용된 GPR 데이터 3차원 배열 (np.ndarray)
    """
    _, _, ch = extractionRad(path, filename)
    mins, maxs = [], []

    # 1단계: 채널별 ground 평균 계산 후 min/max 탐지
    for i in range(ch):
        signal_avg = np.mean(gpr_data[i, :depth, :], axis=1)
        min_idx, max_idx = detect_min_max(signal_avg)
        if min_idx is not None and max_idx is not None:
            mins.append(signal_avg[min_idx])
            maxs.append(signal_avg[max_idx])
        else:
            # fallback 처리
            mins.append(-1000)
            maxs.append(1000)

    ranges = np.array(maxs) - np.array(mins)
    factors = np.sqrt(ranges.max() / ranges)

    # 2단계: 채널별 정규화
    gpr_normalized = gpr_data * factors[:, None, None]
    return gpr_normalized


def detect_ground_index(signal, neg_thresh=-1000, pos_thresh=1000):
    """
    평균 신호에서 지표면 범위를 찾아 중간 ground index 반환
    alignGround에 사용하는 함수
    """
    min_idx = max_idx = None
    for i in range(len(signal) - 1):
        if min_idx is None and signal[i] < neg_thresh and signal[i+1] - signal[i] > 0:
            min_idx = i
        if min_idx is not None and signal[i] > pos_thresh and signal[i+1] - signal[i] < 0:
            max_idx = i
            break
    if min_idx is not None and max_idx is not None:
        for i in range(min_idx, max_idx + 1):
            if signal[i] > 0:
                return round((i + (min_idx + max_idx) / 2) / 2)
    return 10  # fallback index

def alignGround(path, filename, gpr_data, depth=256, pad=10):
    """
    각 채널마다 지표면의 반사 위치가 서로 다를 수 있기 때문에,
    GPR 데이터에서 지표면(ground)을 기준으로 정렬한 결과를 반환해주는 함수

    :param path: .rad 파일이 존재하는 디렉토리 경로, 문자열(str) 형식
    :param filename: 처리 대상 .rd3 파일 이름, 문자열(str) 형식
    :param gpr_data: (채널 수, 깊이, 거리) 형태의 GPR 데이터 3차원 배열 (np.ndarray)

    :return gpr_reshaped2: 지표면을 기준으로 정렬된 GPR 데이터 (np.ndarray), shape = (채널 수, 256, 거리 수)
    """
    _, _, ch = extractionRad(path, filename)
    ground_aligned = np.zeros_like(gpr_data)

    for i in range(ch):
        signal_avg = np.mean(gpr_data[i, :depth, :], axis=1)
        signal_avg = signal_avg.astype(np.int32)
        ground_idx = detect_ground_index(signal_avg)

        start = max(ground_idx - pad, 0)
        end = depth
        length = end - start

        ground_aligned[i, :length, :] = gpr_data[i, start:end, :]

    return ground_aligned

def alignChannel(path, filename, gpr_data, depth=256):
    """
    0.044, 2.58 으로 거리가 차이나는 채널 간 위치 오차 보정해주는 함수

    :param path: .rad 파일이 존재하는 디렉토리 경로, 문자열(str) 형식
    :param filename: 처리 대상 .rd3 파일 이름, 문자열(str) 형식
    :param gpr_reshaped2: 지표면 기준으로 정렬된 GPR 데이터 3차원 배열 (np.n

    return gpr_reshaped2: 채널 간 수평 정렬이 적용된 GPR 데이터 (np.ndarray), shape = (채널 수, 256, 거리 수)
    """
    ch_offsets, distance_interval, _ = extractionRad(path, filename)
    offsets = np.array(ch_offsets) - np.min(ch_offsets)  # 가장 가까운 채널을 기준으로 정렬
    gpr_aligned = np.copy(gpr_data)

    for ch_idx, offset in enumerate(offsets):
        if offset == 0:
            continue

        shift_px = int(offset / distance_interval)
        gpr_aligned[ch_idx, :, shift_px:] = gpr_data[ch_idx, :, :-shift_px]

        # 앞쪽 빈 공간은 평균값으로 채움 (방향성 보존)
        mean_values = np.mean(gpr_aligned[ch_idx, :, shift_px:], axis=1, keepdims=True)
        gpr_aligned[ch_idx, :, :shift_px] = mean_values

    return gpr_aligned