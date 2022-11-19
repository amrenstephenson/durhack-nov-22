#import importlib
from image_generator import ImageGenerator
from http.server import BaseHTTPRequestHandler, HTTPServer
import os
#import sys
import json
from collections import OrderedDict
import random
from decimal import *
from binance_streamer import BinanceStreamer
import requests
from functools import cache

SCRIPT_DIR = os.path.dirname(__file__)
# visualisation_path = os.path.join(SCRIPT_DIR, "..", "visualisation", "visualisation.py")

# loader = importlib.machinery.SourceFileLoader("visualisation", visualisation_path)
# spec = importlib.util.spec_from_loader("visualisation", loader)
# visualisation = importlib.util.module_from_spec(spec)
# loader.exec_module(visualisation)


HOST_NAME = "0.0.0.0"
SERVER_PORT = 8080

ALLOWED_PATHS = ["dashboard.html", "api.html"]

binance_streamer = BinanceStreamer()
image_generator = ImageGenerator()


class DurhackServer(BaseHTTPRequestHandler):

    def do_GET(self):
        SCRIPT_DIR = os.path.dirname(__file__)

        path = self.path
        path = path[1:]  # Remove leading /
        path = path[:-1] if path.endswith("/") else path  # Remove trailing / (if there is one)
        if path == "api/currencies/num":
            self.good_response_plain(str(len(binance_streamer.cached_stream_data)))
        elif path == "api/currencies/raw":
            self.good_response_json(json.dumps(binance_streamer.cached_stream_data))
        elif path == "api/currencies/prediction":
            self.good_response_json(json.dumps(self.new_prediction()))
        elif path == "api/currencies/prediction-string":
            prediction = self.new_prediction()
            if prediction == None:
                self.good_response_plain("The future remains uncertain.")
            else:
                self.good_response_plain(f"{prediction[0]}")
        elif path == "api/image":
            # text = "const unsigned short bootlogo[32400] PROGMEM={"
            # byte_data = image_generator.generate_image()
            # for i in range(0, len(byte_data), 2):
            #     text += "0x"
            #     text += str(hex(byte_data[i]))[2:].zfill(2)
            #     text += str(hex(byte_data[i+1]))[2:].zfill(2)
            #     text += ","
            # text = text[:-1]
            # text += "};"

            # with open("image_data.h", "w") as f:
            #     f.write(text)

            self.good_response_bytes(image_generator.generate_image())
        elif path == "":
            self.send_response(301)
            self.send_header("Location", "/dashboard")
            self.end_headers()
        else:
            path = path + ".html" if "." not in path else path  # Default to .html if no file type is given.

            if path in ALLOWED_PATHS:
                with open(os.path.join(SCRIPT_DIR, "public", path), "r") as f:
                    self.good_response_html(f.read())
            else:
                self.send_response(404)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(bytes(f"<h1>ERROR 404</h1>{self.path} not found.", "utf-8"))

    def new_prediction(self):
        sorted_percentages = OrderedDict(sorted(binance_streamer.cached_stream_data.items(), key=lambda t: Decimal(t[1]["price_change_percent"])))
        prediction_index = len(sorted_percentages) - random.randrange(1, 6)
        if prediction_index < 0:
            prediction_index = 0
        if len(sorted_percentages) == 0:
            return None
        else:
            prediction_symbol = list(sorted_percentages.items())[prediction_index]
            symbol_info = self.get_symbol_info(prediction_symbol[0])
            return (f"{symbol_info['baseAsset']}/{symbol_info['quoteAsset']}", prediction_symbol[1])

    @cache
    def get_symbol_info(self, symbol):
        resp = requests.get("https://api.binance.com/api/v3/exchangeInfo", params={"symbol": symbol})
        if resp and resp.json() and len(resp.json()) and "symbols" in resp.json() and len(resp.json()["symbols"]):
            return resp.json()["symbols"][0]
        return {"baseAsset": "ETH", "quoteAsset": "BTC"}

    def good_response_plain(self, text):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(bytes(str(text), "utf-8"))

    def good_response_json(self, text):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(bytes(str(text), "utf-8"))

    def good_response_html(self, text):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes(str(text), "utf-8"))

    def good_response_bytes(self, bytes_content):
        self.send_response(200)
        self.send_header("Content-type", "application/octet-stream")
        self.end_headers()
        self.wfile.write(bytes_content)


if __name__ == "__main__":
    durhack_server = HTTPServer((HOST_NAME, SERVER_PORT), DurhackServer)
    print(f"Server started at http://{HOST_NAME}:{SERVER_PORT}")

    try:
        durhack_server.serve_forever()
    except KeyboardInterrupt:
        pass

    durhack_server.server_close()
    print("Server stopped.")
