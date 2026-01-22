import sys
import os
import requests
from loguru import logger

# Ensure src can be imported
sys.path.append(os.getcwd())

from src.data.sources.tushare_client import TushareClient

def debug_proxy():
    # 1. Init tushare
    client = TushareClient()
    
    # Check effective proxies
    logger.info(f"System proxies: {requests.utils.getproxies()}")
    
    url = "https://emappdata.eastmoney.com/stockrank/getAllCurrentList"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    # 2. Try with NO_PROXY set
    try:
        logger.info(f"Requests getting {url} with headers...")
        resp = requests.get(url, headers=headers, timeout=5)
        logger.info(f"Response: {resp.status_code}")
    except Exception as e:
        logger.error(f"Request failed: {e}")

    # 3. Clear env vars and try again
    logger.info("Clearing HTTP_PROXY/HTTPS_PROXY...")
    os.environ.pop("HTTP_PROXY", None)
    os.environ.pop("HTTPS_PROXY", None)
    
    # Check effective proxies again
    logger.info(f"System proxies after clear: {requests.utils.getproxies()}")

    try:
        logger.info(f"Retry requests getting {url} with headers...")
        resp = requests.get(url, headers=headers, timeout=5)
        logger.info(f"Response: {resp.status_code}")
    except Exception as e:
        logger.error(f"Retry failed: {e}")

if __name__ == "__main__":
    debug_proxy()
