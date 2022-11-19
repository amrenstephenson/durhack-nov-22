import asyncio
import certifi
from websockets import connect
import json
import random
import threading

STREAM_SYBMOL = "btcusdt"
STREAM_TYPE = "aggTrade"
#STREAM_NAME = STREAM_SYBMOL + "@" + STREAM_TYPE
STREAM_NAME = "!ticker_1d@arr"

ENDPOINT = f"wss://stream.binance.com:9443/ws/{STREAM_NAME}"

running = True

currency = {}

def main():
    threading.Thread(target=wait_for_input_then_stop).start()
    asyncio.new_event_loop().run_until_complete(stream())


def wait_for_input_then_stop():
    global running
    input()
    running = False
    print("Stopping!")


async def stream():
    global running
    async with connect(ENDPOINT) as websocket:
        while running:
            result = await websocket.recv()
            if running:
                data = json.loads(result)
                for coin in data:
                  if coin['s'] not in currency:
                    print(coin['s'], coin['h'])
                  
                  currency[coin['s']] = coin['h']

                print(len(currency))


if __name__ == "__main__":
    main()
