'''
rd3, rad 파일 읽기 등 I/O 관련 함수
'''
import numpy as np

def readRd3(filepath):
    with open(filepath, "rb") as f:
        data = f.read()
    rd3_data = np.frombuffer(data, dtype=np.short)
    return rd3_data