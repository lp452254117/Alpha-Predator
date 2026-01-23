"""数据源工厂模块

提供统一的数据源访问接口，支持多数据源 fallback：
1. 优先使用 Tushare（需要 token）
2. 若 Tushare 不可用，自动 fallback 到 AkShare（免费）
"""

from typing import Optional, Protocol, runtime_checkable
from datetime import date

import pandas as pd
from loguru import logger


@runtime_checkable
class DataSourceProtocol(Protocol):
    """数据源协议，定义统一接口"""
    
    def get_daily_data(
        self,
        ts_code: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """获取日线数据"""
        ...
    
    def get_realtime_quote(self, ts_code: str) -> dict:
        """获取实时行情"""
        ...
    
    def get_stock_info(self, ts_code: str) -> dict:
        """获取股票基本信息"""
        ...
    
    def get_index_spot(self) -> pd.DataFrame:
        """获取指数实时行情"""
        ...
    
    def get_today_str(self) -> str:
        """获取今日日期字符串"""
        ...


class UnifiedDataSource:
    """统一数据源
    
    自动选择可用的数据源，优先 Tushare，fallback 到 AkShare。
    """
    
    def __init__(self):
        self._tushare = None
        self._akshare = None
        self._primary = None  # 当前使用的主数据源
        self._source_name = "unknown"
        
        self._init_data_source()
    
    def _init_data_source(self):
        """初始化数据源，尝试 Tushare，失败则使用 AkShare"""
        
        # 尝试初始化 Tushare
        try:
            from src.data.sources.tushare_client import TushareClient
            self._tushare = TushareClient()
            self._primary = self._tushare
            self._source_name = "Tushare"
            logger.info("数据源初始化成功: Tushare Pro")
            return
        except ValueError as e:
            logger.warning(f"Tushare 初始化失败: {e}")
        except Exception as e:
            logger.warning(f"Tushare 初始化异常: {e}")
        
        # Fallback 到 AkShare
        try:
            from src.data.sources.ths_client import THSClient
            self._akshare = THSClient()
            self._primary = self._akshare
            self._source_name = "AkShare"
            logger.info("数据源初始化成功: AkShare (免费)")
            return
        except Exception as e:
            logger.error(f"AkShare 初始化失败: {e}")
        
        raise RuntimeError("所有数据源初始化失败，无法继续运行")
    
    @property
    def source_name(self) -> str:
        """当前数据源名称"""
        return self._source_name
    
    @property
    def is_tushare(self) -> bool:
        """是否使用 Tushare"""
        return self._source_name == "Tushare"
    
    @property
    def is_akshare(self) -> bool:
        """是否使用 AkShare"""
        return self._source_name == "AkShare"
    
    def get_today_str(self) -> str:
        """获取今日日期字符串（YYYYMMDD）"""
        return date.today().strftime("%Y%m%d")
    
    def normalize_code(self, code: str) -> str:
        """标准化股票代码"""
        code = str(code).strip()
        if "." in code:
            return code
        
        # 常见规则
        if code.startswith(("60", "68")):
            return f"{code}.SH"
        elif code.startswith(("00", "30")):
            return f"{code}.SZ"
        elif code.startswith(("8", "4")):
            return f"{code}.BJ"
            
        return code

    def get_daily_data(
        self,
        ts_code: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """获取日线数据"""
        if self.is_tushare:
            ts_code = self.normalize_code(ts_code)
            return self._tushare.get_daily(
                ts_code=ts_code,
                start_date=start_date,
                end_date=end_date,
            )
        else:
            return self._akshare.get_daily_data(
                ts_code=ts_code,
                start_date=start_date,
                end_date=end_date,
            )
    
    def get_realtime_quote(self, ts_code: str) -> dict:
        """获取实时行情"""
        if self.is_akshare:
            return self._akshare.get_realtime_quote(ts_code)
        else:
            # Tushare 实时行情 via Sina
            try:
                df = self._tushare.get_realtime_quotes(ts_code)
                if df is not None and not df.empty:
                    row = df.iloc[0]
                    return {
                        "ts_code": ts_code,
                        "name": row.get("name", ""),
                        "price": float(row.get("price", 0)),
                        "change": 0.0, # Tushare legacy/sina might not return pct_chg directly, or calculated
                        # Sina keys: name, open, pre_close, price, high, low, bid, ask, vol, amount, ...
                        # Actually 'price' is current price.
                        # Calculate change if needed: (price - pre_close) / pre_close * 100
                        "volume": float(row.get("volume", 0)) / 100, # Sina volume is in shares, we might want lots or consistent. AkShare is usually lots? Check AkShare implementation. 
                        # AkShare stock_zh_a_spot_em volume is in 'hand' (100 shares)? No, usually shares or lots.
                        # Let's check AkShare implementation logic. 
                        # Wait, AkShare `stock_zh_a_spot_em` returns volume in '手' (lots)? Or shares?
                        # Sina returns shares. 
                        "amount": float(row.get("amount", 0)),
                        "high": float(row.get("high", 0)),
                        "low": float(row.get("low", 0)),
                        "open": float(row.get("open", 0)),
                        "pre_close": float(row.get("pre_close", 0)),
                    }
                    
                # Fix change calculation
                # pre_close = float(row.get("pre_close", 0))
                # price = float(row.get("price", 0))
                # if pre_close > 0:
                #     change_pct = (price - pre_close) / pre_close * 100
            except Exception as e:
                logger.error(f"Tushare 获取实时行情失败: {e}")
            return {}
    
    def get_stock_info(self, ts_code: str) -> dict:
        """获取股票基本信息"""
        if self.is_akshare:
            return self._akshare.get_stock_info(ts_code)
        else:
            # Tushare 需要查询 stock_basic
            try:
                # 优化：直接查询指定代码，避免全量拉取
                ts_code = self.normalize_code(ts_code)
                df = self._tushare.get_stock_list(ts_code=ts_code)
                if not df.empty:
                    r = df.iloc[0]
                    return {
                        'ts_code': ts_code,
                        'name': r.get('name', ''),
                        'industry': r.get('industry', ''),
                        'area': r.get('area', ''),
                        'market': r.get('market', ''),
                    }
            except Exception as e:
                logger.error(f"获取股票信息失败: {e}")
            return {'ts_code': ts_code, 'name': '未知', 'industry': '未知'}
    
    def get_index_data(
        self,
        ts_code: str = "000001.SH",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """获取指数日线数据"""
        if self.is_tushare:
            return self._tushare.get_index_daily(
                ts_code=ts_code,
                start_date=start_date,
                end_date=end_date,
            )
        else:
            # AkShare 获取指数数据
            return self._akshare.get_index_spot()
    
    def get_index_spot(self) -> pd.DataFrame:
        """获取指数实时行情"""
        if self.is_akshare:
            return self._akshare.get_index_spot()
        else:
            # 对于 Tushare，使用 get_realtime_quotes 获取主要指数
            # Sina codes: sh=000001, sz=399001, cyb=399006, sz50=000016, sz180=000010, kc50=000688
            codes = ['sh', '399001', '399006', '000016', '000010', '000688']
            try:
                df = self._tushare.get_realtime_quotes(codes)
                if not df.empty:
                    # Calculate pct_chg
                    df['price'] = pd.to_numeric(df['price'])
                    df['pre_close'] = pd.to_numeric(df['pre_close'])
                    df['pct_chg'] = ((df['price'] - df['pre_close']) / df['pre_close'] * 100).round(2)
                    
                    # Rename to match AkShare/Main expectation
                    df = df.rename(columns={
                        'code': '代码',
                        'name': '名称',
                        'price': '最新价',
                        'pct_chg': '涨跌幅',
                        'volume': '成交量',
                        'amount': '成交额'
                    })
                    return df
            except Exception as e:
                logger.error(f"Tushare 获取指数行情失败: {e}")
            
            return pd.DataFrame()
    
    def get_north_flow(self, trade_date: Optional[str] = None) -> dict:
        """获取北向资金数据"""
        if self.is_tushare:
            try:
                if trade_date:
                    df = self._tushare.get_moneyflow_hsgt(trade_date=trade_date)
                else:
                    # 如果未指定日期，获取最近 30 天的数据（Tushare 默认返回按日期降序）
                    # 避免传参 None 导致校验失败
                    from datetime import datetime, timedelta
                    end_date = self.get_today_str()
                    start_date = (datetime.strptime(end_date, "%Y%m%d") - timedelta(days=30)).strftime("%Y%m%d")
                    df = self._tushare.get_moneyflow_hsgt(start_date=start_date, end_date=end_date)
                
                if not df.empty:
                    # 取最新的一条
                    row = df.iloc[0]
                    return {
                        'north_money': float(row.get('north_money', 0)),
                        'south_money': float(row.get('south_money', 0)),
                    }
            except Exception as e:
                logger.error(f"获取北向资金失败: {e}")
        else:
            try:
                return self._akshare.get_north_flow()
            except Exception as e:
                logger.error(f"获取北向资金失败: {e}")
        return {}
    
    def get_shibor(self, trade_date: Optional[str] = None) -> dict:
        """获取 Shibor 利率数据"""
        if self.is_tushare:
            try:
                df = self._tushare.get_shibor(date=trade_date)
                if not df.empty:
                    row = df.iloc[0]
                    return {
                        'on': row.get('on', 0),
                        '1w': row.get('1w', 0),
                        '1m': row.get('1m', 0),
                        '3m': row.get('3m', 0),
                    }
            except Exception as e:
                logger.error(f"获取 Shibor 失败: {e}")
        # AkShare 暂不支持 Shibor
        return {}
    
    def get_sector_flow(self) -> pd.DataFrame:
        """获取板块资金流向"""
        if self.is_akshare:
            return self._akshare.get_sector_flow()
        return pd.DataFrame()
    
    def get_hot_stocks(self) -> pd.DataFrame:
        """获取热门股票"""
        if self.is_akshare:
            return self._akshare.get_hot_stocks()
        return pd.DataFrame()
    
    def get_stock_list(self) -> pd.DataFrame:
        """获取股票列表"""
        if self.is_tushare:
            return self._tushare.get_stock_list()
        else:
            # AkShare 通过实时行情获取股票列表
            try:
                import akshare as ak
                df = ak.stock_zh_a_spot_em()
                # 转换为统一格式
                df = df.rename(columns={
                    '代码': 'symbol',
                    '名称': 'name',
                })
                # 添加 ts_code 列
                df['ts_code'] = df['symbol'].apply(
                    lambda x: f"{x}.SZ" if x.startswith(('0', '3')) else f"{x}.SH"
                )
                return df[['ts_code', 'symbol', 'name']]
            except Exception as e:
                logger.error(f"获取股票列表失败: {e}")
                return pd.DataFrame()


# 全局单例
_data_source: Optional[UnifiedDataSource] = None


def get_data_source() -> UnifiedDataSource:
    """获取统一数据源单例"""
    global _data_source
    if _data_source is None:
        _data_source = UnifiedDataSource()
    return _data_source


def reset_data_source() -> None:
    """重置数据源单例"""
    global _data_source
    _data_source = None
