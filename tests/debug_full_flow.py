import sys
import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Add project root to sys.path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

# Explicitly load .env
load_dotenv(project_root / ".env")

from src.core.deep_dive import DeepDiveDiagnostic
from loguru import logger

async def test_full_flow():
    print("Initializing DeepDiveDiagnostic...")
    diagnostic = DeepDiveDiagnostic()
    
    target_code = "601688" # Raw code without suffix
    print(f"\n--- Testing diagnose('{target_code}') ---")
    
    try:
        # 1. Quick Scan
        print("Running quick_scan...")
        scan_result = await diagnostic.quick_scan(target_code)
        print(f"Quick Scan Result: {scan_result['ts_code']} - {scan_result['name']}")
        
        # 2. Full Diagnose
        print("\nRunning diagnose (mocking LLM)...")
        # Initialize components but verify data fetching mainly
        # We can't easily mock LLM here without more code, but we can check if it fails at data fetching
        
        # We'll call get_stock_info and collect_stock_data directly to verify internal steps of diagnose
        stock_info = await diagnostic.get_stock_info(target_code)
        print(f"Stock Info: {stock_info}")
        
        if stock_info:
            data = await diagnostic.collect_stock_data(target_code)
            print(f"Daily Data records: {len(data.get('daily')) if data.get('daily') is not None else 0}")
            print(f"Basic Data found: {data.get('daily_basic') is not None}")
        else:
            print("Stock Info failed!")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_full_flow())
