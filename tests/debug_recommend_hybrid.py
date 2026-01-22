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

from src.core.alpha_predator import AlphaPredator
from src.data.sources.factory import get_data_source
from loguru import logger

async def test_hybrid_recommend():
    print("Initializing AlphaPredator...")
    predator = AlphaPredator()
    ds = get_data_source()
    
    print(f"\n--- DataSource Status ---")
    print(f"Primary Source: {ds.source_name}")
    print(f"Is Tushare: {ds.is_tushare}")
    
    print("\n--- Testing recommend_stocks with hybrid logic ---")
    # Simulation: We'll override the LLM to avoid real API costs/delays and focused on data collection log
    # But AlphaPredator logs "采集股票数据失败" if internal steps fail, so we watch logs.
    
    target_sectors = ["证券", "银行"]
    
    print(f"Requesting sectors: {target_sectors}")
    
    try:
        # We can't easily intercept local variables inside the function without modifying it or using a debugger.
        # However, we can run it and check if it produces a valid result key or errors out.
        # Real LLM call might fail if not configured, but data collection happens before LLM.
        
        # We'll rely on the logger messages printed to stdout to verify data collection.
        # "获取板块资金流向..." "获取概念板块..." etc are logged in analyze_sectors
        # recommend_stocks doesn't log much data details unless we added them.
        # I added "AkShare 客户端初始化失败" log in the fix. If we see standard logs, it's good.
        
        # Let's invoke analyze_sectors first as it was also modified
        print("\n[1] Running analyze_sectors()...")
        sector_result = await predator.analyze_sectors()
        print("Analyze Sectors Result Keys:", sector_result.keys())
        
        if "error" in sector_result:
             print("Analyze Sectors Error:", sector_result.get("error"))
        
        # Now recommend stocks
        print("\n[2] Running recommend_stocks()...")
        rec_result = await predator.recommend_stocks(target_sectors)
        print("Recommend Stocks Result Keys:", rec_result.keys())
        
        if "error" in rec_result:
             print("Recommend Stocks Error:", rec_result.get("error"))
             
    except Exception as e:
        print(f"FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_hybrid_recommend())
