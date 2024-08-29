from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import uuid
from config import redis_queue
from utils.validatecsv import validate_csv
from worker.csv_worker import process_csv
from repository.db_ops import db_ops
from My_Exception.custom_exception import CustomException

app = FastAPI()
queue = redis_queue.get_queue()

@app.post("/api/upload")
async def upload_csv(file: UploadFile = File(...)):
    try:
        csv_stat = await validate_csv(file)        
        request_id = str(uuid.uuid4())
        job = queue.enqueue(process_csv,csv_stat,request_id)

        await db_ops.insert_job({
            "requestId": request_id,
            "status": "pending",
            "jobId": job.id,
            "output_url": ""
        })

        return JSONResponse(content={"requestId": request_id}, status_code=202)

    except CustomException as err:
        raise HTTPException(status_code=400, detail=str(err))
    except Exception as err:
        raise HTTPException(status_code=500, detail="Something went wrong")

@app.get("/api/status/{request_id}")
async def get_status(request_id: str):
    status = await db_ops.get_job_status(request_id)
    if status is None:
        raise HTTPException(status_code=404, detail="Job not found.")
    
    return {"status": status}

