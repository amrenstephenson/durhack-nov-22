from abc import ABC, abstractmethod
import requests
from typing import Tuple, Optional


class SymbolSplittingError(Exception):
    pass


class FinanceAPI(ABC):
    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def split_symbol_pair(self, symsymbol_pairbol: str) -> Optional[Tuple[str, str]]:
        pass

    @abstractmethod
    def collect_candlestick_data(self, symbol_pair: str) -> Optional[str]:
        pass


class FinanceAPIBinance(FinanceAPI):
    def split_symbol_pair(self, symbol_pair: str) -> Optional[Tuple[str, str]]:
        try:
            resp = requests.get("https://api.binance.com/api/v3/exchangeInfo", params={"symbol": symbol_pair})
        except requests.exceptions.ConnectionError:
            raise SymbolSplittingError
        symbols = resp.json()["symbols"][0]
        return (symbols["baseAsset"], symbols["quoteAsset"])

    def collect_candlestick_data(self, symbol_pair: str) -> Optional[str]:
        try:
            return requests.get(f"https://www.binance.com/api/v3/klines?symbol={symbol_pair}&interval=1h&limit=24").json()
        except requests.exceptions.ConnectionError:
            return None
