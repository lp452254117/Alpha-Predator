import socket
import sys
import os
import requests
import ssl
from urllib.parse import urlparse
from loguru import logger

# Clear env proxies for the "Direct" test phase
def clear_proxy_env():
    for key in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 'NO_PROXY', 'no_proxy']:
        if key in os.environ:
            del os.environ[key]

def get_proxy_env():
    return {k: os.environ.get(k) for k in ['HTTP_PROXY', 'HTTPS_PROXY', 'NO_PROXY'] if k in os.environ}

def test_dns(domain):
    try:
        ip = socket.gethostbyname(domain)
        logger.info(f"✅ DNS Resolution for {domain}: {ip}")
        return ip
    except Exception as e:
        logger.error(f"❌ DNS Resolution Failed for {domain}: {e}")
        return None

def test_tcp_connect(ip, port=443):
    if not ip: return False
    try:
        sock = socket.create_connection((ip, port), timeout=5)
        sock.close()
        logger.info(f"✅ TCP Connect to {ip}:{port} Success")
        return True
    except Exception as e:
        logger.error(f"❌ TCP Connect to {ip}:{port} Failed: {e}")
        return False

def test_http_request(url, proxy_config=None, name="Direct"):
    logger.info(f"--- Testing HTTP Request ({name}) to {url} ---")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    proxies = proxy_config if proxy_config else {}
    
    try:
        resp = requests.get(url, headers=headers, proxies=proxies, timeout=10, verify=False) # Skip SSL verify to see if it's just cert issue
        logger.info(f"✅ HTTP {resp.status_code} (Size: {len(resp.content)})")
        return True
    except Exception as e:
        logger.error(f"❌ HTTP Request Failed: {e}")
        return False

def diagnose():
    target_domain = "emappdata.eastmoney.com"
    target_url = "https://emappdata.eastmoney.com/stockrank/getAllCurrentList"
    
    # 1. Baseline: Local Network Check (Direct)
    logger.info("=== Phase 1: Direct Connection (No Proxy) ===")
    clear_proxy_env()
    
    test_dns("www.baidu.com")
    ip = test_dns(target_domain)
    
    if ip:
        test_tcp_connect(ip, 443)
    
    test_http_request(target_url, name="Direct")

    # 2. Proxy Check
    logger.info("\n=== Phase 2: Using Tushare Proxy ===")
    proxy_url = "http://user:liuhkcxjvasrdg@8.140.4.230:8888"
    proxies = {"http": proxy_url, "https": proxy_url}
    
    test_http_request(target_url, proxy_config=proxies, name="With Proxy")
    
    # 3. NO_PROXY Simulation
    logger.info("\n=== Phase 3: NO_PROXY Simulation (Requests Lib) ===")
    # requests library respects NO_PROXY if set in env, let's test if it works with logic
    # But essentially it's the same as Phase 1 if requests logic works. 
    # Let's just confirm if the user's manual NO_PROXY string is valid
    
    no_proxy_str = "eastmoney.com,.eastmoney.com,sina.com.cn,.sina.com.cn,sinajs.cn,.sinajs.cn,127.0.0.1,localhost"
    os.environ["HTTP_PROXY"] = proxy_url
    os.environ["HTTPS_PROXY"] = proxy_url
    os.environ["NO_PROXY"] = no_proxy_str
    
    logger.info(f"Env setup: {get_proxy_env()}")
    # Using 'trust_env=True' (default) to pick up env vars
    try:
        resp = requests.get(target_url, timeout=10, verify=False)
        logger.info(f"✅ HTTP with NO_PROXY env: {resp.status_code}")
    except Exception as e:
        logger.error(f"❌ HTTP with NO_PROXY env Failed: {e}")

if __name__ == "__main__":
    diagnose()
