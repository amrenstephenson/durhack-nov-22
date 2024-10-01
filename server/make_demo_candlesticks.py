import os
from graph_generator import GraphGeneratorPlotly as GraphGenerator
from finance_api import FinanceAPIBinance as FinanceAPI
from image_processor import ImageProcessorPIL as ImageProcessor
import sys

finance_api = FinanceAPI()

def generate_graph_for_symbol_pair(filepath, symbol_pair: str):
    candlestick_data = finance_api.collect_candlestick_data(symbol_pair)
    if candlestick_data == None:
        return None

    graph_g = GraphGenerator(candlestick_data)
    graph_g.generate_candlestick_graph()
    graph_g.save_graph(filepath, width=700, height=640)

    image_p = ImageProcessor(filepath)
    image_p.crop(50, 105, 653, 443)
    image_p.resize_down(240, 135)
    image_p.set_black_point(40)
    image_p.increase_contrast(2)
    image_p.save_to_file(filepath)
    return image_p.to_rgb565()

filepath = os.path.join(os.path.dirname(__file__), "candlestick_graph.png")
symbol_pair = sys.argv[1]
img_data = bytearray(generate_graph_for_symbol_pair(filepath, symbol_pair))
print(f'const unsigned short {symbol_pair}_img[] PROGMEM = {{ ', end='')
for b in img_data:
    print(f'{hex(b)},', end='')
print('};')
