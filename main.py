from rd3lib import readRd3, reshapeRd3, cutRd3, plot_gpr_image, apply_filter, image_save, alignSignal, alignGround, alignChannel

def gpr_processing(rd3):
    rd3 = reshapeRd3(rd3)
    rd3 = alignSignal(path, filename, rd3)
    rd3 = alignGround(path, filename, rd3)
    rd3 = alignChannel(path, filename, rd3)
    rd3 = apply_filter(rd3)
    return rd3

path = "C:\\Users\\HYH\\Desktop\\AI_분석\\01 RAWDATA\\SBR_013\\00\\"
filename = "SBR_013.rd3"
start_m = 100
length_m = 200
save_path = "C:\\Users\\HYH\\Desktop\\AI_분석\\01 RAWDATA\\SBR_013\\00"

# 파일 읽고 데이터 정렬 진행
rd3 = readRd3(path, filename)
rd3 = gpr_processing(rd3)

# 원하는 크기로 이미지를 자름
rd3 = cutRd3(rd3, start_m, length_m)

# 이미지를 저장하는 프로세스 (추후 프런트와 연동하여 원하는 이미지 모양(크기)로 저장하는 모듈 개발 예정)
image_save(rd3, save_path)

plot_gpr_image(rd3, channel=9)



