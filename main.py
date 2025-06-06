from typing import List
from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import shutil
import os
from image200 import run
from zipfile import ZipFile
import os
import re
from collections import defaultdict


app = FastAPI()

UPLOAD_DIR = "./uploads"
RESULT_DIR = "./results"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(RESULT_DIR, exist_ok=True)
app.mount("/results", StaticFiles(directory="results"), name="results")
templates = Jinja2Templates(directory="templates")

process_done = False

@app.get("/", response_class=HTMLResponse)
def home(request: Request):

    return templates.TemplateResponse(request, "Jinja_front.html", {
        "request": request,
        "process_done": process_done
    })


@app.post("/upload")
async def upload(request: Request, files: List[UploadFile] = File(...)):
    '''
    List[UploadFile] 형식으로 받은 파일을을
    UPLOAD_DIR path에 파일을 저장하는 형식
    '''
    clear_directories()
    for file in files:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

    # 허용되지 않은 확장자 검사
    filenames = os.listdir(UPLOAD_DIR)
    required_exts = {"rd3", "rad", "rst"}
    uploaded_exts = set([f.split('.')[-1].lower() for f in filenames])
    disallowed_exts = uploaded_exts - required_exts
    if disallowed_exts:
        return templates.TemplateResponse(request, "Jinja_front.html", {
            "request": request,
            "ready": False,
            "error": "rd3, rad, rst 파일만 사용할 수 있습니다.",
            "images": []
        })

    global process_done
    process_done = False

    return templates.TemplateResponse(request, "Jinja_front.html", {
        "request": request,
        "upload": True,
        "ready": False,
    })


@app.post("/run-process")
async def process(request: Request):
    '''
    from image200 import run을 하여
    uploads 디렉토리에 있는 파일들을 이미지로 만들어서
    results 디렉토리에 저장함
    그 이후 create_zip_from_results 함수를 이용하여 .PNG 이미지들을 .zip형식으로 수정
    파일이름을 읽어 전역변수 filename에 넣고 추후 저장할때 파일명을 자동으로 지정해줌
    '''
    filenames = os.listdir(UPLOAD_DIR)
    required_exts = {"rd3", "rad", "rst"}
    uploaded_exts = set([f.split('.')[-1].lower() for f in filenames])


    # 정상 실행 조건(rd3, rad, rst 파일이 모두 존재해야 함)
    if not required_exts.issubset(uploaded_exts):
        return templates.TemplateResponse(request, "Jinja_front.html", {
            "request": request,
            "ready": False,
            "error": "rd3, rad, rst 파일이 모두 필요합니다.",
            "images": []
        })

    global filename
    for name in filenames:
        if name.endswith(".rd3"):
            filename = name[:-4]

    run()
    create_zip_from_results(output_zip_path=f"results/{filename}.zip")
    result_images = get_png_list()

    return templates.TemplateResponse(request, "Jinja_front.html", {
        "request": request,
        "ready": True,
        "images": result_images
    })

@app.get("/download")
async def download_result():
    '''
    run_process에서 가져온 전역변수로 파일명을 수정하여 다운로드 하게 하는 부분
    '''
    return FileResponse(f"results/{filename}.zip", filename=f"{filename}.zip")

@app.post("/clear")
async def clear_and_redirect():
    '''
    버튼을 누르면 clear_directories가 사용되어
    results, uploads 디렉토리에 있는 파일들이 모두 삭제되고
    홈으로 돌아감
    '''
    global process_done
    process_done = False  # 상태 초기화
    clear_directories()
    return RedirectResponse(url="/", status_code=303)

def get_png_list():
    result_dir = "./results"
    files = [f for f in os.listdir(result_dir) if f.endswith(".png")]

    pattern = re.compile(r"_(\d+)\.png$")
    grouped = defaultdict(list)

    for file in files:
        match = pattern.search(file)
        if match:
            index = int(match.group(1))
            grouped[index].append(file)

    def sort_key(name):
        # 도로, 평단, 종단 순서가 중요
        if "도로" in name:
            return 0
        elif "평단" in name:
            return 1
        elif "종단" in name:
            return 2
        # 횡단은 이 리스트에 포함시키지 않습니다. (별도 처리)
        else:
            return 99 # 이외의 파일은 마지막으로 보냅니다.

    final_sorted_groups = []

    for index in sorted(grouped.keys()):
        current_group_files = sorted(grouped[index], key=sort_key)

        main_images = [] # 도로, 평단, 종단
        cross_section_image = None # 횡단면

        # 파일들을 분류합니다.
        for file_name in current_group_files:
            if "횡단" in file_name:
                cross_section_image = file_name
            elif "도로" in file_name or "평단" in file_name or "종단" in file_name:
                main_images.append(file_name)

        # main_images를 다시 한번 도로, 평단, 종단 순서로 정렬 (혹시 위에서 제대로 안 되었을 경우 대비)
        # 이 부분은 sort_key가 잘 작동한다면 불필요할 수 있습니다.
        # 명시적인 순서 유지를 위해 재정렬하는 로직을 추가할 수도 있습니다.
        ordered_main_images = [None] * 3 # 도로, 평단, 종단 슬롯
        for file_name in main_images:
            if "도로" in file_name:
                ordered_main_images[0] = file_name
            elif "평단" in file_name:
                ordered_main_images[1] = file_name
            elif "종단" in file_name:
                ordered_main_images[2] = file_name

        final_sorted_groups.append({
            'index': index, # 그룹 인덱스를 함께 넘겨주는 것이 좋습니다.
            'main_images': ordered_main_images, # 도로, 평단, 종단 이미지
            'cross_section_image': cross_section_image # 횡단면 이미지
        })

    print("이미지 정렬 및 그룹화 결과:", final_sorted_groups)
    return final_sorted_groups



def create_zip_from_results(output_zip_path: str, result_dir: str = "./results"):
    '''
    results 안에 있는 png이미지를 zip으로 만들어주는 함수
    '''
    with ZipFile(output_zip_path, "w") as zipf:
        for file in os.listdir(result_dir):
            if file.endswith(".png"):
                zipf.write(os.path.join(result_dir, file), arcname=file)

def clear_directories():
    '''
    디렉토리 안에 있는 파일을 모두 지우는 함수
    '''
    for dir_path in ["uploads", "results"]:
        if os.path.exists(dir_path):
            for filename in os.listdir(dir_path):
                file_path = os.path.join(dir_path, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)