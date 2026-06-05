import logging
import time
from apscheduler.schedulers.blocking import BlockingScheduler
from ingestion.fetch import fetch_all
from ingestion.parse import parse_all
from ingest import ingest_data

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("DailyScheduler")

def run_ingestion_job():
    """
    Full daily pipeline: fetch fresh HTML → parse live data → embed into ChromaDB.
    This ensures NAV, AUM, returns, and all fund details are always up-to-date.
    """
    logger.info("Starting automated daily ingestion pipeline.")

    # Simple retry mechanism (1 retry)
    max_retries = 1
    for attempt in range(max_retries + 1):
        try:
            logger.info(f"Attempt {attempt + 1}: Step 1/3 — Fetching fresh HTML from Groww...")
            fetch_all()
            logger.info("Step 1/3 complete: HTML fetched.")

            logger.info("Step 2/3 — Parsing HTML to extract live NAV, AUM, returns...")
            parse_all()
            logger.info("Step 2/3 complete: Data parsed.")

            logger.info("Step 3/3 — Embedding chunks into ChromaDB...")
            result = ingest_data()

            if result and result.get("status") == "success":
                logger.info(
                    f"Pipeline complete! "
                    f"Files processed: {result.get('urls_fetched', 0)}, "
                    f"Chunks embedded: {result.get('chunks_generated', 0)}"
                )
            else:
                logger.warning("Pipeline completed but returned no metrics.")

            break  # Success — exit retry loop

        except Exception as e:
            logger.error(f"Ingestion job failed on attempt {attempt + 1}: {e}", exc_info=True)
            if attempt < max_retries:
                logger.info("Retrying in 10 seconds...")
                time.sleep(10)
            else:
                logger.error("Max retries reached. Manual intervention may be needed.")

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

    logger.info("Scheduler started. Full pipeline (fetch→parse→ingest) will run daily at 10:00 AM IST.")

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler shutting down gracefully.")
