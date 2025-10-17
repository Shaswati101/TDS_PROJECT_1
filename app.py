import os
import uuid
from fastapi import FastAPI, Request, BackgroundTasks, HTTPException, status
from typing import Dict
from dotenv import load_dotenv

from orchestration.workflow import create_project_workflow, update_project_workflow

load_dotenv()
app = FastAPI()
task_store: Dict = {}

SECRET = os.getenv("SECRET")

@app.get("/", tags=["test"])
def read_root():
    return {"status": "Service is running"}

def verify_secret(s):
    return s == SECRET

@app.post("/create-project", status_code=status.HTTP_202_ACCEPTED, tags=["Project Creation"])
async def create_project(request: Request, background_tasks: BackgroundTasks):

    req = await request.json()

    if not verify_secret(req.get("secret")):
        raise HTTPException(status_code=403, detail="invalid secret")

    task_id = str(uuid.uuid4())
    task_store[task_id] = {"status": "PENDING", "details": "Task has been queued."}
    eval_body = {
                    "email":req.get("email"),
                    "task":req.get("task"),
                    "round":req.get("round"),
                    "nonce":req.get("nonce"),}

    response = {}
    if req.get("round") == 1:
        background_tasks.add_task(create_project_workflow,
                                  task_id=task_id,
                                  task_store=task_store,
                                  repo_name=os.getenv("REPO_NAME"),
                                  code_prompt=req.get("brief"),
                                  attachments=req.get("attachments",[]),
                                  checks=req.get("checks",[]),
                                  eval_url = req.get("evaluation_url"),
                                  eval_body=eval_body)
        response = { "message" : "Project creation has been initiated.", "task_id" : task_id, "status_url" : f"/tasks/{task_id}/status"}
    elif req.get("round") > 1:
        background_tasks.add_task(update_project_workflow,
                                  task_id=task_id,
                                  task_store=task_store,
                                  repo_name=os.getenv("REPO_NAME"),
                                  code_prompt=req.get("brief"),
                                  attachments=req.get("attachments",[]),
                                  checks=req.get("checks",[]),
                                  eval_url = req.get("evaluation_url"),
                                  eval_body =eval_body )

        response = {"message": "Project update has been initiated.", "task_id": task_id, "status_url": f"/tasks/{task_id}/status"}

    return response


@app.get("/tasks/{task_id}/status", tags=["task status"])
async def get_task_status(task_id: str):
    task = task_store.get(task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return {"task_id" : task_id, **task}


@app.post("/evaluate", tags=["evaluate"])
async def evaluate(request: Request):
    req = await request.json()
    print(req)
