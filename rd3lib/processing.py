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


def alignSignal(path, filename, gpr_reshaped):
    """
    GPR 데이터를 채널 간 정렬 및 정규화하는 함수

    :param path: .rad 파일이 존재하는 디렉토리 경로, 문자열(str) 형식
    :param filename: 처리 대상 .rd3 파일 이름, 문자열(str) 형식
    :param gpr_reshaped: (채널 수, 깊이, 거리) 형태의 GPR 데이터 3차원 배열 (np.ndarray)

    :return gpr_reshaped: 채널 간 정규화가 적용된 GPR 데이터 3차원 배열 (np.ndarray)
    """
    chOffsets, distance_interval, ch = extractionRad(path, filename)
    minimum_list = []
    maximum_list = []

    for align_channel in range(ch):
        ground_avg_list = []
        for align_depth_001 in range(256):
            ground_avg_list.append(np.mean(gpr_reshaped[align_channel][align_depth_001, :]))
        ground_avg_list = np.int32(ground_avg_list)

        for align_depth_002 in range(0, len(ground_avg_list - 1)):
            if ground_avg_list[align_depth_002] < -1000 and ground_avg_list[align_depth_002 + 1] - ground_avg_list[align_depth_002] > 0:
                minimum = ground_avg_list[align_depth_002]
                min_idx = align_depth_002
                minimum_list.append(minimum)
                break
        
        for align_depth_003 in range(min_idx, len(ground_avg_list - 1)):
            if ground_avg_list[align_depth_003] > 1000 and ground_avg_list[align_depth_003 +1] - ground_avg_list[align_depth_003] < 0:
                maximum = ground_avg_list[align_depth_003]
                max_idx = align_depth_003
                maximum_list.append(maximum)
                break
        
        range_list = np.array(maximum_list) - np.array(minimum_list)
        multiple_list = (range_list.max() / range_list)**0.5

        range_list = np.array(maximum_list) - np.array(minimum_list)
        multiple_list = (range_list.max() / range_list)**0.5

        align_test2_mean_mult = np.empty((gpr_reshaped.shape))
        for i in range(gpr_reshaped.shape[1]):
            for j in range(gpr_reshaped.shape[2]):
                align_test2_mean_mult[:, i, j] = gpr_reshaped[:, i, j] * multiple_list

        gpr_reshaped = align_test2_mean_mult
        return gpr_reshaped




def alignGround(path, filename, gpr_reshaped):
    """
    각 채널마다 지표면의 반사 위치가 서로 다를 수 있기 때문에,
    GPR 데이터에서 지표면(ground)을 기준으로 정렬한 결과를 반환해주는 함수

    :param path: .rad 파일이 존재하는 디렉토리 경로, 문자열(str) 형식
    :param filename: 처리 대상 .rd3 파일 이름, 문자열(str) 형식
    :param gpr_reshaped: (채널 수, 깊이, 거리) 형태의 GPR 데이터 3차원 배열 (np.ndarray)
    
    :return gpr_reshaped2: 지표면을 기준으로 정렬된 GPR 데이터 (np.ndarray), shape = (채널 수, 256, 거리 수)
    """
    chOffsets, distance_interval, ch = extractionRad(path, filename)

    ground_idx_list = [10 for i in range(ch)]
    min_idx = 0
    max_idx = 0

    for align_channel in range(ch):
        ground_avg_list = []
        for align_depth_001 in range(256):
            ground_avg_list.append(np.mean(gpr_reshaped[align_channel][align_depth_001, :]))
        ground_avg_list = np.int32(ground_avg_list)

        for align_depth_002 in range(0, len(ground_avg_list - 1)):
            if ground_avg_list[align_depth_002] < -1000 and ground_avg_list[align_depth_002 + 1] - ground_avg_list[align_depth_002] > 0:
                minimun = ground_avg_list[align_depth_002]
                min_idx = align_depth_002
                break
        
        for align_depth_003 in range(min_idx, len(ground_avg_list - 1)):
            if ground_avg_list[align_depth_003] > 1000 and ground_avg_list[align_depth_003 + 1] - ground_avg_list[align_depth_003] < 0:
                maximum = ground_avg_list[align_depth_003]
                max_idx = align_depth_003
                break
        
        for align_depth_004 in range(min_idx, max_idx + 1):
            if ground_avg_list[align_depth_004] > 0:
                uint_idx = align_depth_004
                mean_idx = (min_idx + max_idx) / 2
                ground_idx = round((uint_idx + mean_idx) / 2)
                ground_idx_list[align_channel] = ground_idx
                break

    gpr_reshaped2 = np.zeros((ch, 256, len(gpr_reshaped[0][0])))
    for align_channel3 in range(0, ch):
        gpr_reshaped2[align_channel3, 0:256 - ground_idx_list[align_channel3] + 10, :]\
            = gpr_reshaped[align_channel3, ground_idx_list[align_channel3] - 10:256, :]
    return gpr_reshaped2

def alignChannel(path, filename, gpr_reshaped2):
    """
    0.044, 2.58 으로 거리가 차이나는 채널 간 위치 오차 보정해주는 함수

    :param path: .rad 파일이 존재하는 디렉토리 경로, 문자열(str) 형식
    :param filename: 처리 대상 .rd3 파일 이름, 문자열(str) 형식
    :param gpr_reshaped2: 지표면 기준으로 정렬된 GPR 데이터 3차원 배열 (np.n
    
    return gpr_reshaped2: 채널 간 수평 정렬이 적용된 GPR 데이터 (np.ndarray), shape = (채널 수, 256, 거리 수)
    """
    chOffsets, distance_interval, ch = extractionRad(path, filename)
    print(f"chOffsets:{chOffsets}")
    print(f"distance_interval:{distance_interval}")
    gpr_aligned = np.copy(gpr_reshaped2)
    chOffsets = np.array(chOffsets)
    chOffsets -= np.min(chOffsets)

    for i, value in enumerate(chOffsets):
        if value == 0:
            continue
        val_scalar = int(value / distance_interval)  # val_scalar : 한 체널에 대한 shift 된 픽셀 개수를 뜻함
        print(f"{i}번째 val_scalar: {val_scalar}")
        gpr_aligned[i, :, val_scalar:] = gpr_reshaped2[i, :, :-val_scalar]
        for align_depth3 in range(0, 256):
            gpr_aligned[i, align_depth3, :val_scalar] = (gpr_aligned[i, align_depth3, :val_scalar] * 0.1
                                                        + int(np.mean(gpr_aligned[i, align_depth3, val_scalar:])))

    return gpr_aligned