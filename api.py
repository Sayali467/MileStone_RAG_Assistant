from fastapi import FastAPI, HTTPException, Header, BackgroundTasks
import os
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from query_engine import query_rag_engine
from apscheduler.schedulers.background import BackgroundScheduler
from scheduler import run_ingestion_job
import logging

app = FastAPI(title="Groww Genie API")

# Enable CORS for the Angular frontend
cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str
    citation: str
    citation_title: str
    last_updated: str
    is_refusal: bool

@app.post("/api/chat", response_model=QueryResponse)
def chat(request: QueryRequest):
    if not request.query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    try:
        res = query_rag_engine(request.query)
        return QueryResponse(
            answer=res["answer"],
            citation=res.get("citation_url", ""),
            citation_title=res.get("citation_title", "Source Factsheet"),
            last_updated=res.get("last_updated", ""),
            is_refusal=res.get("is_refusal", False)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
@app.get("/health")
def health_check():
    return {"status": "ok", "service": "Groww Genie API"}

@app.post("/api/admin/ingest")
def trigger_ingestion(background_tasks: BackgroundTasks, authorization: str = Header(None)):
    secret = os.getenv("ADMIN_SECRET_TOKEN")
    if not secret or authorization != f"Bearer {secret}":
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    background_tasks.add_task(run_ingestion_job)
    return {"status": "accepted", "message": "Ingestion job started in the background."}

@app.on_event("startup")
def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        run_ingestion_job, 
        'cron', 
        hour=10, 
        minute=0, 
        timezone='Asia/Kolkata',
        id='daily_ingestion'
    )
    scheduler.start()
    logging.info("BackgroundScheduler started for daily ingestion.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
