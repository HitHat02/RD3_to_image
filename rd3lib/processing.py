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


def alignSignal(path, filename):
    """
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
        
        



def alignGround(path, filename):
    """
    각 채널마다 지표면의 반사 위치가 서로 다를 수 있기 때문에,
    기준선에 맞춰 수직으로 정렬해주는 함수
    """
    ch = extractionRad(path, filename)

    ground_idx_list = [10 for i in range(ch)]
    min_idx = 0
    max_idx = 0

    for align_channel in range(ch):
        ground_avg_list = []
        for align_depth_001 in range(256):
            ground_avg_list.append(np.mean(gpr_reshape[align_channel][align_depth_001, :]))
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

def alignChannel(path, filename):
    """
    채널 간 위치 오차 보정해주는 함수, 오프셋 이동 후 앞 부분은 평균값으로 채워 
    수평정렬을 완료하는 함수
    """
    chOffsets, distance_interval = extractionRad(path, filename)

    gpr_aligned = gpr_reshape
    chOffsets = np.array(chOffsets)
    chOffsets -= np.min(chOffsets)

    for i, value in enumerate(chOffsets):
        if value == 0:
            continue
        gpr_aligned[i,:,int(value/distance_interval):] = gpr_reshape[i,:,:-int(value/distance_interval)]
        for align_depth3 in range(256):
            gpr_aligned[i, align_depth3, :int(value/distance_interval)] = gpr_aligned[i, align_depth3, :int(value/distance_interval)]*0 
            int(np.mean(gpr_aligned[i, align_depth3, int(value/distance_interval):]))