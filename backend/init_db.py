"""Initialize database tables if they don't exist"""
import sys
from pathlib import Path
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.db.base import engine, Base
from app.db.models import Session, LLMEvent
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db(max_retries=5):
    """Create all tables if they don't exist"""
    for attempt in range(max_retries):
        try:
            logger.info(f"Creating database tables... (attempt {attempt + 1}/{max_retries})")
            Base.metadata.create_all(bind=engine)
            logger.info("✅ Database tables created successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Error creating tables: {str(e)}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in 2 seconds...")
                time.sleep(2)
            else:
                logger.error("⚠️  Max retries reached. Skipping database initialization.")
                logger.error("   The app will start but database operations may fail.")
                return False

if __name__ == "__main__":
    init_db()
