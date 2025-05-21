'''
데이터 전처리 및 slicing, filtering 등을 담당하는 모듈
'''

import numpy as np
from rd3lib.io import extractionRad

def reshapeRd3(raw_rd3):
    '''
    1차원의 gpr 바이너리 파일을 3차원 바이너리 파일로 수정하는 함수
    파일의 형태는 (깊이, 채널, 길이)형태로 나옴

    :param raw_rd3: 1차원 gpr np 파일(파일을 바로 읽었을때)
    :return: 3차원 gpr np 파일
    '''
    trace_count = len(raw_rd3) // (25 * 256)
    gpr = raw_rd3.reshape(trace_count, 25, 256)

    gpr_reshaped = np.zeros((25, 256, trace_count), dtype=np.int16)
    for ch in range(25):
        gpr_reshaped[ch] = gpr[:, ch, :].T

    return gpr_reshaped

def cutRd3(rd3, start_idx, length):
    '''
    원하는 크기로 3차원 rd3 파일을 수정해주는 함수

    :param rd3: 3차원 gpr np 파일
    :param start_idx: 자르기 시작할 int 수치
    :param length: 자를려고 하는 크기의 int 수치
    :return: 잘라서 크기가 작아진 3차원 gpr np 파일
    '''

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
        for align_depth_001 in range(0,256):
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
    minimum_idx = 0
    maximum_idx = 0

    for align_channel in range(0, ch):
        ground_avg_list = []
        for align_depth_001 in range(0, 256):
            ground_avg_list.append(np.mean(gpr_reshaped[align_channel][align_depth_001, :]))
        ground_avg_list = np.int32(ground_avg_list)

        for align_depth_002 in range(0, len(ground_avg_list - 1)):
            if ground_avg_list[align_depth_002] < - 1000 and ground_avg_list[align_depth_002 + 1] - ground_avg_list[
                align_depth_002] > 0:
                minimum = ground_avg_list[align_depth_002]
                minimum_idx = align_depth_002
                break

        for align_depth_003 in range(minimum_idx, len(ground_avg_list - 1)):
            if ground_avg_list[align_depth_003] > 1000 and ground_avg_list[align_depth_003 + 1] - ground_avg_list[align_depth_003] < 0:
                maximum = ground_avg_list[align_depth_003]
                maximum_idx = align_depth_003
                break

        for align_depth_004 in range(minimum_idx, maximum_idx + 1):
            if ground_avg_list[align_depth_004] > 0:
                uint_idx = align_depth_004
                mean_idx = (minimum_idx + maximum_idx) / 2
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

    gpr_aligned = np.copy(gpr_reshaped2)
    chOffsets = np.array(chOffsets)
    chOffsets -= np.min(chOffsets)

    for i, value in enumerate(chOffsets):
        if value == 0:
            continue
        gpr_aligned[i, :, int(value/distance_interval):] = gpr_reshaped2[i, :, :-int(value/distance_interval)]
        for align_depth3 in range(0, 256):
            gpr_aligned[i, align_depth3, :int(value/distance_interval)] = gpr_aligned[i, align_depth3, :int(value/distance_interval)] * 0  + int(np.mean(gpr_aligned[i, align_depth3, int(value/distance_interval):]))

    return gpr_aligned