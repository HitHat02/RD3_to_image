import argparse
from rd3lib import readRd3, reshapeRd3, cutRd3, plot_gpr_image, apply_filter, image_save, alignSignal, alignGround, alignChannel
import ast

def gpr_processing(path, filename, rd3):
    '''
    GPR 전처리 파이프라인
    1. 1차원 바이너리 파일을 3차원으로 만들고
    2. 각채널 정규화
    3. 지표면 정렬
    4. 채널간 수평 보정
    '''
    rd3 = reshapeRd3(rd3)
    rd3 = alignSignal(path, filename, rd3)
    rd3 = alignGround(path, filename, rd3)
    rd3 = alignChannel(path, filename, rd3)
    rd3 = apply_filter(rd3)
    return rd3

def main():
    parser = argparse.ArgumentParser(description="GPR 데이터 전처리 및 이미지 저장")
    parser.add_argument('--path', required=True, help='RD3 파일이 있는 디렉토리 경로')
    parser.add_argument('--filename', required=True, help='RD3 파일 이름')
    parser.add_argument('--start_idx', type=int, required=True, help='이미지 자를 시작 인덱스')
    parser.add_argument('--length', type=int, required=True, help='자를 길이')
    parser.add_argument('--save_path', required=True, help='저장할 디렉토리 경로')
    parser.add_argument('--save_point', required=True, help='종횡평단면 이미지 자를 위치값을 가지는 리스트')
    parser.add_argument('--image_size', required=True, help='종횡평단면 이미지 크키값을 가지는 리스트')
    args = parser.parse_args()

    # 문자열을 리스트로 변환
    save_point = ast.literal_eval(args.save_point)
    image_size = ast.literal_eval(args.image_size)

    # 파일 읽기
    rd3 = readRd3(args.path, args.filename)

    # 전처리
    rd3 = gpr_processing(args.path, args.filename, rd3)

    # 이미지 자르기
    rd3 = cutRd3(rd3, args.start_idx, args.length)

    # 이미지 저장
    image_save(rd3, args.save_path, save_point, image_size)

    # GPR 이미지 시각화 (기본 채널 9)
    plot_gpr_image(rd3, channel=9)

if __name__ == '__main__':
    main()