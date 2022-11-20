# Fortune Fruits
## Inspiration
This year, our team was very interested in trying out a hardware hack. When we heard about QRT's challenges to visualise the crypto exchange market, we knew what we had to do. It was time to **augment** some bananas!

## What it does
We created a banana with a built-in TFT LCD display that displays predictions about profitable trades and shows historical trend graphs. These augmented bananas use [capacitance](https://en.wikipedia.org/wiki/Capacitance) to detect when the user picks them up or throws them in the air. This allows the bananas to respond to interaction and know when to display new information.

## How we built it
- We build a python application using the [websockets](https://pypi.org/project/websockets/) library to stream trade data from [Binance](https://www.binance.com/en)'s WSS API
- We perform analysis on the trade data to make predictions of profitable trades
- We expose these predictions via a HTTP endpoint using python's [flask](https://flask.palletsprojects.com/en/2.2.x/) library
- We augment a ESP microcontroller into a banana which fetches predictions from our HTTP server
- We display predictions and candlestick charts from our server on the TFT LCD in the banana
- We soldered a wire onto the microcontroller to take capacitance readings of the banana so it knows when it is being held

## Challenges we ran into
The very first challenge we encountered was gathering the data from Binance via a ```websocket```. The Binance documentation was helpful but didn't have any specific examples and TLS authentication was a additional problem.

## Accomplishments that we're proud of
- We performed surgery on a banana
- We measured the capacitance of a banana to determine when somebody is holding it

## What we learned
- Bananas don't last long after augmentation.
- Websockets are amazing - once they start working.

## What's next for Fortune Fruits
The potential is limitless. A larger display could provide new pineapples perspectives, miniaturisation could allow for keyhole surgery on a grape to take place, or we could even witness a fully wireless watermelon.
