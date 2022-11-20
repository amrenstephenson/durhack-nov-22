from typing import Optional
import random

QUALITY_GOOD = "good"
QUALITY_MEH = "meh"
QUALITY_BAD = "bad"
QUALITIES = [QUALITY_GOOD, QUALITY_MEH, QUALITY_BAD]


class StockPredictor():
    def __init__(self, binance_streamer, finance_collector) -> None:
        self.binance_streamer = binance_streamer
        self.finance_collector = finance_collector

    def new_prediction(self, quality) -> Optional[str]:
        def clamp(num, min_value, max_value): return max(min(num, max_value), min_value)

        data_count = len(self.binance_streamer.cached_stream_data)
        if data_count == 0:
            return None

        sorted_data = self.get_sorted_data_for_quality(quality)
        index = clamp(random.randrange(0, 5), 0, data_count)
        prediction = sorted_data[index]

        prediction_symbol_pair = prediction[0]
        prediction_data = prediction[1]
        return ",".join([*self.finance_collector.split_symbol_pair(prediction_symbol_pair), prediction_data["last_price"], prediction_data["price_change_percent"]])

    def get_sorted_data_for_quality(self, quality: str):
        if quality == QUALITY_GOOD:
            return self.binance_streamer.get_sorted_data()
        elif quality == QUALITY_MEH:
            return self.binance_streamer.get_sorted_data_abs()
        elif quality == QUALITY_BAD:
            return self.binance_streamer.get_sorted_data(reverse=True)
        else:
            return ValueError("Quality must be one of " + ", ".join(QUALITIES) + ".")
