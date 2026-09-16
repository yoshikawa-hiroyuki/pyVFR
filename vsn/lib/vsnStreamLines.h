//
// vsnStreamLines
//
#ifndef _VSN_STREAMLINES_H_
#define _VSN_STREAMLINES_H_

#include <deque>
#include "vsn_impl.h"
#include "vsnInterpolate.h"

//----------------------------------------------------------------
// class vnsStreamLines
//----------------------------------------------------------------
class vsnStreamLines {
public:
  vsnStreamLines(int divTime=4, int numSkip=1, int maxPts=1000);
  virtual ~vsnStreamLines();

  int       m_divTime;
  int       m_numSkip;
  int       m_maxPts;
  
  // point array of lines
  struct PTarray {
    int      cnt;
    vector3* x;
    PTarray() : cnt(0), x(NULL) {}
    ~PTarray() {if(x) DeAllocate(x);}
  };

  vsnInterpolate _gus;
  bool           _bound[3];
  VSN::DVec3*    _x0;
  PTarray*       _array;

  double GetIntegrand(const VSN::DVec4 x_i, VSN::DVec3 func);
  int RKG(const double t_step, VSN::DVec4 x_i); // Runge-Kutta-Gill
  int StreamLine(VSN::DVec4 x_i, const int l);
};

#endif // _VSN_STREAMLINES_H_
