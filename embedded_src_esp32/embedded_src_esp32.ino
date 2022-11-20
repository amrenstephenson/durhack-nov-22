#include <Arduino.h>
#include <Math.h>
#include <WiFi.h>
#include <HTTPClient.h>

// Display libraries
#include <SPI.h>
#include <TFT_eSPI.h>

// Orange settings
#define ORANGE_PIN 15
#define ORANGE_THRESHOLD 27

// Timeouts
#define S_TO_MICROS 1000000
#define TIMEOUT 30 * S_TO_MICROS
#define THROW_MIN_DELAY 0.1 * S_TO_MICROS

typedef enum {
  BALL,
  GRAPH
} view_t;

view_t currentView = BALL;
unsigned long lastTouched = 0;
bool touched = false; // If orange was touched since last run through main loop
bool active = false; // If false when display is asleep waiting to be picked up

enum TradeRanking {
  GOOD,
  MEH,
  BAD,
  N_RANKINGS
};

TFT_eSPI tft = TFT_eSPI();

String tradeStr = "";
enum TradeRanking tradeRanking = GOOD;
unsigned long lastInteraction = 0;
unsigned long curPage = 0;

void orangeTouched(){
  touched = true;
}

void connectToWiFi(void) {
  if (WiFi.status() != WL_CONNECTED) {
    const char* ssid = "LinkIT";
    const char* password = "DXQjTwNw";
    WiFi.begin(ssid, password);
    Serial.println("Connecting");
    while(WiFi.status() != WL_CONNECTED) { 
      delay(500);
      Serial.print(".");
    }

    Serial.println("");
    Serial.printf("Connected to %s\n", ssid);
    Serial.println("IP address: " + WiFi.localIP().toString());
  }
}

String GET(String url) {
  String resp;

  for (;;) {
    if (WiFi.status() == WL_CONNECTED) {
      WiFiClient client;
      HTTPClient http;
      Serial.println("Requesting " + url);
      if (http.begin(client, url)) {
        int httpCode = http.GET();
        Serial.println("============== Response code: " + String(httpCode));
        if (httpCode == 200) {
          resp = http.getString();
          http.end();
          break;
        }
        http.end();
      }
    }
    
    Serial.println("[HTTPS] Unable to connect");
    tft.fillScreen(TFT_BLACK);
    tft.setCursor(10, 10, 2);
    tft.setTextColor(TFT_WHITE, TFT_RED);
    tft.println("Amren's crappy server is down");
    delay(1000);
  }

  return resp;
}

void printCentered(String str) {
  unsigned long width = tft.width();
  unsigned long y = tft.getCursorY();

  char* s = strdup(str.c_str());
  char* token = strtok(s, " ");

  char* save = NULL;
  const char* part = strtok_r(s, "\n", &save);
  while (part) {
    unsigned long txtW = tft.textWidth(part);
    unsigned long x = (width - txtW) / 2;
    tft.setCursor(x, y, 2);
    tft.println(part);

    y += tft.fontHeight();
    part = strtok_r(NULL, "\n", &save);
  }

  free(s);
}

void initBallView(void) {
  tradeRanking = (enum TradeRanking)random(GOOD, N_RANKINGS);
  static const String endpoints[N_RANKINGS] = {
    [GOOD] = "http://10.249.11.28:8080/api/currencies/prediction-string/good",
    [MEH] = "http://10.249.11.28:8080/api/currencies/prediction-string/meh",
    [BAD] = "http://10.249.11.28:8080/api/currencies/prediction-string/bad"
  };
  tradeStr = GET(endpoints[tradeRanking]);

  tft.fillScreen(TFT_BLACK);
  tft.setRotation(0);
  
  unsigned long width = tft.width();
  unsigned long height = tft.height();

  //draw triangle:
  unsigned long pad = 10;
  unsigned long side_len = width - 2 * pad;
  unsigned long tri_height = sqrt(side_len*side_len - (side_len/2)*(side_len/2));
  unsigned long top_offset = height - pad - tri_height;
  tft.fillTriangle(width / 2, height - pad, pad, top_offset, width - pad, top_offset, TFT_BLUE);

  //draw trade name:
  tft.setTextColor(TFT_WHITE, TFT_BLACK);
  tft.setTextSize(1);
  unsigned long txtW = tft.textWidth(tradeStr);
  tft.setCursor((width - txtW) / 2, 45, 2);
  tft.println(tradeStr);

  //draw prediction:
  static const String predictions[N_RANKINGS] = {
    [GOOD] = "Outlook\ngood.",
    [MEH] = "Future\nuncertain.",
    [BAD] = "Very\ndoubtful."
  };
  tft.setTextColor(TFT_WHITE, TFT_BLUE);
  tft.setTextSize(1);
  tft.setCursor(0, top_offset + 20, 2);
  printCentered(predictions[tradeRanking]);
}

void initGraphView(void) {
  tft.setRotation(1);
  tft.setCursor(69, 60, 2);
  tft.fillScreen(TFT_BLACK);
  tft.setTextColor(TFT_WHITE, TFT_BLACK);
  tft.println("Loading graph...");
  String dataStr = GET("http://10.249.11.28:8080/api/image/" + tradeStr);
  tft.fillScreen(TFT_BLACK);

  const unsigned short* dataBytes = (const unsigned short*)dataStr.c_str();
  tft.setSwapBytes(true);
  tft.pushImage(0, 0, 240, 135, dataBytes);
}

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  randomSeed(analogRead(A0));
  Serial.println();
  touchAttachInterrupt(ORANGE_PIN, orangeTouched, ORANGE_THRESHOLD);
  attachInterrupt(35, orangeTouched, FALLING);

  Serial.println("MAC Address: " + WiFi.macAddress());

  tft.begin();
  tft.setRotation(0);
}

void loop() {
  // Ensure connected to wifi
  connectToWiFi();

  unsigned long currentTime = micros();

  // If touched since last loop
  if (touched) {
    // If touched while timed out, render display
    if (!active) {
      currentView = BALL;
      active = true;
      initBallView();
    }
    // If touched while active, check if been not touched long enough to switch page
    else if (currentTime - lastTouched >= THROW_MIN_DELAY) {
      if (currentView == BALL) {
        currentView = GRAPH;
        initGraphView();
      }
      else {
        currentView = BALL;
        initBallView();
      }
    }

    touched = false;
    lastTouched = currentTime;
  }

  // If active and not touched in TIMEOUT millis then reset state and turn off screen
  if (active && currentTime - lastTouched > TIMEOUT) {
    active = false;
    tft.fillScreen(TFT_BLACK);
  }
}
