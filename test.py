from rd3lib import readRd3, reshapeRd3, cutRd3, plot_gpr_image, apply_filter


path = "C:\\Users\\HYH\\Desktop\\AI_분석\\01 RAWDATA\\SBR_013\\00\\SBR_013.rd3"
rd3 = readRd3(path)
start_idx = 100
length = 200
rd3 = reshapeRd3(rd3)
rd3 = apply_filter(rd3)
rd3 = cutRd3(rd3, start_idx, length)
plot_gpr_image(rd3, channel=9)


