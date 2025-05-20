import numpy as np
from cut_rd3 import reshapeRd3, cutRd3
import os
import matplotlib.pyplot as plt

class GPRProcessor:
    """
    GPR 데이터를 처리하는 클래스
    - GPR을 3차원으로 변형 후 원하는 부분만 잘라서 RETURN 해주는 기능 제공

    """
    def __init__(self, path, start_idx, length):
        """
        start_idx : 시작지점
        length : 구해야할 거리
        """
        self.rd3 = (readRd3(path))
        self.start_idx = 100
        self.length = 200

    def run(self):
        rd3 = reshapeRd3(self.rd3)
        cutrd3 = cutRd3(rd3, self.start_idx, self.length)
        return cutrd3


def readRd3(filepath):
    with open(filepath, "rb") as f:
        data = f.read()
    rd3_data = np.frombuffer(data, dtype=np.short)
    return rd3_data



def plot_gpr_image(rd3_cut, channel, cmap='gray'):
    plt.figure(figsize=(12, 6))
    plt.imshow(rd3_cut[channel], aspect='auto', cmap=cmap)
    plt.title(f"GPR img")
    plt.tight_layout()
    plt.show()



if __name__ == "__main__":
    rd3_path = "C:\\Users\\HYH\\Desktop\\AI_분석\\01 RAWDATA\\SBR_013\\00\\SBR_013.rd3"

    processor = GPRProcessor(rd3_path, start_idx=350, length=800)
    rd3 = processor.run()

    plot_gpr_image(rd3, channel=9)


