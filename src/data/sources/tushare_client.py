"""Tushare Pro 数据源客户端

封装 Tushare Pro API，提供：
- 日线/分钟线行情数据
- 指数数据
- 集合竞价数据
- 本地缓存与增量更新
"""

from datetime import date, datetime
from typing import Optional

import pandas as pd
import tushare as ts
from loguru import logger

from src.config import get_settings


class TushareClient:
    """Tushare Pro API 客户端"""
    
    def __init__(self, token: Optional[str] = None):
        """初始化客户端
        
        Args:
            token: Tushare Pro Token，默认从配置读取
        """
        settings = get_settings()
        self.token = token or settings.tushare.token.get_secret_value()
        
        if not self.token:
            raise ValueError("Tushare Token 未配置，请在 .env 中设置 TUSHARE_TOKEN")
        
        # 配置代理 (User provided)
        import os
        proxy_url = "http://user:liuhkcxjvasrdg@8.140.4.230:8888"
        os.environ["HTTP_PROXY"] = proxy_url
        os.environ["HTTPS_PROXY"] = proxy_url
        # Configure NO_PROXY to prevent other clients (like AkShare/Eastmoney) from using this proxy
        # Note: Add leading dots for subdomain matching and specific domains
        os.environ["NO_PROXY"] = "eastmoney.com,.eastmoney.com,sina.com.cn,.sina.com.cn,sinajs.cn,.sinajs.cn,127.0.0.1,localhost"
        
        # 初始化 Tushare Pro API
        ts.set_token(self.token)
        self.pro = ts.pro_api()
        logger.info("Tushare Pro 客户端初始化成功")
    
    def get_daily(
        self,
        ts_code: Optional[str] = None,
        trade_date: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """获取日线行情数据
        
        Args:
            ts_code: 股票代码（如 000001.SZ）
            trade_date: 交易日期（YYYYMMDD）
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            包含 OHLCV 数据的 DataFrame
        """
        try:
            df = self.pro.daily(
                ts_code=ts_code,
                trade_date=trade_date,
                start_date=start_date,
                end_date=end_date,
            )
            logger.debug(f"获取日线数据: {ts_code}, 记录数: {len(df)}")
            return df
        except Exception as e:
            logger.error(f"获取日线数据失败: {e}")
            raise
    
    def get_daily_basic(
        self,
        ts_code: Optional[str] = None,
        trade_date: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """获取每日基本面指标（PE、PB、换手率等）
        
        Args:
            ts_code: 股票代码
            trade_date: 交易日期
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            基本面指标 DataFrame
        """
        try:
            df = self.pro.daily_basic(
                ts_code=ts_code,
                trade_date=trade_date,
                start_date=start_date,
                end_date=end_date,
                fields="ts_code,trade_date,close,turnover_rate,turnover_rate_f,"
                       "volume_ratio,pe,pe_ttm,pb,ps,ps_ttm,dv_ratio,dv_ttm,"
                       "total_share,float_share,free_share,total_mv,circ_mv",
            )
            logger.debug(f"获取基本面数据: {ts_code}, 记录数: {len(df)}")
            return df
        except Exception as e:
            logger.error(f"获取基本面数据失败: {e}")
            raise
    
    def get_index_daily(
        self,
        ts_code: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """获取指数日线行情
        
        Args:
            ts_code: 指数代码（如 000001.SH 上证指数）
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            指数行情 DataFrame
        """
        try:
            df = self.pro.index_daily(
                ts_code=ts_code,
                start_date=start_date,
                end_date=end_date,
            )
            logger.debug(f"获取指数数据: {ts_code}, 记录数: {len(df)}")
            return df
        except Exception as e:
            logger.error(f"获取指数数据失败: {e}")
            raise
    
    def get_stock_list(self, market: Optional[str] = None, ts_code: Optional[str] = None) -> pd.DataFrame:
        """获取股票列表
        
        Args:
            market: 市场类型（主板/创业板/科创板/北交所）
            ts_code: 股票代码（如果指定，只查询该股票）
            
        Returns:
            股票列表 DataFrame
        """
        try:
            df = self.pro.stock_basic(
                ts_code=ts_code if ts_code else "",
                exchange="",
                list_status="L",
                fields="ts_code,symbol,name,area,industry,market,list_date",
            )
            if market and not ts_code:
                df = df[df["market"] == market]
            logger.debug(f"获取股票列表, 记录数: {len(df)}")
            return df
        except Exception as e:
            logger.error(f"获取股票列表失败: {e}")
            raise
    
    def get_trade_cal(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        is_open: Optional[int] = None,
    ) -> pd.DataFrame:
        """获取交易日历
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            is_open: 是否交易日（1=是，0=否）
            
        Returns:
            交易日历 DataFrame
        """
        try:
            df = self.pro.trade_cal(
                exchange="SSE",
                start_date=start_date,
                end_date=end_date,
                is_open=is_open,
            )
            return df
        except Exception as e:
            logger.error(f"获取交易日历失败: {e}")
            raise
    
    def get_today_str(self) -> str:
        """获取今日日期字符串（YYYYMMDD）"""
        return date.today().strftime("%Y%m%d")
    
    def get_moneyflow_hsgt(
        self,
        trade_date: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """获取沪深港通资金流向
        
        Args:
            trade_date: 交易日期
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            北向资金数据 DataFrame
        """
        try:
            # 过滤 None 参数
            kwargs = {
                k: v for k, v in {
                    "trade_date": trade_date,
                    "start_date": start_date,
                    "end_date": end_date,
                }.items() if v is not None
            }
            
            df = self.pro.moneyflow_hsgt(**kwargs)
            logger.debug(f"获取北向资金数据, 记录数: {len(df)}")
            return df
        except Exception as e:
            logger.error(f"获取北向资金数据失败: {e}")
            raise
    
    def get_shibor(
        self,
        date: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """获取 Shibor 利率数据
        
        Args:
            date: 日期
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            Shibor 数据 DataFrame
        """
        try:
            df = self.pro.shibor(
                date=date,
                start_date=start_date,
                end_date=end_date,
            )
            logger.debug(f"获取 Shibor 数据, 记录数: {len(df)}")
            return df
        except Exception as e:
            logger.error(f"获取 Shibor 数据失败: {e}")
            raise


    def get_fina_indicator(
        self,
        ts_code: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        period: Optional[str] = None
    ) -> pd.DataFrame:
        """获取财务指标数据
        
        Args:
            ts_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            period: 报告期
            
        Returns:
            财务指标 DataFrame
        """
        try:
            df = self.pro.fina_indicator(
                ts_code=ts_code,
                start_date=start_date,
                end_date=end_date,
                period=period
            )
            logger.debug(f"获取财务指标: {ts_code}, 记录数: {len(df)}")
            return df
        except Exception as e:
            logger.error(f"获取财务指标失败: {e}")
            raise

    def get_moneyflow(
        self,
        ts_code: str,
        trade_date: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """获取个股资金流向
        
        Args:
            ts_code: 股票代码
            trade_date: 交易日期
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            资金流向 DataFrame
        """
        try:
            df = self.pro.moneyflow(
                ts_code=ts_code,
                trade_date=trade_date,
                start_date=start_date,
                end_date=end_date
            )
            logger.debug(f"获取个股资金流向: {ts_code}, 记录数: {len(df)}")
            return df
        except Exception as e:
            logger.error(f"获取个股资金流向失败: {e}")
            raise

    def get_forecast(
        self,
        ts_code: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """获取业绩预告
        
        Args:
            ts_code: 股票代码
            start_date: 公告开始日期
            end_date: 公告结束日期
            
        Returns:
            业绩预告 DataFrame
        """
        try:
            df = self.pro.forecast(
                ts_code=ts_code,
                start_date=start_date,
                end_date=end_date
            )
            logger.debug(f"获取业绩预告: {ts_code}, 记录数: {len(df)}")
            return df
        except Exception as e:
            logger.error(f"获取业绩预告失败: {e}")
            raise

    def get_realtime_quotes(self, ts_code: str) -> pd.DataFrame:
        """获取实时行情 (使用 Tushare 旧版接口/Sina源)
        
        Args:
            ts_code: 股票代码 (e.g. 000001.SZ)
            
        Returns:
            实时行情 DataFrame
        """
        try:
            # Tushare get_realtime_quotes needs pure code usually, but let's check.
            # actually ts.get_realtime_quotes handles list of codes.
            # It expects code string/list. 
            # If we pass "000001.SZ", does it work? 
            # Usually strict numbers like "000001".
            if isinstance(ts_code, list):
                # Handle list of codes
                codes = [c.split('.')[0] if isinstance(c, str) else str(c) for c in ts_code]
                df = ts.get_realtime_quotes(codes)
            else:
                code = ts_code.split('.')[0]
                df = ts.get_realtime_quotes(code)
            return df
        except Exception as e:
            logger.error(f"获取实时行情失败: {e}")
            return pd.DataFrame()

    def get_corporate_events(
        self,
        ts_code: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """获取公司大事（替代公告接口）
        
        聚合：
        1. 业绩预告 (forecast)
        2. 业绩快报 (express)
        3. 分红送转 (dividend)
        4. 限售解禁 (share_float)
        
        Returns:
            DataFrame columns: [ann_date, title, type]
        """
        events = []
        
        try:
            # 1. 业绩预告
            df_forecast = self.pro.forecast(ts_code=ts_code, start_date=start_date, end_date=end_date)
            if not df_forecast.empty:
                for _, row in df_forecast.iterrows():
                    type_str = row.get('type', '未知')
                    min_chg = row.get('p_change_min')
                    max_chg = row.get('p_change_max')
                    chg_str = f"{min_chg}%~{max_chg}%" if min_chg and max_chg else "N/A"
                    events.append({
                        'ann_date': row.get('ann_date'),
                        'title': f"业绩预告: {type_str} ({chg_str})",
                        'type': 'forecast'
                    })
            
            # 2. 业绩快报
            df_express = self.pro.express(ts_code=ts_code, start_date=start_date, end_date=end_date)
            if not df_express.empty:
                for _, row in df_express.iterrows():
                    rev_yoy = row.get('revenue_yoy')
                    net_yoy = row.get('yoy_net_profit')
                    events.append({
                        'ann_date': row.get('ann_date'),
                        'title': f"业绩快报: 营收同比{rev_yoy}%, 净利同比{net_yoy}%",
                        'type': 'express'
                    })
                    
            # 3. 分红送转
            df_div = self.pro.dividend(ts_code=ts_code, ann_date=start_date) # dividend usually filters by ann_date
            # Tushare dividend API annoyingly filters by specific date usually or just ts_code.
            # Let's try just ts_code and filter later if needed, but pro.dividend might need fields.
            # Using defaults.
            if df_div is not None and not df_div.empty: # Assuming previous call cached or we make new one
                pass # Already called? No.
            
            # Actually calling dividend inside structure
            df_div = self.pro.dividend(ts_code=ts_code)
            if not df_div.empty:
               # Filter by date if start_date provided
               if start_date:
                   df_div = df_div[df_div['ann_date'] >= start_date]
               if end_date:
                   df_div = df_div[df_div['ann_date'] <= end_date]
               
               for _, row in df_div.iterrows():
                   plan = row.get('div_proc', '实施')
                   stk = row.get('stk_div', 0)
                   cash = row.get('cash_div_tax', 0)
                   events.append({
                       'ann_date': row.get('ann_date'),
                       'title': f"分红: {plan} (10送{stk}派{cash}元)",
                       'type': 'dividend'
                   })

            # 4. 限售解禁
            df_float = self.pro.share_float(ts_code=ts_code, start_date=start_date, end_date=end_date)
            if not df_float.empty:
                for _, row in df_float.iterrows():
                    ratio = row.get('float_ratio', 0)
                    events.append({
                        'ann_date': row.get('float_date'), # Using float_date as event date
                        'title': f"限售解禁: 比例{ratio}%",
                        'type': 'share_float'
                    })
                    
        except Exception as e:
            logger.warning(f"获取公司大事失败: {e}")
            
        if not events:
            return pd.DataFrame()
            
        df_res = pd.DataFrame(events)
        return df_res.sort_values('ann_date', ascending=False)

    def get_top10_holders(
        self,
        ts_code: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """获取前十大股东
        
        Args:
            ts_code: 股票代码
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
            
        Returns:
            前十大股东 DataFrame
        """
        try:
            # 如果未指定日期，默认查询最近一个报告期
            # Tushare top10_holders 接口可以直接传 ts_code 获取所有历史，按日期降序
            # 我们可以获取最近的
            df = self.pro.top10_holders(
                ts_code=ts_code,
                start_date=start_date,
                end_date=end_date
            )
            logger.debug(f"获取前十大股东: {ts_code}, 记录数: {len(df)}")
            return df
        except Exception as e:
            logger.error(f"获取前十大股东失败: {e}")
            return pd.DataFrame()


# 全局客户端单例
_client: Optional[TushareClient] = None


def get_tushare_client() -> TushareClient:
    """获取 Tushare 客户端单例"""
    global _client
    if _client is None:
        _client = TushareClient()
    return _client
