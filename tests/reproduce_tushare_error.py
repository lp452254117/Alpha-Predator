
import os
import sys
from loguru import logger
import tushare as ts
from src.config import get_settings

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

    logger.info("Testing moneyflow_hsgt with all None...")
    try:
        df = pro.moneyflow_hsgt(trade_date=None, start_date=None, end_date=None)
        logger.info(f"Success with all None: {len(df)} records")
    except Exception as e:
        logger.error(f"Failed with all None: {e}")

    logger.info("Testing moneyflow_hsgt with None trade_date but explicit None...")
    try:
        # Checking if explicitly passing None is the issue vs missing argument
        df = pro.moneyflow_hsgt(trade_date="")
        logger.info(f"Success with empty string: {len(df)} records")
    except Exception as e:
        logger.error(f"Failed with empty string: {e}")

if __name__ == "__main__":
    test_tushare_moneyflow()
