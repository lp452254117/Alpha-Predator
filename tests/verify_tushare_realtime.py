import sys
import os
from loguru import logger

# Ensure src can be imported
sys.path.append(os.getcwd())

from src.data.sources.factory import UnifiedDataSource

def test_tushare_realtime():
    ds = UnifiedDataSource()
    
    if not ds.is_tushare:
        logger.warning("Not in Tushare mode, cannot test Tushare Realtime Quote.")
        return

    ts_code = "000001.SZ" # Ping An Bank, should have data
    logger.info(f"Testing get_realtime_quote for {ts_code}...")
    
    quote = ds.get_realtime_quote(ts_code)
    
    logger.info(f"Quote: {quote}")
    
    if quote and quote.get("price", 0) > 0:
        logger.info(f"SUCCESS: Got realtime quote. Price: {quote['price']}")
        logger.info(f"Name: {quote.get('name')}")
        logger.info(f"Volume: {quote.get('volume')} (Lots if /100 matches logic)")
    else:
        logger.error("FAIL: Failed to get valid quote or price is 0")

if __name__ == "__main__":
    test_tushare_realtime()
