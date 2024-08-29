from fastapi import FastAPI, UploadFile, File, Response
import uuid
from config import db,redis_queue
from utils.validatecsv import validate_csv
from worker.csv_worker import process_csv

app = FastAPI()
db = db.connect_db()
queue = redis_queue.get_queue()

@app.post("/api/upload")
async def upload_csv(res: Response, file: UploadFile = File(...)):
    try:
        csv_stat = await validate_csv(file)        
        request_id = str(uuid.uuid4())
        job = queue.enqueue(process_csv,file,request_id)
        
    except Exception:
        pass

