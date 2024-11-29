from fastapi import APIRouter, Query
from tools.xhs import get_xhs_img_urls

tools_router = APIRouter()

@tools_router.get("/xhs/img")
async def get_xhs_img_urls_api(content):
    return {"code":200,"msg":"success","data":get_xhs_img_urls(content)}