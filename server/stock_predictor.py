from typing import Optional
import random

QUALITY_GOOD = "good"
QUALITY_MEH = "meh"
QUALITY_BAD = "bad"
QUALITIES = [QUALITY_GOOD, QUALITY_MEH, QUALITY_BAD]


class StockPredictor():
    def __init__(self, finance_streamer, finance_collector) -> None:
        self.finance_streamer = finance_streamer
        self.finance_collector = finance_collector

    def new_prediction(self, quality) -> Optional[str]:
        def clamp(num, min_value, max_value): return max(min(num, max_value), min_value)

        stream_data_count = self.finance_streamer.count_stream_data()
        if stream_data_count == 0:
            return None

        sorted_data = self.get_sorted_data_for_quality(quality)
        index = clamp(random.randrange(0, 5), 0, stream_data_count)
        prediction = sorted_data[index]

        prediction_symbol_pair = prediction[0]
        prediction_data = prediction[1]
        split_symbols = self.finance_collector.split_symbol_pair(prediction_symbol_pair)
        return ",".join([*split_symbols, prediction_data["last_price"], prediction_data["price_change_percent"]])

    def get_sorted_data_for_quality(self, quality: str):
        if quality == QUALITY_GOOD:
            return self.finance_streamer.get_sorted_data()
        elif quality == QUALITY_MEH:
            return self.finance_streamer.get_sorted_data_abs()
        elif quality == QUALITY_BAD:
            return self.finance_streamer.get_sorted_data(reverse=True)
        else:
            return ValueError("Quality must be one of " + ", ".join(QUALITIES) + ".")
