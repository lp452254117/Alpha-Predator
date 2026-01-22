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

async def test_recommend_logic():
    print("Initializing AlphaPredator...")
    predator = AlphaPredator()
    ds = get_data_source()
    
    print(f"\n--- DataSource Status ---")
    print(f"Primary Source: {ds.source_name}")
    print(f"Is Tushare: {ds.is_tushare}")
    print(f"Is AkShare: {ds.is_akshare}")
    
    # Check logic in recommend_stocks
    print("\n--- Simulating recommend_stocks logic ---")
    if ds.is_akshare:
        print("Logic path: AkShare (Correct for recommendation data)")
    else:
        print("Logic path: Tushare (Likely missing data collection implementation)")
        
    # Simulate the code block in recommend_stocks
    stock_quotes = "暂无数据"
    if ds.is_akshare:
       print("Would fetch data via AkShare...")
    elif ds.is_tushare:
        print("Current code only checks 'if self.data_source.is_akshare:' for data collection!")
        print("If source is Tushare, it skips fetching specific recommendation data.")

if __name__ == "__main__":
    asyncio.run(test_recommend_logic())
