#include <Arduino.h>
#include <U8g2lib.h>
#include "ScrollingText.h"

extern U8G2_SSD1306_128X32_UNIVISION_F_HW_I2C u8g2;

void ScrollingText::loop() {
  u8g2.setClipWindow(_f.x0, _f.y0, _f.x1, _f.y1);

  const char* txt = _s.c_str();
  constexpr long GAP = 20;

  long windowW = _f.x1 - _f.x0;
  long textW = u8g2.getStrWidth(txt);
  long textH = u8g2.getAscent();
  long scrollPageW = max(textW + GAP, windowW + 1);

  long offset1 = _offset;
  long offset2 = _offset + scrollPageW;

  u8g2.drawStr(_f.x0 + offset1, _f.y0 + textH, txt);
  if (offset2 < windowW)
    u8g2.drawStr(_f.x0 + offset2, _f.y0 + textH, txt);
  
  if (textW > windowW) {
    _offset--;
    if (_offset + textW < 0)
      _offset += scrollPageW;
  }

  u8g2.setMaxClipWindow();
}
