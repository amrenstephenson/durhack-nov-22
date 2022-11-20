from flask import Flask, abort, redirect, url_for, current_app
from binance_streamer import BinanceStreamer
import os
from image_processor import ImageProcessorPIL as ImageProcessor
from graph_generator import GraphGeneratorPlotly as GraphGenerator
from finance_collector import FinanceCollectorBinance as FinanceCollector
from stock_predictor import StockPredictor, QUALITIES

app = Flask(__name__)

binance_streamer = BinanceStreamer()
finance_collector = FinanceCollector()
stock_predictor = StockPredictor(binance_streamer, finance_collector)

SCRIPT_DIR = os.path.dirname(__file__)


def start_server():
    app.run(host="0.0.0.0", port=8080)


@app.route("/")
def index():
    return redirect(url_for("api"))


@app.route("/api")
def api():
    return current_app.send_static_file("api.html")


@app.route("/api/prediction/<quality>")
def prediction(quality):
    if quality not in QUALITIES:
        return abort(400, "Prediction quality must be 'good', 'meh' or 'bad'.")
    return stock_predictor.new_prediction(quality)


@app.route("/api/image")
def easter_egg():
    orange_image_path = os.path.join(SCRIPT_DIR, "orange.jpg")
    return ImageProcessor(orange_image_path).to_rgb565()


@app.route("/api/image/<symbol>")
def image(symbol):
    image_path = generate_graph_for_symbol_pair(symbol)
    return ImageProcessor(image_path).to_rgb565()


def generate_graph_for_symbol_pair(symbol_pair: str):
    filepath = os.path.join(SCRIPT_DIR, "candlestick_graph.png")

    candlestick_data = finance_collector.collect_candlestick_data(symbol_pair)

    graph_g = GraphGenerator(candlestick_data)
    graph_g.generate_candlestick_graph()
    graph_g.save_graph(filepath, width=700, height=640)

    image_p = ImageProcessor(filepath)
    image_p.crop(50, 105, 653, 443)
    image_p.resize_down(240, 135)
    image_p.set_black_point(40)
    image_p.increase_contrast(2)
    image_p.save_to_file(filepath)

    return filepath


if __name__ == "__main__":
    start_server()
