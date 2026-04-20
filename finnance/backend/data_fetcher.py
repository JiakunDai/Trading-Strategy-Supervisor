import random
import requests
from abc import ABC, abstractmethod
from typing import Optional, Tuple, Dict


class StockDataFetcher(ABC):
    """股票数据获取器抽象基类"""
    
    @abstractmethod
    def get_name(self) -> str:
        """返回数据源名称"""
        pass
    
    @abstractmethod
    def fetch_data(self, symbol: str, api_key: Optional[str] = None) -> Tuple[Optional[Dict], float, bool]:
        """
        获取股票数据
        返回: (股票信息字典, 当前价格, 是否成功)
        """
        pass


class AlphaVantageFetcher(StockDataFetcher):
    """优先级 1: Alpha Vantage 数据源"""
    
    def __init__(self):
        self.name = "Alpha Vantage"
        self.base_url = "https://www.alphavantage.co/query"
    
    def get_name(self) -> str:
        return self.name
    
    def fetch_data(self, symbol: str, api_key: Optional[str] = None) -> Tuple[Optional[Dict], float, bool]:
        if not api_key:
            print(f"[{self.name}] No API key provided")
            return None, 0.0, False
        
        try:
            params = {
                "function": "TIME_SERIES_DAILY",
                "symbol": symbol,
                "apikey": api_key,
                "outputsize": "compact"
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            data = response.json()
            
            if "Time Series (Daily)" not in data:
                error_msg = data.get("Note", data.get("Error Message", "Unknown error"))
                print(f"[{self.name}] Error: {error_msg}")
                return None, 0.0, False
            
            time_series = data["Time Series (Daily)"]
            dates = sorted(time_series.keys(), reverse=True)
            
            current_price = float(time_series[dates[0]]["4. close"])
            
            prices = []
            for i, date in enumerate(dates[:20]):
                prices.append(float(time_series[date]["4. close"]))
            ma20 = sum(prices) / len(prices) if prices else current_price
            
            return {
                'current': current_price,
                'ma20': ma20,
                'source': self.name
            }, current_price, True
            
        except Exception as e:
            print(f"[{self.name}] Error fetching {symbol}: {e}")
            return None, 0.0, False


class PolygonFetcher(StockDataFetcher):
    """优先级 2: Polygon.io 数据源"""
    
    def __init__(self):
        self.name = "Polygon.io"
        self.base_url = "https://api.polygon.io"
    
    def get_name(self) -> str:
        return self.name
    
    def fetch_data(self, symbol: str, api_key: Optional[str] = None) -> Tuple[Optional[Dict], float, bool]:
        if not api_key:
            print(f"[{self.name}] No API key provided")
            return None, 0.0, False
        
        try:
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=100)).strftime('%Y-%m-%d')
            
            url = f"{self.base_url}/v2/aggs/ticker/{symbol}/range/1/day/{start_date}/{end_date}"
            params = {"apiKey": api_key}
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get("status") != "OK" or "results" not in data:
                print(f"[{self.name}] Error: {data.get('error', 'Unknown error')}")
                return None, 0.0, False
            
            results = data["results"]
            if not results:
                return None, 0.0, False
            
            current_price = results[-1]["c"]
            
            prices = [r["c"] for r in results[-20:]]
            ma20 = sum(prices) / len(prices) if prices else current_price
            
            return {
                'current': current_price,
                'ma20': ma20,
                'source': self.name
            }, current_price, True
            
        except Exception as e:
            print(f"[{self.name}] Error fetching {symbol}: {e}")
            return None, 0.0, False


