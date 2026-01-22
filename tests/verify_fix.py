
import os
import sys
import logging
import pandas as pd
from unittest.mock import MagicMock

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add project root to path
sys.path.append(os.getcwd())

# Mock settings and tushare
sys.modules['src.config'] = MagicMock()
sys.modules['tushare'] = MagicMock()

# Import the client 
from src.data.sources.tushare_client import TushareClient

def test_fix():
    # Mock tushare pro api
    mock_ts = sys.modules['tushare']
    mock_pro = MagicMock()
    mock_ts.pro_api.return_value = mock_pro
    mock_ts.set_token = MagicMock()
    
    # Mock config settings
    mock_settings = sys.modules['src.config'].get_settings.return_value
    mock_settings.tushare.token.get_secret_value.return_value = "dummy_token"
    
    client = TushareClient(token="dummy_token")
    
    # Test get_moneyflow_hsgt with None args
    logger.info("Testing get_moneyflow_hsgt(trade_date=None)...")
    try:
        # Mock return value
        mock_pro.moneyflow_hsgt.return_value = pd.DataFrame()
        
        client.get_moneyflow_hsgt(trade_date=None)
        
        # Verify call args
        call_args = mock_pro.moneyflow_hsgt.call_args[1]
        logger.info(f"Call args: {call_args}")
        
        if 'trade_date' in call_args and call_args['trade_date'] is None:
             logger.error("FAIL: trade_date=None was passed to API")
        elif 'start_date' in call_args and call_args['start_date'] is None:
             logger.error("FAIL: start_date=None was passed to API")
        elif 'end_date' in call_args and call_args['end_date'] is None:
             logger.error("FAIL: end_date=None was passed to API")
        else:
             logger.info("SUCCESS: None arguments were filtered out")
             
    except Exception as e:
        logger.error(f"Error during test: {e}")

if __name__ == "__main__":
    test_fix()
