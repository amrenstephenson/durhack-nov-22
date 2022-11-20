import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import json
import os
from PIL import Image


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

    image = Image.open(filepath)
    image = image.crop((70-20, 90+15, 630+43-20, 30 + 338+50+10+15))
    image.thumbnail((240, 135), Image.Resampling.LANCZOS)
    image.save(filepath, quality=100, optimize=True)

    return filepath


if __name__ == "__main__":
    generate_graph()
