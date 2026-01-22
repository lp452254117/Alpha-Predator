import sys
import os
from pathlib import Path
import tushare as ts
import pandas as pd

# Add project root to sys.path to import config
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from src.config import get_settings

def run_with_timeout(func, args=(), kwargs=None, timeout=10):
    if kwargs is None:
        kwargs = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(func, *args, **kwargs)
        try:
            return future.result(timeout=timeout)
        except concurrent.futures.TimeoutError:
            print(f"TIMEOUT: Call to {func.__name__} timed out after {timeout}s")
            return None
        except Exception as e:
            print(f"ERROR: Call to {func.__name__} failed: {e}")
            return None

def debug_tushare():
    try:
        settings = get_settings()
        token = settings.tushare.token.get_secret_value()
        
        print(f"Token found: {token[:6]}...{token[-4:]}")
        
        # Configure Proxy if needed
        proxy_url = "http://user:liuhkcxjvasrdg@8.140.4.230:8888"
        os.environ["HTTP_PROXY"] = proxy_url
        os.environ["HTTPS_PROXY"] = proxy_url
        print(f"Proxy set to: {proxy_url}")

        ts.set_token(token)
        pro = ts.pro_api()
        
        target_code_raw = "601688"
        target_code_suffix = "601688.SH"
        
        # Test 1: Stock Basic
        print(f"\n--- Testing stock_basic for {target_code_raw} ---")
        df_raw = run_with_timeout(pro.stock_basic, kwargs={'ts_code': target_code_raw}, timeout=10)
        if df_raw is not None:
            print(f"Result count: {len(df_raw)}")
            if not df_raw.empty:
                print(df_raw.head())
        
        print(f"\n--- Testing stock_basic for {target_code_suffix} ---")
        df_suffix = run_with_timeout(pro.stock_basic, kwargs={'ts_code': target_code_suffix}, timeout=10)
        if df_suffix is not None:
            print(f"Result count: {len(df_suffix)}")
            if not df_suffix.empty:
                print(df_suffix.head())

        # Test 2: Daily Data
        print(f"\n--- Testing daily for {target_code_raw} (20240101-20240110) ---")
        df_daily_raw = run_with_timeout(pro.daily, kwargs={'ts_code': target_code_raw, 'start_date': '20240101', 'end_date': '20240110'}, timeout=15)
        if df_daily_raw is not None:
             print(f"Result count: {len(df_daily_raw)}")

        print(f"\n--- Testing daily for {target_code_suffix} (20240101-20240110) ---")
        df_daily_suffix = run_with_timeout(pro.daily, kwargs={'ts_code': target_code_suffix, 'start_date': '20240101', 'end_date': '20240110'}, timeout=15)
        if df_daily_suffix is not None:
             print(f"Result count: {len(df_daily_suffix)}")
             
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import concurrent.futures
    debug_tushare()
