#include <Arduino.h>
#include <Math.h>
#include <WiFi.h>
#include <HTTPClient.h>

#include <SPI.h>
#include <TFT_eSPI.h>       // Hardware-specific library

#define S_TO_MICROS 1000000
#define TIMEOUT 30 * S_TO_MICROS

enum TradeRanking {
  GOOD,
  MEH,
  BAD,
  N_RANKINGS
};

struct TradeDetails {
  String symbol = "";
  String from = "";
  String to = "";
  enum TradeRanking ranking = GOOD;
  float price = 0.0;
  float percentIncrease = 0.0;
};

TFT_eSPI tft = TFT_eSPI();

TradeDetails currentTrade;
unsigned long lastInteraction = 0;
unsigned long curPage = 0;

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
    tft.setCursor(0, 10, 2);
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
  connectToWiFi();

  enum TradeRanking tradeRanking = (enum TradeRanking)random(GOOD, N_RANKINGS);
  static const String endpoints[N_RANKINGS] = {
    [GOOD] = "http://10.249.11.28:8080/api/prediction/good",
    [MEH] = "http://10.249.11.28:8080/api/prediction/meh",
    [BAD] = "http://10.249.11.28:8080/api/prediction/bad"
  };

  //parse CSV:
  String tradeCSV = GET(endpoints[tradeRanking]);
  const char* delims = ",/"; //TODO: / is not needed once we have v2 API
  char* s = strdup(tradeCSV.c_str());
  const char* part = strtok(s, delims);
  unsigned int i = 0;
  while (part) {
    switch (i++) {
      case 0:
        currentTrade.from = part;
        break;
      case 1:
        currentTrade.to = part;
        break;
      case 2:
        currentTrade.price = atof(part);
        break;
      case 3:
        currentTrade.percentIncrease = atof(part);
        break;
    }
    part = strtok(NULL, delims);
  }
  free(s);
  currentTrade.ranking = tradeRanking;
  currentTrade.symbol = currentTrade.to + "/" + currentTrade.from;

  tft.fillScreen(TFT_BLACK);
  tft.setRotation(0);

  if (micros() - lastInteraction >= TIMEOUT)
    lastInteraction = micros();
  
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
  unsigned long txtW = tft.textWidth(currentTrade.symbol);
  tft.setCursor((width - txtW) / 2, 45, 2);
  tft.println(currentTrade.symbol);

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
  if (micros() - lastInteraction >= TIMEOUT)
    lastInteraction = micros();
  
  tft.setRotation(1);
  tft.setCursor(69, 60, 2);
  tft.fillScreen(TFT_BLACK);
  tft.setTextColor(TFT_WHITE, TFT_BLACK);
  tft.println("Loading graph...");
  String dataStr = GET("http://10.249.11.28:8080/api/image/" + currentTrade.from + currentTrade.to);
  tft.fillScreen(TFT_BLACK);

  const unsigned short* dataBytes = (const unsigned short*)dataStr.c_str();
  tft.setSwapBytes(true);
  tft.pushImage(0, 0, 240, 135, dataBytes);
  
  //draw label:
  unsigned long yLblOff;
  if (currentTrade.ranking == GOOD || currentTrade.ranking == MEH) {
    yLblOff = 5;
  } else {
    yLblOff = 98;
  }
  tft.setTextColor(TFT_WHITE, TFT_BLACK);
  tft.setCursor(5, yLblOff);
  tft.println(currentTrade.symbol);
  tft.setCursor(5, yLblOff+tft.fontHeight());
  tft.printf("1%s = %.3f%s", currentTrade.from.c_str(), currentTrade.price, currentTrade.to.c_str());
}

int needsRefresh = 0;
int needsPageChange = 0;

#define BUTTON_MIN_DELAY 0.5 * S_TO_MICROS
void refreshPage(void) {
  static unsigned long lastPressed = 0;
  unsigned long now = micros();
  if (now - lastPressed > BUTTON_MIN_DELAY) {
    needsRefresh = 1;
  }
  lastPressed = now;
}

void changePage(void) {
  static unsigned long lastPressed = 0;
  unsigned long now = micros();
  if (now - lastPressed > BUTTON_MIN_DELAY) {
    needsPageChange = 1;
    needsRefresh = 1;
  }
  lastPressed = now;
}

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  randomSeed(analogRead(A0));
  Serial.println();
  pinMode(35, INPUT);
  pinMode(0, INPUT);
  attachInterrupt(35, changePage, FALLING);
  attachInterrupt(0, refreshPage, FALLING);

  Serial.println("MAC Address: " + WiFi.macAddress());

  tft.begin();
  tft.setRotation(0);

  needsRefresh = 1;
}

void loop() {
  if (needsPageChange) {
    curPage = !curPage;
  }

  if (needsRefresh) {
    if (curPage == 0)
      initBallView();
    else
      initGraphView();
  }

  needsRefresh = 0;
  needsPageChange = 0;
}
