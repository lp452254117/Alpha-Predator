
import os
import sys
import logging
import tushare as ts
from src.config import get_settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add project root to path
sys.path.append(os.getcwd())

def test_tushare_moneyflow():
    settings = get_settings()
    token = settings.tushare.token.get_secret_value()
    
    if not token:
        logger.error("No Tushare token found")
        return

    ts.set_token(token)
    pro = ts.pro_api()

    logger.info("Testing moneyflow_hsgt with explicit None for trade_date...")
    try:
        # This matches what happens when get_north_flow() is called without args
        df = pro.moneyflow_hsgt(trade_date=None, start_date=None, end_date=None)
        logger.info(f"Success with all None: {len(df)} records")
    except Exception as e:
        logger.error(f"Failed with all None: {e}")

    logger.info("Testing moneyflow_hsgt by OMITTING arguments...")
    try:
        # This is what we SHOULD do if args are None
        df = pro.moneyflow_hsgt()
        logger.info(f"Success with omitted args: {len(df)} records")
    except Exception as e:
        logger.error(f"Failed with omitted args: {e}")

if __name__ == "__main__":
    test_tushare_moneyflow()
