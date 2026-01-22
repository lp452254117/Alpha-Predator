import sys
import os
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from src.data.sources.factory import UnifiedDataSource
from loguru import logger

def test_factory_normalization():
    print("Initializing UnifiedDataSource...")
    ds = UnifiedDataSource()
    
    # Check if Tushare is initialized
    print(f"Current source: {ds.source_name}")
    
    if not ds.is_tushare:
        print("WARNING: Tushare not initialized. Verification might be limited.")
    
    # Test Normalization
    print("\n--- Testing normalization logic ---")
    
    cases = [
        ("601688", "601688.SH"),
        ("000001", "000001.SZ"),
        ("688001", "688001.SH"),
        ("300001", "300001.SZ"),
        ("601688.SH", "601688.SH"), # Idempotency
        ("123", "123") # Fallback
    ]
    
    for input_code, expected in cases:
        actual = ds.normalize_code(input_code)
        status = "PASS" if actual == expected else "FAIL"
        print(f"Input: {input_code}, Expected: {expected}, Actual: {actual} [{status}]")

    # Test get_stock_info with raw code
    target_raw = "601688"
    print(f"\n--- Testing get_stock_info('{target_raw}') ---")
    info = ds.get_stock_info(target_raw)
    print(f"Info: {info}")
    
    if info.get('ts_code') == "601688.SH":
        print("PASS: Returned ts_code is normalized.")
    else:
        print(f"FAIL: returned ts_code is {info.get('ts_code')}")

    if info.get('name') != '未知':
        print(f"PASS: Stock name found: {info.get('name')}")
    else:
        print("FAIL: Stock name is unknown (fetch failed)")

    # Test get_daily_data with raw code (small range)
    print(f"\n--- Testing get_daily_data('{target_raw}') ---")
    try:
        df = ds.get_daily_data(target_raw, start_date='20240101', end_date='20240105')
        print(f"Records found: {len(df)}")
        if not df.empty:
            print(df.head(1).to_string())
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_factory_normalization()
