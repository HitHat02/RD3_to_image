import numpy as np
import os
import matplotlib.pyplot as plt

path = "C:\\Users\\admin\\Desktop\\SBR_013\\00\\"
filename = "SBR_013.rd3"
# class GPRCut:
#     """
#     GPR 데이터를 처리하는 클래스
#     - GPR을 3차원으로 변형 후 원하는 부분만 잘라서 RETURN 해주는 기능 제공

#     """
#     def __init__(self, gpr_data, start_idx, length):
#         """
#         start_idx : 시작지점
#         length : 구해야할 거리
#         """
#         self.gpr = gpr_data
#         self.start_idx = start_idx
#         self.length = length

#     def reshapeRd3(self):
#         trace_count = len(self.gpr) // (25 * 256)
#         reshaped = self.gpr.reshape(trace_count, 25, 256)
#         self.gpr_reshaped = np.zeros((25, 256, trace_count), dtype=np.int16)
#         for ch in range(25):
#             self.gpr_reshaped[ch] = reshaped[:, ch, :].T
#         return self.gpr_reshaped
    
def cutRd3(self):
        end_idx = min(self.start_idx + self.length, self.gpr_reshaped.shape[2])
        return self.gpr_reshaped[:, :, self.start_idx:end_idx]

def fileRead(path, filename):
    with open(path + filename, "rb") as f:
        data = f.read()
    rd3 = np.frombuffer(data, dtype=np.short)
    return rd3


def plot_gpr_image(gpr_cut, channel, cmap='gray'):
    plt.figure(figsize=(12, 6))
    plt.imshow(gpr_cut[channel], aspect='auto', cmap=cmap)
    plt.title(f"GPR img")
    plt.tight_layout()
    plt.show()



if __name__ == "__main__":

    raw_data = fileRead(path, filename)
    processor = GPRCut(raw_data, start_idx=780, length=680)
    processor.reshapeRd3()
    cut = processor.cutRd3()

    plot_gpr_image(cut, channel=15)


def readRad(path, filename):
    """
    파일 확장자를 rad로 변경해주고 rad 내부를 읽어오는 함수
    """
    nameRad = filename[:-3]+"rad"
    with open(path + nameRad, "rb") as f:
        data = f.read()
    # 숫자 데이터
    rad = np.frombuffer(data, dtype=np.short)

    # 헤더 텍스트
    text = data[:].decode("utf-8", errors="ignore")
    return rad, text

def extractionRad(path, filename):
    """
    - .rad 파일 내부의 CH_Y_OFFSETS과 DISTANCE INTERVAL의 값을 추출해 내는 함수

    - path : local의 파일 경로 , string 
    - filename : 파일 경로에 있는 
    """
    # 1. rad 읽어오기 -> rad에서 CH_Y_OFFSETS: 뒤에 있는 부분을 배열에 담아야함
    # 2. 제일 첫 번째 거를 0으로 만들어야하니까? 평균을 빼야함?(최소값을 뺴야하나? )
    # 3. 

    rad, header_text = readRad(path, filename)

    ch_y_offsets = []

    for line in header_text.splitlines():
        if line.startswith("CH_Y_OFFSETS:"):
                ch_y_line = line.split(":", 1)[1].strip()
                chOffsets = [float(x) for x in CH_Y_line.split()]

        elif line.startswith("DISTANCE INTERVAL:"):
             distance_interval = float(line.split(":")[1].strip())
             

    return chOffsets, distance_interval

def alignChannels():
     """
     - 0.044, 2.58 으로 거리가 차이나는 채널을 일정하게 맞춰주는 함수
     """

# 2개의 함수를 만들어야 하나? rad에서 chOffsets을 빼오는거? + alignch하는거