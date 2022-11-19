import asyncio
import certifi
from websockets import connect
import json
import random
import threading


class Visualisation():
    # STREAM_SYBMOL = "btcusdt"
    # STREAM_TYPE = "aggTrade"
    # STREAM_NAME = STREAM_SYBMOL + "@" + STREAM_TYPE
    STREAM_NAME = "!ticker_1d@arr"

    ENDPOINT = f"wss://stream.binance.com:9443/ws/{STREAM_NAME}"

    def __init__(self, debug=False):
        self.debug = debug
        self.currency = {}

        threading.Thread(target=self.start_event_loop).start()

    def start_event_loop(self):
        asyncio.new_event_loop().run_until_complete(self.stream())

    async def stream(self):
        global running
        async with connect(self.ENDPOINT) as websocket:
            while True:
                result = await websocket.recv()
                data = json.loads(result)
                with open("temp.json", "w") as f:
                    f.write(json.dumps(data))
                for coin in data:
                    if self.debug and coin['s'] not in self.currency:
                        print(coin['s'], coin['h'])

                    self.currency[coin['s']] = coin['h']

                if self.debug:
                    print(len(self.currency))


if __name__ == "__main__":
    Visualisation(debug=True)