class FinnhubFetcher(StockDataFetcher):
    """优先级 3: Finnhub 数据源"""
    
    def __init__(self):
        self.name = "Finnhub"
        self.base_url = "https://finnhub.io/api/v1"
    
    def get_name(self) -> str:
        return self.name
    
    def fetch_data(self, symbol: str, api_key: Optional[str] = None) -> Tuple[Optional[Dict], float, bool]:
        if not api_key:
            print(f"[{self.name}] No API key provided")
            return None, 0.0, False
        
        try:
            url = f"{self.base_url}/quote"
            params = {
                "symbol": symbol,
                "token": api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if "c" not in data:
                print(f"[{self.name}] Error: {data.get('error', 'Unknown error')}")
                return None, 0.0, False
            
            current_price = data["c"]
            ma20 = current_price * 0.98
            
            return {
                'current': current_price,
                'ma20': ma20,
                'source': self.name
            }, current_price, True
            
        except Exception as e:
            print(f"[{self.name}] Error fetching {symbol}: {e}")
            return None, 0.0, False


class YahooFinanceFetcher(StockDataFetcher):
    """备用: Yahoo Finance 数据源（无API Key）"""
    
    def __init__(self):
        self.name = "Yahoo Finance"
        self._tickers = {}
    
    def get_name(self) -> str:
        return self.name
    
    def fetch_data(self, symbol: str, api_key: Optional[str] = None) -> Tuple[Optional[Dict], float, bool]:
        try:
            import yfinance as yf
            
            if symbol not in self._tickers:
                self._tickers[symbol] = yf.Ticker(symbol)
            
            ticker = self._tickers[symbol]
            data = ticker.history(period='6mo')
            
            if data.empty:
                return None, 0.0, False
            
            current_price = data['Close'].iloc[-1]
            ma20 = data['Close'].tail(20).mean()
            
            return {
                'current': current_price,
                'ma20': ma20,
                'source': self.name
            }, current_price, True
            
        except Exception as e:
            print(f"[{self.name}] Error fetching {symbol}: {e}")
            return None, 0.0, False


class MockDataFetcher(StockDataFetcher):
    """最后备选: 模拟数据数据源"""
    
    def __init__(self):
        self.name = "Mock Data"
        self._base_prices = {
            'VOO': 450, 'QQQ': 420, 'GLD': 200,
            'MSFT': 420, 'AAPL': 180, 'GOOGL': 150,
            'AMZN': 180, 'NVDA': 500, 'TSLA': 250,
            'META': 480, 'BRK-B': 400, 'SPY': 500
        }
    
    def get_name(self) -> str:
        return self.name
    
    def _get_base_price(self, symbol: str) -> float:
        """获取基准价格，如果不在预定义列表中则使用随机基准"""
        if symbol in self._base_prices:
            return self._base_prices[symbol]
        return 100.0 + (hash(symbol) % 400)
    
    def fetch_data(self, symbol: str, api_key: Optional[str] = None) -> Tuple[Optional[Dict], float, bool]:
        try:
            base = self._get_base_price(symbol)
            current_price = base * (1 + (random.random() - 0.5) * 0.15)
            ma20 = base * (1 + (random.random() - 0.5) * 0.1)
            
            return {
                'current': current_price,
                'ma20': ma20,
                'source': self.name
            }, current_price, True
            
        except Exception as e:
            print(f"[{self.name}] Error generating mock data for {symbol}: {e}")
            return None, 0.0, False


class DataFetcherManager:
    """数据获取管理器，支持多个数据源链式尝试"""
    
    def __init__(self):
        self._fetchers: list = []
        self._api_keys: Dict[str, str] = {}
        self._init_default_fetchers()
    
    def _init_default_fetchers(self):
        """初始化默认的数据源列表（按优先级排序）"""
        self.add_fetcher(AlphaVantageFetcher())
        self.add_fetcher(PolygonFetcher())
        self.add_fetcher(FinnhubFetcher())
        self.add_fetcher(YahooFinanceFetcher())
        self.add_fetcher(MockDataFetcher())
    
    def set_api_key(self, source_name: str, api_key: str) -> None:
        """设置某个数据源的 API Key"""
        self._api_keys[source_name] = api_key
    
    def get_api_key(self, source_name: str) -> Optional[str]:
        """获取某个数据源的 API Key"""
        return self._api_keys.get(source_name)
    
    def add_fetcher(self, fetcher: StockDataFetcher) -> None:
        """添加一个新的数据源到链的末尾"""
        self._fetchers.append(fetcher)
    
    def get_stock_data(self, symbol: str) -> Tuple[Optional[Dict], float, str]:
        """
        依次尝试所有数据源获取股票数据
        返回: (股票信息字典, 当前价格, 使用的数据源名称)
        """
        for fetcher in self._fetchers:
            try:
                api_key = self.get_api_key(fetcher.get_name())
                data, price, success = fetcher.fetch_data(symbol, api_key)
                if success:
                    print(f"[DataFetcher] Successfully fetched {symbol} from {fetcher.get_name()}")
                    return data, price, fetcher.get_name()
            except Exception as e:
                print(f"[DataFetcher] {fetcher.get_name()} failed for {symbol}: {e}")
                continue
        
        return None, 0.0, "None"
    
    def get_available_sources(self) -> list:
        """获取所有可用的数据源名称"""
        return [f.get_name() for f in self._fetchers]


from datetime import datetime, timedelta

_fetcher_manager: Optional[DataFetcherManager] = None

def get_fetcher_manager() -> DataFetcherManager:
    """获取数据获取管理器单例"""
    global _fetcher_manager
    if _fetcher_manager is None:
        _fetcher_manager = DataFetcherManager()
    return _fetcher_manager

def fetch_stock_data(symbol: str) -> Tuple[Optional[Dict], float, str]:
    """便捷函数：直接获取股票数据"""
    return get_fetcher_manager().get_stock_data(symbol)
