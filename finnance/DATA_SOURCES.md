# 数据源扩展指南

本项目使用模块化的数据源系统，可以轻松添加新的数据源。

## 📋 现有数据源

| 数据源 | 优先级 | 说明 |
|--------|--------|------|
| Yahoo Finance | 1 | 使用 yfinance 库获取真实数据 |
| Mock Data | 2 | 模拟数据，作为最后的备选方案 |

## 🔧 如何添加新数据源

### 步骤 1: 创建新的数据源类

在 `backend/data_fetcher.py` 中添加新的类，继承自 `StockDataFetcher`：

```python
class MyNewFetcher(StockDataFetcher):
    """我的新数据源"""
    
    def __init__(self):
        self.name = "My New Source"
    
    def get_name(self) -> str:
        return self.name
    
    def fetch_data(self, symbol: str) -> Tuple[Optional[Dict], float, bool]:
        """
        获取股票数据
        返回: (数据字典, 当前价格, 是否成功)
        """
        try:
            # 在这里实现你的数据获取逻辑
            # 例如调用某个 API
            current_price = 100.0
            ma20 = 95.0
            
            return {
                'current': current_price,
                'ma20': ma20,
                'source': self.name
            }, current_price, True
            
        except Exception as e:
            print(f"[{self.name}] Error: {e}")
            return None, 0.0, False
```

### 步骤 2: 注册新数据源

在 `DataFetcherManager._init_default_fetchers()` 方法中添加：

```python
def _init_default_fetchers(self):
    self.add_fetcher(YahooFinanceFetcher())
    self.add_fetcher(MyNewFetcher())  # 添加你的新数据源
    self.add_fetcher(MockDataFetcher())
```

## 💡 推荐的免费数据源

以下是一些可以添加的免费数据源：

### 1. Alpha Vantage
- 官网: https://www.alphavantage.co/
- 需要 API Key（免费）
- 限制: 每天 25 次请求

### 2. Polygon.io
- 官网: https://polygon.io/
- 有免费套餐
- 限制: 每分钟 5 次请求

### 3. Tiingo
- 官网: https://www.tiingo.com/
- 有免费套餐
- 限制: 每天 500 次请求

### 4. Finnhub
- 官网: https://finnhub.io/
- 有免费套餐
- 限制: 每秒 1 次请求

## 📝 示例：添加 Alpha Vantage 数据源

```python
import requests

class AlphaVantageFetcher(StockDataFetcher):
    """Alpha Vantage 数据源"""
    
    def __init__(self, api_key: str):
        self.name = "Alpha Vantage"
        self.api_key = api_key
        self.base_url = "https://www.alphavantage.co/query"
    
    def get_name(self) -> str:
        return self.name
    
    def fetch_data(self, symbol: str) -> Tuple[Optional[Dict], float, bool]:
        try:
            params = {
                "function": "TIME_SERIES_DAILY",
                "symbol": symbol,
                "apikey": self.api_key,
                "outputsize": "compact"
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            data = response.json()
            
            if "Time Series (Daily)" not in data:
                return None, 0.0, False
            
            time_series = data["Time Series (Daily)"]
            dates = sorted(time_series.keys(), reverse=True)
            
            current_price = float(time_series[dates[0]]["4. close"])
            
            # 计算20日均线
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
```

## 🎯 最佳实践

1. **错误处理**: 始终用 try-except 包裹你的数据获取逻辑
2. **超时设置**: 设置合理的请求超时时间（5-10秒）
3. **日志输出**: 使用 print 输出日志，方便调试
4. **优先级**: 把更可靠的数据源放在前面
5. **Mock Data**: 始终保留 Mock Data 作为最后的备选方案

## 🔍 测试数据源

添加新数据源后，可以运行测试：

```bash
cd backend
python test_fetcher.py
```

或者单独测试：

```python
from data_fetcher import get_fetcher_manager
manager = get_fetcher_manager()
data, price, source = manager.get_stock_data("AAPL")
print(f"Source: {source}, Price: {price}")
```
