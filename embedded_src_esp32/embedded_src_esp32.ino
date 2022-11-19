#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include "ScrollingText.h"

#include <SPI.h>
#include <TFT_eSPI.h>       // Hardware-specific library

#define S_TO_MICROS 1000000
#define TIMEOUT 30 * S_TO_MICROS

TFT_eSPI tft = TFT_eSPI();

unsigned long lastInteraction = 0;

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
  String prediction = GET("http://10.249.11.28:8080/api/currencies/prediction-string");
  String txt = "The future of " + prediction + " looks bright.";

  Serial.println(txt);

  if (micros() - lastInteraction >= TIMEOUT)
    lastInteraction = micros();
}

void setup() {
  // put your setup code here, to run once:
  resetTerminal();

  Serial.println("MAC Address: " + WiFi.macAddress());

  tft.begin();
  tft.setRotation(1);
  tft.fillScreen(TFT_GREEN);

  initScrollingText();
}

void loop() {
  // put your main code here, to run repeatedly:

  if (!digitalRead(0)) {
    initScrollingText();
  }
  
  //if (micros() - lastInteraction < TIMEOUT)
    // Do scroll stuff

  delay(7);
}
