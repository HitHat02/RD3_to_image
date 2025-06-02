from rd3lib import image_save, road_image_save
from rd3lib import extractionRad, cut_200m, chunk_range
from rd3lib import rd3_process
import os
from road import roadDrawing

def run():
    for root, dirs, files in os.walk(".\\uploads"):
        for name in files:
            if name[-4:] == ".rd3":
                DIRNAME = str(root)
                BASENAME = str(name)
    print(BASENAME)

    rd3 = rd3_process(DIRNAME, BASENAME)

    # 벌크 범위를 가지고있는 리스트 변수 계산
    _, distance_interval, _ = extractionRad(DIRNAME, BASENAME)
    chunk_list = chunk_range(rd3.shape[2], distance_interval)

    # 이미지 자르기 list형식의 200m씩 잘려있는 이미지가 들어있음
    rd3list = cut_200m(rd3, chunk_list)

    # 이미지 저장
    for number in range(len(rd3list)):
        image_save(rd3list[number], BASENAME, number, depth=30)

    # 도로면 저장
    roaddrawing = roadDrawing(DIRNAME, BASENAME)
    file_langth = rd3.shape[2]
    img = roaddrawing.makeImg(file_langth)
    road_image_save(img, BASENAME, [[0, 1772]])


