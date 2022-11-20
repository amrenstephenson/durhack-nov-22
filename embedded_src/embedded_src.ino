#include <Arduino.h>
#include <U8g2lib.h>
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>
#include "ScrollingText.h"

#ifdef U8X8_HAVE_HW_SPI
#include <SPI.h>
#include <Wire.h>
#endif

#define S_TO_MICROS 1000000
#define TIMEOUT 30 * S_TO_MICROS

U8G2_SSD1306_128X32_UNIVISION_F_HW_I2C u8g2(U8G2_R0, /* reset=*/ 16, /* clock=*/ SCL, /* data=*/ SDA);   // pin remapping with ESP8266 HW I2C

ScrollingText* scrollingLbl = nullptr;
unsigned long lastInteraction = 0;

void connectToWiFi(void) {
  if (WiFi.status() != WL_CONNECTED) {
    const char* ssid = "LinkIT";
    const char* password = "GLapCAkH";
    WiFi.begin(ssid, password);

    Serial.print("Connecting.");
    while (WiFi.status() != WL_CONNECTED) {
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

  if (WiFi.status() == WL_CONNECTED) {
    WiFiClient client;
    HTTPClient http;
    Serial.println("Requesting " + url);
    if (http.begin(client, url)) {
      int httpCode = http.GET();
      Serial.println("============== Response code: " + String(httpCode));
      if (httpCode > 0) {
        resp = http.getString();
      } else {
        Serial.println("Failed to get response from server.");
        ESP.restart();
      }
      http.end();
    } else {
      Serial.println("[HTTPS] Unable to connect");
      ESP.restart();
    }
  }

  return resp;
}

void resetTerminal(void) {
  Serial.begin(115200);
  Serial.println();
}

void initScrollingText(void) {
  connectToWiFi();
  
  String toCurrency = "";
  String fromCurrency = "";
  String tradeCSV = GET("http://10.249.11.28:8080/api/prediction/good");
  const char* delims = ",";
  char* s = strdup(tradeCSV.c_str());
  const char* part = strtok(s, delims);
  unsigned int i = 0;
  while (part) {
    switch (i++) {
      case 0:
        fromCurrency = part;
        break;
      case 1:
        toCurrency = part;
        break;
      default:
        break;
    }
    part = strtok(NULL, delims);
  }
  free(s);

  String txt = "The future of " + fromCurrency + "/" + toCurrency + " looks bright.";
  TextFrame frame = {0, (u8g2.getDisplayHeight() - u8g2.getAscent()) / 2, u8g2.getDisplayWidth(), u8g2.getDisplayHeight()};
  if (scrollingLbl)
    delete scrollingLbl;
  scrollingLbl = new ScrollingText(frame, txt);

  if (micros() - lastInteraction >= TIMEOUT)
    lastInteraction = micros();
}

void setup() {
  // put your setup code here, to run once:
  resetTerminal();

  Serial.println("MAC Address: " + WiFi.macAddress());

  pinMode(9, OUTPUT);
  digitalWrite(9, 0);	// default output in I2C mode for the SSD1306 test shield: set the i2c adr to 0

  u8g2.begin();
  u8g2.setFontMode(1);
  u8g2.setFontDirection(0);
  u8g2.setFont(u8g2_font_ncenB14_tr);

  initScrollingText();
}

void loop() {
  // put your main code here, to run repeatedly:
  u8g2.clearBuffer();

  if (!digitalRead(0)) {
    initScrollingText();
  }
  
  if (micros() - lastInteraction < TIMEOUT)
    scrollingLbl->loop();

  u8g2.sendBuffer();
  delay(7);
}
