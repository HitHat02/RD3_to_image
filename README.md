# RD3_to_image

가상환경을 구성하고 main.py에 파라미터를 작성 작성 후 실행

## main.py 코드에 경로 및 파일명을 기입해야함.
### 파일 읽기 파라미터
- path : 파일이 있는 디렉토리 경로
- filename : 파일 이름(파일 확장자까지 포함)
### 파일 자르기 파라미터
- start_m : 자르고 싶은곳의 시작 지점(미터 단위)
- length_m : 자르고 싶은 파일의 크기(미터 단위)
### 파일 저장 파라미터
- save_path : 저장하고자 하는 디렉토리 경로

### 20250523/ 추후 저장 하기 전에 이미지 크기를 수정할 수 있도록 하는 변수들 추가
- save_point : 종단면, 평단면, 횡단면 순으로 자를려고 하는 위치값을 가지고 있는 리스트
- save_point 예시 - "[채널, 깊이, 거리]"
- image_size : 종단면, 평단면, 횡단면 순으로 이미지 크기 값을 가지고 있는 리스트
- image_size 예시 - "[(종단면 가로세로 값), (평단면 가로세로 값), (횡단면 가로세로 값)]"

## 파일 실행 코드
```bash
python main.py --path "C:\\Users\\HYH\\Desktop\\AI_분석\\01 RAWDATA\\SBR_013\\00\\" --filename "SBR_013.rd3" --start_idx 100 --length 200 --save_path "C:\\Users\\HYH\\Desktop\\AI_분석\\01 RAWDATA\\SBR_013\\00" --save_point "[22, 20, 130]" --image_size "[(8.0, 5.0), (8.0, 3.0), (3.0, 6.0)]"
```