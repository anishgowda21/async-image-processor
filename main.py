from typing import List
from fastapi import FastAPI, UploadFile, File, HTTPException,BackgroundTasks,Form
from fastapi.responses import JSONResponse
import uuid
from utils.validatecsv import validate_csv
from worker.csv_worker import process_csv
from repository.db_ops import db_ops
from My_Exception.custom_exception import CustomException
from My_models.job_status import JobStatus

app = FastAPI()

@app.post("/api/upload")
async def upload_csv(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    webhook_urls: str = Form(default=[])
    ):
    try:
        csv_stat = await validate_csv(file)        
        request_id = str(uuid.uuid4())
        if webhook_urls:
            webhook_urls = webhook_urls.split(",")

        await db_ops.insert_job({
            "requestId": request_id,
            "status": "pending",
            "output_url": "",
            "webhook_urls": webhook_urls
        })

        background_tasks.add_task(process_csv,csv_stat,request_id)

        return JSONResponse(content={"requestId": request_id}, status_code=202)

    except CustomException as err:
        raise HTTPException(status_code=400, detail=str(err))
    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail="Something went wrong")

@app.get("/api/status/{request_id}")
async def get_status(request_id: str):
    job = await db_ops.get_job_status(request_id)
    if job:
        return JobStatus(
            requestId=job["requestId"],
            status=job["status"],
            output_url= job['output_url']
        )
    return JSONResponse(content={"error": "Job not found"}, status_code=404)


@app.post("/api/webhook/{request_id}")
async def add_webhook(request_id: str, webhook_url: str = Form(...)):
    job = await db_ops.get_job_status(request_id)
    if not job:
        return JSONResponse(content={"error": "Job not found"}, status_code=404)
    
    if job['status'] != 'pending':
        return JSONResponse(content={"error": "Cannot add webhook to a completed job"}, status_code=400)

    await db_ops.add_webhook(request_id, webhook_url)
    return JSONResponse(content={"message": "Webhook added successfully"}, status_code=200)


