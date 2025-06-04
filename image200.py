from rd3lib import image_save, road_image_save
from rd3lib import extractionRad, cut_200m
from rd3lib.utils import rd3_process, chunk_range
import os
from road import roadDrawing

def run():
    DIRNAME = None
    BASENAME = None

    for root, dirs, files in os.walk("./uploads"):  # ✅ 슬래시 방향 수정
        for name in files:
            if name.endswith(".rd3"):
                DIRNAME = str(root)
                BASENAME = str(name)
                break  # ✅ 하나만 찾고 멈춤 (필요하다면)

    if not DIRNAME or not BASENAME:
        raise FileNotFoundError("'.rd3' 파일을 uploads 폴더에서 찾을 수 없습니다.")

    # 이후 로직 그대로
    rd3 = rd3_process(DIRNAME, BASENAME)
    _, distance_interval, _ = extractionRad(DIRNAME, BASENAME)
    chunk_list = chunk_range(rd3.shape[2], distance_interval)
    rd3list = cut_200m(rd3, chunk_list)

    for number in range(len(rd3list)):
        image_save(rd3list[number], BASENAME, number, depth=30)

    roaddrawing = roadDrawing(DIRNAME, BASENAME)
    file_langth = rd3.shape[2]
    img = roaddrawing.makeImg(file_langth)
    road_image_save(img, BASENAME, [[0, 1772]])



