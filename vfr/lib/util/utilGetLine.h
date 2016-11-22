#ifndef _UTIL_GET_LINE_H_
#define _UTIL_GET_LINE_H_

#include <iostream>
#include <string>
#include <string.h>


namespace CES {
  inline void GetLine(std::istream& is, std::string& buff) {
    char c;
    const char dcs[] = "\n\r";
    buff = "";
    while ( is.get(c) && ! strchr(dcs, c) )
      buff.push_back(c);
    while ( is.get(c) && strchr(dcs, c) )
      ;
    if ( is.good() ) is.putback(c);
  }

  inline void GetLine(std::istream& is, char* p, const int n) {
    char c;
    const char dcs[] = "\n\r";
    register size_t i = 0;
    if ( ! p || n < 1 ) return;
    memset(p, 0, n);
    while ( i < n-1 && is.get(c) && ! strchr(dcs, c) ) {
      *p++ = c;
      i++;
    }
    while ( is.get(c) && strchr(dcs, c) )
      ;
    if ( is.good() ) is.putback(c);    
  }
};

#endif // _UTIL_GET_LINE_H_
