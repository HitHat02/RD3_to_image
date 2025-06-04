from typing import List
from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import shutil, os

from image200 import run



app = FastAPI()

UPLOAD_DIR = "./uploads"
RESULT_DIR = "./results"

app.mount("/results", StaticFiles(directory="results"), name="results")
templates = Jinja2Templates(directory="templates")

process_done = False

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    png_files = get_png_list()
    return templates.TemplateResponse("Jinja_front.html", {
        "request": request,
        "process_done": process_done,
        "png_files": png_files
    })


@app.post("/upload")
async def upload(request: Request, files: List[UploadFile] = File(...)):
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    for file in files:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

    global process_done
    os.makedirs("results", exist_ok=True)
    global filename
    for root, dirs, files in os.walk("./uploads"):
        for name in files:
            if name.endswith(".rd3"):
                filename = str(name[:-4])

    #  # 필수 파일 체크
    # if not all(ext in [f.split('.')[-1] for f in filenames] for ext in ["rd3", "rad", "rst"]):
    #     return templates.TemplateResponse("Jinja_front.html", {
    #         "request": request,
    #         "ready": False,
    #         "error": "rd3, rad, rst 파일이 모두 필요합니다."
    #     })
    
    run()
    create_zip_from_results(output_zip_path=f"results/{filename}.zip")

    result_images = [f for f in os.listdir(RESULT_DIR) if f.endswith(".png")]
    return templates.TemplateResponse("Jinja_front.html", {
        "request": request,
        "ready": True,
        "images": result_images,
    })

@app.get("/download")
async def download_result():
    return FileResponse(f"results/{filename}.zip", filename=f"{filename}.zip")

@app.post("/clear")
async def clear_and_redirect():
    global process_done
    process_done = False  # 상태 초기화
    clear_directories()
    return RedirectResponse(url="/", status_code=303)


def get_png_list():
    result_dir = "./results"
    return [f for f in os.listdir(result_dir) if f.endswith(".png")]

from zipfile import ZipFile

def create_zip_from_results(output_zip_path: str, result_dir: str = "./results"):
    with ZipFile(output_zip_path, "w") as zipf:
        for file in os.listdir(result_dir):
            if file.endswith(".png"):
                zipf.write(os.path.join(result_dir, file), arcname=file)

def clear_directories():
    for dir_path in ["uploads", "results"]:
        if os.path.exists(dir_path):
            for filename in os.listdir(dir_path):
                file_path = os.path.join(dir_path, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)