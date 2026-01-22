import sys
import os
from loguru import logger

# Ensure src can be imported
sys.path.append(os.getcwd())

from src.data.sources.factory import UnifiedDataSource, get_data_source

def test_fix_verification():
    try:
        # Get the unified data source (which wraps TushareClient)
        ds = UnifiedDataSource() 
        
        # Ensure we are using Tushare
        if not ds.is_tushare:
            logger.warning("Not using Tushare source, skipping measurement. (Is TUSHARE_TOKEN set?)")
            return

        logger.info("Testing get_north_flow(trade_date=None)...")
        
        # This calls TushareClient.get_moneyflow_hsgt internally
        # Before fix: it would pass None and fail
        # After fix: it should calculate 30 days window and pass start_date/end_date
        result = ds.get_north_flow(trade_date=None)
        
        logger.info(f"Result: {result}")
        
        if result and ('north_money' in result or 'south_money' in result):
            logger.info("SUCCESS: get_north_flow returned valid data")
        else:
            logger.warning("WARNING: get_north_flow returned empty dict (might be no data, but no error is good)")
            
    except Exception as e:
        logger.error(f"FAIL: Caught unexpected error: {e}")
        raise

if __name__ == "__main__":
    test_fix_verification()
