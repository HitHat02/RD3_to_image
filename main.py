import numpy as np
import os
import matplotlib.pyplot as plt

class GPRProcessor:
    """
    GPR 데이터를 처리하는 클래스
    - GPR을 3차원으로 변형 후 원하는 부분만 잘라서 RETURN 해주는 기능 제공

    """
    def __init__(self, gpr_data, start_idx, length):
        """
        start_idx : 시작지점
        length : 구해야할 거리
        """
        self.gpr = gpr_data
        self.start_idx = start_idx
        self.length = length

    def reshapeRd3(self):
        trace_count = len(self.gpr) // (25 * 256)
        reshaped = self.gpr.reshape(trace_count, 25, 256)
        self.gpr_reshaped = np.zeros((25, 256, trace_count), dtype=np.int16)
        for ch in range(25):
            self.gpr_reshaped[ch] = reshaped[:, ch, :].T
        return self.gpr_reshaped

    def cutRd3(self):
        end_idx = min(self.start_idx + self.length, self.gpr_reshaped.shape[2])
        return self.gpr_reshaped[:, :, self.start_idx:end_idx]


def readRd3(filepath):
    with open(filepath, "rb") as f:
        data = f.read()
    gpr_data = np.frombuffer(data, dtype=np.short)
    return gpr_data



def plot_gpr_image(gpr_cut, channel, cmap='gray'):
    plt.figure(figsize=(12, 6))
    plt.imshow(gpr_cut[channel], aspect='auto', cmap=cmap)
    plt.title(f"GPR img")
    plt.tight_layout()
    plt.show()



if __name__ == "__main__":
    rd3_path = "C:\\Users\\admin\\Desktop\\SBR_013\\00\\SBR_013.rd3"

    raw_data = readRd3(rd3_path)
    processor = GPRProcessor(raw_data, start_idx=350, length=800)
    processor.reshapeRd3()
    cut = processor.cutRd3()

    plot_gpr_image(cut, channel=9)

   

