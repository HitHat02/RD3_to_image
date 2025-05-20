'''
이미지/그래프 그리기 함수들
'''
import matplotlib.pyplot as plt

def plot_gpr_image(rd3_cut, channel, cmap='gray'):
    plt.figure(figsize=(12, 6))
    plt.imshow(rd3_cut[channel], aspect='auto', cmap=cmap)
    plt.title(f"GPR img")
    plt.tight_layout()
    plt.show()