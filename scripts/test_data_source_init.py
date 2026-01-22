import sys
import os
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))
#
# test_data_source_init.py 这是测试factory.py的初始化函数
#
from loguru import logger
from src.data.sources.factory import UnifiedDataSource, get_data_source

def test_init_data_source():
    logger.info("Starting test for _init_data_source...")

    # Method 1: Direct Instantiation
    logger.info("--- Testing Direct Instantiation ---")
    try:
        ds = UnifiedDataSource()
        logger.info(f"Successfully initialized UnifiedDataSource.")
        logger.info(f"Source Name: {ds.source_name}")
        logger.info(f"Is Tushare: {ds.is_tushare}")
        logger.info(f"Is AkShare: {ds.is_akshare}")
        
    except Exception as e:
        logger.error(f"Failed to instantiate UnifiedDataSource: {e}")

    # Method 2: Singleton Access
    logger.info("\n--- Testing Singleton Access (get_data_source) ---")
    
    # Debug: Check environment variable and Settings
    import os
    from dotenv import load_dotenv
    from src.config import get_settings
    
    # Force load .env
    load_dotenv()
    
    token_env = os.environ.get("TUSHARE_TOKEN")
    logger.info(f"DEBUG: os.environ['TUSHARE_TOKEN'] = {token_env[:4] + '****' if token_env else 'None'}")
    
    settings = get_settings()
    logger.info(f"DEBUG: settings.tushare.token = {settings.tushare.token.get_secret_value()[:4] + '****' if settings.tushare.token.get_secret_value() else 'Empty'}")

    try:
        ds_singleton = get_data_source()
        logger.info(f"Singleton instance retrieved.")
        logger.info(f"Singleton Source Name: {ds_singleton.source_name}")
        
        # Verify it's the same logic
        assert ds_singleton.source_name in ["Tushare", "AkShare"]
        
    except Exception as e:
        logger.error(f"Failed to get singleton data source: {e}")

if __name__ == "__main__":
    test_init_data_source()
