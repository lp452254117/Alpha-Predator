import sys
import os
import time
from loguru import logger

# Ensure src can be imported
sys.path.append(os.getcwd())

from src.data.sources.tushare_client import TushareClient
from src.data.sources.ths_client import THSClient

def test_proxy_fix():
    try:
        # 1. Initialize TushareClient to trigger environment variable setting (Proxy & NO_PROXY)
        logger.info("Initializing TushareClient...")
        ts_client = TushareClient()
        
        # Verify env vars
        logger.info(f"HTTP_PROXY: {os.environ.get('HTTP_PROXY')}")
        logger.info(f"NO_PROXY: {os.environ.get('NO_PROXY')}")
        
        # 2. Initialize THSClient and try to fetch data from EastMoney
        logger.info("Initializing THSClient and fetching hot stocks...")
        ths_client = THSClient()
        
        # This call was failing because of proxy
        df = ths_client.get_hot_stocks()
        
        if not df.empty:
            logger.info(f"SUCCESS: Fetched {len(df)} hot stocks from EastMoney.")
            logger.info(f"Top 3: \n{df.head(3)}")
        else:
            logger.warning("WARNING: Fetched empty DataFrame (might be valid depending on time, but connection likely worked)")

    except Exception as e:
        logger.error(f"FAIL: Connection failed: {e}")
        raise

if __name__ == "__main__":
    test_proxy_fix()
