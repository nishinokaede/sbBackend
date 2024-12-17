import base64
import httpx
from fastapi import FastAPI, File, UploadFile, HTTPException, APIRouter
from fastapi.responses import JSONResponse
from typing import List
from io import BytesIO
import uuid
import json
from fastapi.middleware.cors import CORSMiddleware

sakura_router = APIRouter()

with open("/Users/densu/Code/sbProject/data/config.json", "r") as file:
      GITHUB_CONFIG = json.load(file)

# GitHub API 配置
GITHUB_TOKEN = GITHUB_CONFIG.token  # 替换为你的 GitHub Token
GITHUB_REPO = GITHUB_CONFIG.repo  # 替换为你的仓库名
GITHUB_API_URL = "https://api.github.com/repos/{}/contents/".format(GITHUB_REPO)
GITHUB_BRANCH = "main"  # 你要上传到的分支，默认通常是 'main'
# urls.json 文件路径
URLS_FILE_PATH = "../data/urls.json"

# 记录图片 URL 到 urls.json 文件
def record_url_to_json(file_url: str):
    try:
        # 读取现有的 urls.json 文件
        try:
            with open(URLS_FILE_PATH, "r") as file:
                urls_data = json.load(file)
        except FileNotFoundError:
            urls_data = []

        # 添加新的 URL
        urls_data.append(file_url)

        # 将更新后的数据写回文件
        with open(URLS_FILE_PATH, "w") as file:
            json.dump(urls_data, file, indent=4)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to record URL: {str(e)}")

# 上传文件到 GitHub 仓库
async def upload_image_to_github(file_name: str, file_data: BytesIO):
    new_file_name = f"{uuid.uuid4()}.jpg"
    # 将图片数据转换为 base64 编码
    encoded_image = base64.b64encode(file_data.getvalue()).decode()

    # 目标路径：img/{file_name}
    target_path = f"img/{new_file_name}"

    # 请求体
    data = {
        "message": "Upload image to image directory",
        "content": encoded_image,
        "branch": GITHUB_BRANCH
    }

    headers = {
        "Authorization": f"token {GITHUB_TOKEN}"
    }

    async with httpx.AsyncClient() as client:
        response = await client.put(f"{GITHUB_API_URL}{target_path}", json=data, headers=headers)

    if response.status_code == 201:
        file_url = f"https://nishinokaede.github.io/2sakuraPicBot/{target_path}"
         # 记录 URL 到 urls.json
        record_url_to_json(file_url)
        return {
            "code": 200,
            "message": "图片上传成功",
            "image_url": file_url
        }
    else:
        raise HTTPException(status_code=response.status_code, detail="GitHub upload failed")

# 接口：接收上传的图片并上传到 GitHub img 目录
@sakura_router.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    image_data = await file.read()
    file_name = file.filename

    try:
        result = await upload_image_to_github(file_name, BytesIO(image_data))
        return JSONResponse(content=result)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


# 读取 urls.json 文件并分页返回
@sakura_router.get("/get-urls")
async def get_urls(page: int = 1, page_size: int = 20):
    try:
        # 读取 urls.json 文件
        try:
            with open(URLS_FILE_PATH, "r") as file:
                urls_data = json.load(file)
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="urls.json file not found")

        # 计算分页起始和结束位置
        start_index = (page - 1) * page_size
        end_index = start_index + page_size

        # 获取当前页的数据
        paged_urls = urls_data[start_index:end_index]

        if not paged_urls:
            raise HTTPException(status_code=404, detail="No more URLs found")

        return {
            "code": 200,
            "message": "URLs retrieved successfully",
            "data": paged_urls,
            "page": page,
            "page_size": page_size,
            "total_count": len(urls_data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read URLs: {str(e)}")
