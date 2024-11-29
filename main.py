from starlette.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from app import router
from tools.tools_app import tools_router

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(tools_router)
