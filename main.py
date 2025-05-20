import numpy as np
from rd3lib import readRd3, reshapeRd3, cutRd3, plot_gpr_image, apply_filter


def rd3_run(rd3_path, start_idx, length):
    rd3 = readRd3(rd3_path)
    rd3 = reshapeRd3(rd3)
    rd3 = apply_filter(rd3)
    cut_rd3 = cutRd3(rd3, start_idx, length)
    return cut_rd3



if __name__ == "__main__":
    rd3_path = "C:\\Users\\HYH\\Desktop\\AI_분석\\01 RAWDATA\\SBR_013\\00\\SBR_013.rd3"
    start_idx = 200
    length = 800

    processor = rd3_run(rd3_path, start_idx, length)

    plot_gpr_image(processor, channel=9)


