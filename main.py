import asyncio
from fastapi import FastAPI, UploadFile, File, HTTPException,BackgroundTasks
from fastapi.responses import JSONResponse
import uuid
from config import redis_queue
from utils.validatecsv import validate_csv
from worker.csv_worker import process_csv
from repository.db_ops import db_ops
from My_Exception.custom_exception import CustomException
from My_models.job_status import JobStatus

app = FastAPI()
queue = redis_queue.get_queue()

@app.post("/api/upload")
async def upload_csv(background_tasks: BackgroundTasks,file: UploadFile = File(...)):
    try:
        csv_stat = await validate_csv(file)        
        request_id = str(uuid.uuid4())

        await db_ops.insert_job({
            "requestId": request_id,
            "status": "pending",
            "output_url": ""
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
    job = await db_ops.jobs.find_one({"requestId": request_id})
    if job:
        return JobStatus(
            requestId=job["requestId"],
            status=job["status"],
            processed=job["processed"],
            total=job["total"]
        )
    return JSONResponse(content={"error": "Job not found"}, status_code=404)

