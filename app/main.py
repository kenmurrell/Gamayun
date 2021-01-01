import json
import os
from typing import List, Dict
import regex as re
from fastapi import FastAPI, status, HTTPException
from fastapi.responses import JSONResponse
from worker import celery

app = FastAPI()

ACTIVATED_LANGUAGES = {"az", "be", "da", "de", "en", "es", "fi", "fr", "hu", "it", "nl", "no", "pl", "pt", "ro", "ru", "sv", "tr", "uk"}
REPO_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def load_models() -> List[Dict]:
    models_list = list()
    file_pattern = re.compile(r"^([a-z]{2})(\.json)$")
    models_dir = os.path.join(REPO_DIR, "../models")
    models_dir_list = os.listdir(models_dir)
    for model_file in models_dir_list:
        model_path = os.path.join(models_dir, model_file)
        if not os.path.isfile(model_path):
            continue
        re_match = file_pattern.search(model_file)
        if not re_match or re_match.group(1) not in ACTIVATED_LANGUAGES:
            continue
        with open(model_path, "r", encoding="utf-8") as file_object:
            model = json.load(file_object)
            models_list.append(model)
            print("...Loaded {} model".format(model["name"]))
    return models_list


models = load_models()


@app.get("/detect/{text}")
async def detect(text: str):
    if len(text) > 200:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Input text must be under 200 characters ")
    task = celery.send_task("detect.task", args=[text, models])
    r_dict = {"task_id": task.id, "url": "http://localhost:5000/check/{}".format(task.id)}
    return JSONResponse(status_code=status.HTTP_200_OK, content=r_dict)


@app.get("/check/{id}")
async def check(id: str):
    task = celery.AsyncResult(id)
    if task.state == 'SUCCESS':
        response = {
            'status': task.state,
            'result': task.result,
            'task_id': id
        }
    else:
        response = {
            'status': task.state,
            'result': task.info,
            'task_id': id
        }
    return response
