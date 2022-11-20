#ifndef SCROLLING_TEXT_H
#define SCROLLING_TEXT_H

struct TextFrame {
  unsigned x0;
  unsigned y0;
  unsigned x1;
  unsigned y1;
};

class ScrollingText {
protected:
  long _offset = 0;
  TextFrame _f;
  String _s;

public:
  ScrollingText(TextFrame frame, String txt) : _f(frame), _s(txt) {};
  void loop(void);
};

#endif
