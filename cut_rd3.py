import numpy as np

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
