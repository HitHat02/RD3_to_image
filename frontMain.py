import time
from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import os
from datetime import datetime
from typing import List
from image200 import run
import zipfile
import urllib.parse


app = FastAPI()
templates = Jinja2Templates(directory="templates")
templates.env.filters["urlencode"] = lambda u: urllib.parse.quote(u)

SAVE_DIR = "./uploads"
RESULT_DIR = "./results"
os.makedirs(SAVE_DIR, exist_ok=True)
os.makedirs(RESULT_DIR, exist_ok=True)

# Jinja_front.html 파일에서 image 출력하기 위해 mount 설정
from fastapi.staticfiles import StaticFiles
app.mount("/results", StaticFiles(directory=SAVE_DIR), name="images")

# 현재 날짜와 시간 문자열 생성(zip 파일 이름에 사용함)
now = datetime.now()
zip_filename = "results_" + now.strftime("%Y%m%d%H%M%S%f") + ".zip"


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("Jinja_front.html", {"request": request, "ready": False,
        "files": []})


@app.post("/upload", response_class=HTMLResponse)
async def upload_files(request: Request, files: List[UploadFile] = File(...)):
    """
    업로드된 파일을 저장하고 필수 파일 체크 후, 결과를 생성하는 함수
    :param request: FastAPI Request 객체
    :param files: 업로드된 파일 리스트  
    :return: Jinja2 템플릿을 렌더링하여 결과 페이지를 반환
    """
    filenames = []

    for file in files:
        path = os.path.join(SAVE_DIR, file.filename)
        with open(path, "wb") as buffer:
            buffer.write(await file.read())
        filenames.append(file.filename)
 
     # 필수 파일 체크
    if not all(ext in [f.split('.')[-1] for f in filenames] for ext in ["rd3", "rad", "rst"]):
        return templates.TemplateResponse("Jinja_front.html", {
            "request": request,
            "ready": False,
            "error": "rd3, rad, rst 파일이 모두 필요합니다."
        })

    run()

    zip_filename = "results_" + datetime.now().strftime('%Y%m%d%H%M%S%f') + ".zip"
    make_result_zip(RESULT_DIR, zip_filename)

    result_images = [f for f in os.listdir(RESULT_DIR) if f.endswith(".png")]

    return templates.TemplateResponse("Jinja_front.html", {
        "request": request,
        "ready": True,
        "images": result_images,
        "zipfile": zip_filename
    })

def make_result_zip(result_dir: str, zip_name: str) -> str:
    """
    result_dir에 있는 모든 .png 파일을 zip으로 묶어서 반환하는 함수
    :param result_dir: 결과 이미지가 저장된 디렉토리
    :param zip_name: 생성할 zip 파일의 이름
    :return: 생성된 zip 파일의 이름
    """
    # 이미지 저장 완료까지 잠깐 대기 
    time.sleep(1)

    zip_path = os.path.join(result_dir, zip_name)
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for file in os.listdir(result_dir):
            if file.endswith(".png"):
                print("zip  포함: ",file)
                file_path = os.path.join(result_dir, file)
                zipf.write(file_path, arcname=file)  # arcname → zip 안의 이름
    return zip_name


@app.get("/download/{zipname}")
def download_folder(zipname: str):
    """
    zip 파일을 다운로드하는 함수
    :param zipname: 다운로드할 zip 파일의 이름
    :return: zip 파일을 다운로드할 수 있는 FileResponse
    """
    file_path = os.path.join(RESULT_DIR, zipname) 
    if os.path.exists(file_path):
        return FileResponse(file_path, filename=zipname, media_type="application/zip")
    return JSONResponse(status_code=404, content={"error": "파일이 없습니다."})
