import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from abc import ABC, abstractmethod


class GraphGenerator(ABC):
    def __init__(self, candlestick_data) -> None:
        self.candlestick_data = candlestick_data

    @abstractmethod
    def generate_candlestick_graph(self):
        pass

    @abstractmethod
    def save_graph(self, filepath: str, width: int, height: int):
        pass


class GraphGeneratorPlotly(GraphGenerator):
    def generate_candlestick_graph(self):
        pio.templates.default = "plotly_dark"
        df = pd.DataFrame(self.candlestick_data)
        df[0] /= 1000
        df[0] = pd.to_datetime(df[0], unit='s')
        self.fig = go.Figure(
            data=[go.Candlestick(x=df[0], open=df[1], high=df[2], low=df[3], close=df[4])],
            layout={
                'xaxis': {'title': 'x-label', 'visible': True, 'showticklabels': True},
                'yaxis': {'title': 'y-label', 'visible': False, 'showticklabels': True}
            }
        )

    def save_graph(self, filepath: str, width: int, height: int):
        self.fig.write_image(filepath, width=700, height=640)
