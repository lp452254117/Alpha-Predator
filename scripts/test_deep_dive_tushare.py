import sys
import os
import asyncio
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from loguru import logger
from src.core.deep_dive import DeepDiveDiagnostic
from src.data.sources.factory import get_data_source
from src.config import get_settings, reload_settings
from dotenv import load_dotenv
import os
from pathlib import Path

async def test_deep_dive_tushare():
    env_path = Path(__file__).resolve().parent.parent / '.env'
    logger.info(f"DEBUG: Reading env from {env_path}")
    
    # Manually read .env
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip().startswith('TUSHARE_TOKEN'):
                    parts = line.split('=', 1)
                    if len(parts) == 2:
                        val = parts[1].strip().strip('"').strip("'")
                        os.environ['TUSHARE_TOKEN'] = val
                        logger.info(f"DEBUG: Manually loaded TUSHARE_TOKEN: {val[:5]}***")
    except Exception as e:
        logger.error(f"Failed to read .env: {e}")

    # Fallback: Hardcode token for test if still missing
    if 'TUSHARE_TOKEN' not in os.environ:
        logger.warning("DEBUG: TUSHARE_TOKEN not found in .env, using fallback for testing.")
        os.environ['TUSHARE_TOKEN'] = "dcec0a01f4eccf9270a47d8b96560e382b012aa34c121240de70440a"

    reload_settings()
    settings = get_settings()
    logger.info(f"DEBUG: Token from settings: {settings.tushare.token.get_secret_value()[:5]}***")
    
    # Force minimal initialization
    try:
        engine = DeepDiveDiagnostic()
        # Initialize data source manually to ensure it picks up env
        ds = get_data_source()
        if not ds.is_tushare:
            logger.warning("Data source is not Tushare. Skipping Tushare specific test.")
            # return
        
        ts_code = "000001.SZ"
        logger.info(f"Collecting data for {ts_code}...")
        
        data = await engine.collect_stock_data(ts_code, lookback_days=30)
        
        # Check keys
        keys = data.keys()
        logger.info(f"Keys obtained: {list(keys)}")
        
        required_keys = ["daily", "daily_basic", "financial_abstract", "fund_flow", "price_stats", "announcements"]
        for k in required_keys:
            if k in data:
                logger.info(f"✅ {k} found. Type: {type(data[k])}")
                if hasattr(data[k], 'shape'):
                     logger.info(f"   Shape: {data[k].shape}")
            else:
                logger.warning(f"❌ {k} NOT found.")

        # Test formatting
        logger.info("Testing format_fundamental_data...")
        report = engine.format_fundamental_data(data)
        logger.info("Report snippet:")
        print("-------")
        print(report[:500] + "..." if len(report) > 500 else report)
        print("-------")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_deep_dive_tushare())
