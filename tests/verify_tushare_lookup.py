import sys
import os
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from src.data.sources.factory import UnifiedDataSource, get_data_source
from loguru import logger

# Setup minimal logging
logger.remove()
logger.add(sys.stderr, level="INFO")

def verify_optimization():
    print("Initializing UnifiedDataSource...")
    # This will initialize TushareClient if token is present
    ds = get_data_source()
    
    if not ds.is_tushare:
        print("Warning: Current data source is not Tushare. Verification might be less meaningful.")
        print(f"Current source: {ds.source_name}")
    
    target_code = "000001.SZ"
    print(f"Fetching info for {target_code}...")
    
    info = ds.get_stock_info(target_code)
    
    print("\nResult:")
    print(info)
    
    if info.get('ts_code') == target_code and info.get('name'):
        print("\nSUCCESS: Retrieved stock info correctly.")
    else:
        print("\nFAILURE: Failed to retrieve correct info.")

if __name__ == "__main__":
    verify_optimization()
