import sys
import os
import pandas as pd
from loguru import logger

# Ensure src can be imported
sys.path.append(os.getcwd())

from src.data.sources.factory import UnifiedDataSource
from src.data.sources.ths_client import THSClient

def test_sector_logic():
    # Mock selected sectors
    selected_sectors = ["酿酒行业", "银行"]
    
    # 1. Init Data Source (forces Tushare if configured, or we can force it manually)
    logger.info("Initializing Data Source...")
    ds = UnifiedDataSource()
    
    # Force Tushare mode for this test logic simulation
    # (Assuming ds is in Tushare mode or we reproduce the logic block directly)
    
    logger.info("Getting stock list from Tushare...")
    try:
        df_all = ds.get_stock_list()
        logger.info(f"Stock list size: {len(df_all)}")
    except Exception as e:
        logger.error(f"Failed to get stock list: {e}")
        df_all = pd.DataFrame()

    # 2. Simulate the loop in recommend_stocks
    sector_stocks = []
    
    # Try to init ths explicitly for fallback testing
    try:
        ths = THSClient()
    except:
        ths = None

    for sector in selected_sectors:
        logger.info(f"Processing sector: {sector}")
        try:
            matched = pd.DataFrame()
            if not df_all.empty and 'industry' in df_all.columns:
                matched = df_all[df_all['industry'].str.contains(sector, na=False)]
            
            if not matched.empty:
                logger.info(f"Found in Tushare: {len(matched)}")
                # Normalization
                matched = matched.rename(columns={
                    'ts_code': '代码',
                    'name': '名称',
                    'industry': '行业'
                })
                subset = matched.head(10)
                for _, row in subset.iterrows():
                    code = row['代码']
                    sector_stocks.append(row.to_dict())
            else:
                logger.info(f"Not found in Tushare, trying AkShare fallback for {sector}")
                if ths:
                    # This is likely where the error is if AkShare is used
                    logger.info("Calling ak.stock_board_industry_cons_em...")
                    cons = ths.ak.stock_board_industry_cons_em(symbol=sector)
                    logger.info(f"AkShare returned: {len(cons) if cons is not None else 'None'}")
                    if cons is not None and not cons.empty:
                        sector_stocks.extend(cons.head(10).to_dict('records'))
                    
        except Exception as e:
            logger.error(f"Error processing sector {sector}: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_sector_logic()
