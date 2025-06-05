import os
import pytest
from fastapi.testclient import TestClient
from main import app, clear_directories, RESULT_DIR
from io import BytesIO

client = TestClient(app)

@pytest.fixture(scope="function", autouse=True)
def clean_dirs():
    clear_directories()
    yield
    clear_directories()


def test_upload_with_wrong_extension():
    # 잘못된 확장자 파일 업로드
    files = [("files", ("fake.txt", b"fake content", "text/plain"))]
    response = client.post("/upload", files=files)
    assert response.status_code == 200
    assert "rd3, rad, rst 파일만 사용할 수 있습니다." in response.text


def test_full_process_success():
    # 실제 test_uploads 디렉토리에 있는 파일을 읽어서 업로드
    upload_dir = "test_uploads"
    filenames = ["test.rd3", "test.rad", "test.rst"]

    files = []
    for fname in filenames:
        path = os.path.join(upload_dir, fname)
        assert os.path.exists(path), f"파일 누락: {path}"
        files.append(("files", (fname, open(path, "rb"), "application/octet-stream")))

    # 1. 업로드
    upload_resp = client.post("/upload", files=files)
    assert upload_resp.status_code == 200
    assert "error" not in upload_resp.text

    # 2. run-process 호출
    run_resp = client.post("/run-process")
    assert run_resp.status_code == 200
    assert "error" not in run_resp.text

    # 3. download 호출
    download_resp = client.get("/download")
    assert download_resp.status_code == 200
    assert download_resp.headers["content-type"] == "application/x-zip-compressed"
    assert download_resp.headers["content-disposition"].endswith(".zip\"")

    # 4. 실제 결과 zip 파일 존재 확인
    zip_files = [f for f in os.listdir(RESULT_DIR) if f.endswith(".zip")]
    assert len(zip_files) > 0