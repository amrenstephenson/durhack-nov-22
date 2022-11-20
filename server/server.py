from flask import Flask, abort, redirect, url_for, current_app
import os
from image_processor import ImageProcessorPIL as ImageProcessor
from graph_generator import GraphGeneratorPlotly as GraphGenerator
from finance_api import SymbolSplittingError, FinanceAPIBinance as FinanceAPI
from stock_predictor import StockPredictor, QUALITIES
from finance_streamer import FinanceStreamerBinance as FinanceStreamer

app = Flask(__name__)

finance_streamer = FinanceStreamer()
finance_api = FinanceAPI()
stock_predictor = StockPredictor(finance_streamer, finance_api)

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
    try:
        prediction = stock_predictor.new_prediction(quality)
    except SymbolSplittingError:
        abort(500, "The server could not collect the necessary data when splitting symbols.")
    if prediction == None:
        abort(503, "A prediction is temporarily unavailable, please try again later.")

    return prediction


@app.route("/api/image")
def easter_egg():
    orange_image_path = os.path.join(SCRIPT_DIR, "orange.jpg")
    return ImageProcessor(orange_image_path).to_rgb565()


@app.route("/api/image/<symbol>")
def image(symbol):
    image_path = generate_graph_for_symbol_pair(symbol)
    if image_path == None:
        abort(500, "The server could not collect the necessary graph data.")
    return ImageProcessor(image_path).to_rgb565()


def generate_graph_for_symbol_pair(symbol_pair: str):
    filepath = os.path.join(SCRIPT_DIR, "candlestick_graph.png")

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

    return filepath


if __name__ == "__main__":
    start_server()
