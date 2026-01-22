import sys
import os
from datetime import datetime, timedelta
from loguru import logger

# Ensure src can be imported
sys.path.append(os.getcwd())

from src.data.sources.tushare_client import TushareClient

def test_daily_basic_fix():
    client = TushareClient()
    ts_code = "002471.SZ"
    
    # Calculate range
    end_date = datetime.now().strftime("%Y%m%d")
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d") # 30 days lookback
    
    logger.info(f"Testing {ts_code} with range {start_date} - {end_date}...")
    
    # This calls the updated method signature
    df = client.get_daily_basic(ts_code=ts_code, start_date=start_date, end_date=end_date)
    
    logger.info(f"Result count: {len(df)}")
    
    if not df.empty:
        df_sorted = df.sort_values("trade_date", ascending=False)
        latest = df_sorted.iloc[0]
        logger.info(f"Latest record date: {latest['trade_date']}")
        logger.info(f"PE TTM: {latest.get('pe_ttm')}")
        logger.info("SUCCESS: Got data from range query")
    else:
        logger.warning("WARNING: No data found even with range query (market might be closed for a long time?)")

if __name__ == "__main__":
    test_daily_basic_fix()
