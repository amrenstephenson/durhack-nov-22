#include <Arduino.h>
#include <Math.h>
#include <WiFi.h>
#include <HTTPClient.h>

#include <SPI.h>
#include <TFT_eSPI.h>       // Hardware-specific library

#define S_TO_MICROS 1000000
#define TIMEOUT 30 * S_TO_MICROS

TFT_eSPI tft = TFT_eSPI();

String tradeStr = "";
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
    tft.setCursor(0, 0, 2);
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
  tradeStr = GET("http://10.249.11.28:8080/api/currencies/prediction-string");

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
  unsigned long txtW = tft.textWidth(tradeStr);
  tft.setCursor((width - txtW) / 2, 20, 2);
  tft.println(tradeStr);

  //draw prediction:
  tft.setTextColor(TFT_WHITE, TFT_BLUE);
  tft.setTextSize(1);
  tft.setCursor(0, top_offset + 20, 2);
  printCentered("Outlook\ngood.");
}

void initGraphView(void) {
  if (micros() - lastInteraction >= TIMEOUT)
    lastInteraction = micros();
  
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
