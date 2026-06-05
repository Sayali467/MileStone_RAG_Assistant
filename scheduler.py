import logging
import time
from apscheduler.schedulers.blocking import BlockingScheduler
from ingest import ingest_data

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("DailyScheduler")

def run_ingestion_job():
    logger.info("Starting automated daily ingestion pipeline (Phase 3.6).")
    
    # Simple retry mechanism (1 retry)
    max_retries = 1
    for attempt in range(max_retries + 1):
        try:
            logger.info(f"Triggering ingestion entrypoint... (Attempt {attempt + 1})")
            
            # Phase 3: Fetch, parse, chunk, embed, upsert
            result = ingest_data()
            
            if result and result.get("status") == "success":
                logger.info(
                    f"Ingestion successful! "
                    f"URLs processed: {result.get('urls_fetched', 0)}, "
                    f"Chunks created: {result.get('chunks_generated', 0)}"
                )
            else:
                logger.warning("Ingestion completed but returned no metrics.")
            
            # Break out of the retry loop if successful
            break
            
        except Exception as e:
            logger.error(f"Ingestion job failed: {e}", exc_info=True)
            if attempt < max_retries:
                logger.info("Retrying in 10 seconds...")
                time.sleep(10)
            else:
                logger.error("Max retries reached. Alerting on failure.")

if __name__ == "__main__":
    scheduler = BlockingScheduler()
    
    # Scheduled to run every day at 10:00 AM IST
    scheduler.add_job(
        run_ingestion_job, 
        'cron', 
        hour=10, 
        minute=0, 
        timezone='Asia/Kolkata',
        id='daily_ingestion'
    )
    
    logger.info("Scheduler started. Ingestion will run daily at 10:00 AM IST.")
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler shutting down gracefully.")
