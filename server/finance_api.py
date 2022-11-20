from abc import ABC, abstractmethod
import requests
from typing import Tuple


class FinanceAPI(ABC):
    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def split_symbol_pair(self, symsymbol_pairbol: str) -> Tuple[str, str]:
        pass

    @abstractmethod
    def collect_candlestick_data(self, symbol_pair: str):
        pass


class FinanceAPIBinance(FinanceAPI):
    def split_symbol_pair(self, symbol_pair: str):
        resp = requests.get("https://api.binance.com/api/v3/exchangeInfo", params={"symbol": symbol_pair})
        symbols = resp.json()["symbols"][0]
        return (symbols["baseAsset"], symbols["quoteAsset"])

    def collect_candlestick_data(self, symbol_pair: str):
        return requests.get(f"https://www.binance.com/api/v3/klines?symbol={symbol_pair}&interval=1h&limit=24").json()
