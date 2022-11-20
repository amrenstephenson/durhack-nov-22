import asyncio
from websockets import connect
import json
import threading
from decimal import *
from collections import OrderedDict


class BinanceStreamer():
    STREAM_NAME = "!ticker_1d@arr"
    ENDPOINT = f"wss://stream.binance.com:9443/ws/{STREAM_NAME}"

    def __init__(self, debug=False):
        self.debug = debug
        self.cached_stream_data = {}

        threading.Thread(target=self.event_loop_thread).start()

    def event_loop_thread(self):
        asyncio.new_event_loop().run_until_complete(self.get_data_from_websocket())

    def get_sorted_data(self, reverse=False):
        return sorted(self.cached_stream_data.items(), key=lambda t: Decimal(t[1]["price_change_percent"]), reverse=not reverse)

    def get_sorted_data_abs(self):
        return sorted(self.cached_stream_data.items(), key=lambda t: abs(Decimal(t[1]["price_change_percent"])))

    async def get_data_from_websocket(self):
        global running
        async with connect(self.ENDPOINT) as websocket:
            while True:
                stream_data = await websocket.recv()
                stream_json = json.loads(stream_data)

                for item in stream_json:
                    self.cached_stream_data[item["s"]] = {
                        "event_type": item["e"],
                        "event_time": item["E"],
                        "price_change": item["p"],
                        "price_change_percent": item["P"],
                        "open_price": item["o"],
                        "high_price": item["h"],
                        "low_price": item["l"],
                        "last_price": item["c"],
                        "weighted_average_price": item["w"],
                        "total_traded_base_asset_volume": item["v"],
                        "total_traded_quote_asset_volume": item["q"],
                        "statistics_open_time": item["O"],
                        "statistics_close_time": item["C"],
                        "first_trade_id": item["F"],
                        "last_trade_id": item["L"],
                        "total_number_of_trades": item["n"],
                    }


if __name__ == "__main__":
    BinanceStreamer(debug=True)
