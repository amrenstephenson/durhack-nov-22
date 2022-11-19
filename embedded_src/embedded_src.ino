#include <Arduino.h>
#include <U8g2lib.h>
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>
#include "ScrollingText.h"

#ifdef U8X8_HAVE_HW_SPI
#include <SPI.h>
#endif
#ifdef U8X8_HAVE_HW_I2C
#include <Wire.h>
#endif

U8G2_SSD1306_128X32_UNIVISION_F_HW_I2C u8g2(U8G2_R0, /* reset=*/ 16, /* clock=*/ SCL, /* data=*/ SDA);   // pin remapping with ESP8266 HW I2C

ScrollingText* helloWorld;

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

void setup() {
  // put your setup code here, to run once:
  resetTerminal();

  Serial.println("MAC Address: " + WiFi.macAddress());
  connectToWiFi();
  String prediction = GET("http://10.249.11.28:8080/api/currencies/prediction-string");

  pinMode(9, OUTPUT);
  digitalWrite(9, 0);	// default output in I2C mode for the SSD1306 test shield: set the i2c adr to 0

  String txt = "The future of " + prediction + " looks bright.";
  helloWorld = new ScrollingText({0, 0, u8g2.getDisplayWidth(), u8g2.getDisplayHeight()}, txt);

  Serial.println("Beginning display");

  u8g2.begin();
}

void loop() {
  // put your main code here, to run repeatedly:
  u8g2.clearBuffer();
  u8g2.setFontMode(1);
  u8g2.setFontDirection(0);
  u8g2.setFont(u8g2_font_ncenB14_tr);
  
  helloWorld->loop();

  u8g2.sendBuffer();
  delay(10);
}
