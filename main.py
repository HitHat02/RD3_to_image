from typing import List
from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import shutil, os

from image200 import run



app = FastAPI()

UPLOAD_DIR = "./uploads"

app.mount("/results", StaticFiles(directory="results"), name="results")
templates = Jinja2Templates(directory="templates")

process_done = False

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    '''
    홈화면 png이미지를 표시하도록 할려고 했지만 잘 안됨
    '''
    png_files = get_png_list()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "process_done": process_done,
        "png_files": png_files
    })


@app.post("/upload")
async def upload(request: Request, files: List[UploadFile] = File(...)):
    '''
    List[UploadFile] 형식으로 받은 파일을을
    UPLOAD_DIR path에 파일을 저장하는 형식
    '''
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    for file in files:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

    return templates.TemplateResponse("index.html", {
        "request": request,
        "message": f"{len(files)}개 파일 업로드 완료",
        "show_run": True
    })

@app.post("/run-process")
async def run_process(request: Request):
    '''
    from image200 import run을 하여
    uploads 디렉토리에 있는 파일들을 이미지로 만들어서
    results 디렉토리에 저장함
    그 이후 create_zip_from_results 함수를 이용하여 .PNG 이미지들을 .zip형식으로 수정
    파일이름을 읽어 전역변수 filename에 넣고 추후 저장할때 파일명을 자동으로 지정해줌
    '''
    global process_done
    os.makedirs("results", exist_ok=True)
    global filename
    for root, dirs, files in os.walk("./uploads"):
        for name in files:
            if name.endswith(".rd3"):
                filename = str(name[:-4])
    run()
    create_zip_from_results(output_zip_path=f"results/{filename}.zip")
    process_done = True
    return templates.TemplateResponse("index.html", {
        "request": request,
        "message": "run() 실행 완료",
        "process_done": True
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
    return [f for f in os.listdir(result_dir) if f.endswith(".png")]

from zipfile import ZipFile

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