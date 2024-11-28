from starlette.middleware.cors import CORSMiddleware
import json
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import os

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 定义评分数据模型
class Score(BaseModel):
    quadrantX: str
    quadrantY: str
    coordinates: dict


class Submission(BaseModel):
    name: str
    score: Score


# 读取历史记录和提交记录
def load_data(filename: str):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


# 保存数据到文件
def save_data(filename: str, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def load_history_data():
    with open("history.json", "r", encoding="utf-8") as f:
        return json.load(f)

def load_submission_data():
    with open("submission.json", "r", encoding="utf-8") as f:
        return json.load(f)


@app.post("/api/score")
async def receive_score(submission: Submission):
    history_data=load_history_data()
    # 将新的提交记录添加到 history.json
    history_data.append(submission.dict())
    save_data("history.json", history_data)

    submission_data = load_submission_data()
    # 更新 submission.json 中的用户平均评分
    user_scores = [s['score']['coordinates'] for s in history_data if s['name'] == submission.name]

    if user_scores:
        avg_x = sum(score['x'] for score in user_scores) / len(user_scores)
        avg_y = sum(score['y'] for score in user_scores) / len(user_scores)
    else:
        avg_x, avg_y = 0, 0

    # 更新 submission.json 中的平均值
    user_submission = next((s for s in submission_data if s['name'] == submission.name), None)
    if user_submission:
        user_submission['average_x'] = avg_x
        user_submission['average_y'] = avg_y
    else:
        submission_data.append({
            "name": submission.name,
            "average_x": avg_x,
            "average_y": avg_y
        })

    save_data("submission.json", submission_data)

    # 返回提交结果和用户的平均评分
    return {
        "message": "Score received successfully",
        "average": {
            "x": avg_x,
            "y": avg_y
        }
    }


# 获取所有历史评分记录
@app.get("/api/history")
async def get_history():
    history_data=load_history_data()

    return {"code":200, "data":history_data}


# 获取所有用户的平均评分
@app.get("/api/submissions")
async def get_submissions():
    submission_data = load_submission_data()
    return {"code":200, "data":submission_data}
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app='main:app', host='0.0.0.0', port=8080, workers=3, reload=True)
