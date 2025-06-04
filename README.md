# RD3_to_image

가상환경을 구성하고 main.py에 파라미터를 작성 작성 후 실행

## main_old.py 코드에 경로 및 파일명을 기입해야함.
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
python main_old.py --path "C:\\Users\\HYH\\Desktop\\AI_분석\\01 RAWDATA\\SBR_013\\00\\" --filename "SBR_013.rd3" --start_m 0.1 --length_m 14.6 --save_path "C:\\Users\\HYH\\Desktop\\AI_분석\\01 RAWDATA\\SBR_013\\00" --save_point "[22, 20, 130]" --image_size "[(8.0, 5.0), (8.0, 3.0), (3.0, 6.0)]"
```

## image200.py의 설명
### 사용법
- 파일안에 run()함수를 실행하면 프로세스 대로 진행됨
- 같은 프로젝트 디렉토리에 'results', 'uploads' 가 있어야 함.
- 'uploads' 디렉토리에는 rd3, rad, rst 파일이 존재해야 함.
- 'results' 디렉토리에는 image200.py의 함수의 로직에 따라서 결과물을 저장함.

## main.py로 이용한 인터넷 웹 앱 개발
- uvicorn main:app --reload --host 0.0.0.0 --port 8000로 실행하면 됨