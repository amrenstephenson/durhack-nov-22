from flask import Flask, abort, redirect, url_for, render_template, current_app
from binance_streamer import BinanceStreamer
import random
from enum import Enum
from functools import lru_cache
import requests
import os
from PIL import Image, ImageEnhance
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import socket
from image_processor import ImageProcessorPIL as ImageProcessor

from image_to_rgb565 import ImageToRGB565Converter

app = Flask(__name__)
binance_streamer = BinanceStreamer()

SCRIPT_DIR = os.path.dirname(__file__)

QUALITY_GOOD = "good"
QUALITY_MEH = "meh"
QUALITY_BAD = "bad"
QUALITIES = [QUALITY_GOOD, QUALITY_MEH, QUALITY_BAD]


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
    return get_prediction(quality)


@app.route("/api/image")
def easter_egg():
    orange_image_path = os.path.join(SCRIPT_DIR, "orange.jpg")
    return ImageProcessor(orange_image_path).to_rgb565()


@app.route("/api/image/<symbol>")
def image(symbol):
    image_path = generate_graph(symbol)
    return ImageProcessor(image_path).to_rgb565()


def get_prediction(quality):
    data_count = len(binance_streamer.cached_stream_data)
    if data_count == 0:
        return abort(503, "Prediction temporarily unavailable, please try again.")

    sorted_data = get_sorted_data_for_quality(quality)
    index = clamp(random.randrange(0, 5), 0, data_count)
    prediction = sorted_data[index]

    prediction_symbol = prediction[0]
    prediction_data = prediction[1]
    return ",".join([split_symbol(prediction_symbol), prediction_data["last_price"], prediction_data["price_change_percent"]])


@lru_cache(maxsize=None)
def split_symbol(symbol):
    resp = requests.get("https://api.binance.com/api/v3/exchangeInfo", params={"symbol": symbol})
    if resp and resp.json() and len(resp.json()) and "symbols" in resp.json() and len(resp.json()["symbols"]):
        symbols = resp.json()["symbols"][0]
    else:
        symbols = {"baseAsset": "ETH", "quoteAsset": "BTC"}
    return symbols["baseAsset"] + "," + symbols["quoteAsset"]


def get_sorted_data_for_quality(quality):
    if quality == QUALITY_GOOD:
        return binance_streamer.get_sorted_data()
    elif quality == QUALITY_MEH:
        return binance_streamer.get_sorted_data_abs()
    elif quality == QUALITY_BAD:
        return binance_streamer.get_sorted_data(reverse=True)


def generate_graph(crypto_symbol):
    SCRIPT_DIR = os.path.dirname(__file__)

    pio.templates.default = "plotly_dark"

    response = requests.get(f"https://www.binance.com/api/v3/klines?symbol={crypto_symbol}&interval=1h&limit=24")

    df = pd.DataFrame(response.json())
    df[0] /= 1000
    df[0] = pd.to_datetime(df[0], unit='s')
    fig = go.Figure(
        data=[go.Candlestick(x=df[0], open=df[1], high=df[2], low=df[3], close=df[4])],
        layout={
            'xaxis': {'title': 'x-label', 'visible': True, 'showticklabels': True},
            'yaxis': {'title': 'y-label', 'visible': False, 'showticklabels': True}
        }
    )

    filepath = os.path.join(SCRIPT_DIR, "candlestick.png")

    fig.write_image(filepath, width=700, height=640)

    image_p = ImageProcessor(filepath)

    image_p.crop(50, 105, 653, 443)
    image_p.resize_down(240, 135)
    image_p.set_black_point(40)
    image_p.increase_contrast(2)
    image_p.save_to_file(filepath)

    return filepath


def clamp(num, min_value, max_value):
    return max(min(num, max_value), min_value)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
