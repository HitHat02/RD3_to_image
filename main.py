import numpy as np
import os
import matplotlib.pyplot as plt
from rd3lib import readRd3, reshapeRd3, cutRd3, plot_gpr_image, apply_filter

path = "C:\\Users\\admin\\Desktop\\SBR_013\\00\\"
filename = "SBR_013.rd3"



# def alignChannel(path, filename):
#     """
#      - 0.044, 2.58 으로 거리가 차이나는 채널을 일정하게 맞춰주는 함수
#     """
#     chOffsets = extractionRad(path, filename)
#     chOffsets = np.array(chOffsets)
#     chOffsets -= np.min(chOffsets)
#
#     for i, value in enumerate(chOffsets):
#         if value == 0:
#             continue
#
#
#     # 2. 제일 첫 번째 거를 0으로 만들어야하니까? 평균을 빼야함?(최소값을 뺴야하나? )
#     # 3.
