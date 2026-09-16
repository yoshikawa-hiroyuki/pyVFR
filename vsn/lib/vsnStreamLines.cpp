//
// vsnStreamLines
//
#include "vsnStreamLines.h"

using namespace std;
using namespace VSN;

//----------------------------------------------------------------
// class vsnStreamLines
//----------------------------------------------------------------

/* constructors / destructor */

vsnStreamLines::vsnStreamLines(int divTime, int numSkip, int maxPts)
  : m_divTime(divTime), m_numSkip(numSkip), m_maxPts(maxPts)
{
  _bound[0] = _bound[1] = _bound[2] = false;
  _x0 = NULL;
  _array = NULL;
}

vsnStreamLines::~vsnStreamLines() {
  if ( _x0 ) DeAllocate(_x0);
  if ( _array ) delete [] _array;
}

/* internal method for make stream lines */

double vsnStreamLines::GetIntegrand(const DVec4 x_i, DVec3 func) {
  double t_step, max = 0.0;

  DMat3 m; DVec3 v;
  size_t vecDataIdx[3] = {0, 1, 2};
  _gus.InterpolateData(x_i, vecDataIdx, v);

  double J = _gus.MatrixInverse(x_i, m);
  if ( ! J ) return 0.0;

  int n;
  for ( n = 0; n < 3; n++ ) {
    func[n] = m[n][0]*v[0] + m[n][1]*v[1] + m[n][2]*v[2];
    if ( fabs(func[n]) > max ) max = fabs(func[n]);
  }

  if ( ! max )
    t_step = 0.0; // in this case, particle of Stream Line never move.
  else
    t_step = 1.0 / max / m_divTime;

  if ( t_step > 1.0 )
    t_step = 1.0; // avoid a stagnation point.

  return t_step;
}

int vsnStreamLines::RKG(const double t_step, DVec4 x_i) {
  DVec3 q = {0.0, 0.0, 0.0};
  static DVec4 ct = {0.0, 0.5, 0.0, 0.5};
  static DVec4 ck = {2.0, 1.0, 1.0, 2.0};
  static DVec4 cx, cq;
  cq[0] = 0.5; cq[1] = 1.0 - sqrt(0.5); cq[2] = 1.0 + sqrt(0.5); cq[3] = 0.5;
  cx[0] = cq[0]; cx[1] = cq[1]; cx[2] = cq[2]; cx[3] = cq[3]/3 ;

  double eps = 1.0e-8;
  DVec3 i_pre = {x_i[0], x_i[1], x_i[2]};

  const int t = int(x_i[3]);

  int l, n;
  for ( l = 0; l < 4; l++ ) {
    // get right-hand part of equation
    DVec3 func;
    if ( ! GetIntegrand(x_i, func) )
      return -1; // it is caused by J = 0 or all func = 0.

    for ( n = 0; n < 3; n++ ) {
      int i_n = int(x_i[n]);

      double k = t_step * func[n];
      double r = cx[l] * (k - ck[l] * q[n]);
      x_i[n] += r;
      q[n] += 3.0 * r - cq[l] * k;

      int sign = int(floor(x_i[n])) - i_n;
      if ( x_i[n] > double(_gus.m_dims[n] - 1) ) {
        // for the case limit to overlimit
        sign = 1; i_n = _gus.m_dims[n] - 2;
      }
      if ( sign ) {
        if ( x_i[n] < 0.0 || x_i[n] > double(_gus.m_dims[n] - 1) ) {
          if ( _bound[n] ) {
            // the particle is saved by periodic boundary.
            if ( x_i[n] < 0.0 )
              x_i[n] += double(_gus.m_dims[n] - 1);
            else if ( x_i[n] > double(_gus.m_dims[n] - 1) )
              x_i[n] -= double(_gus.m_dims[n] - 1);
          }
          else
            return -1; // if it's true, the particle is gone.
        }
      } // end of if(sign)
    } // end of for(n)
  } // end of for(l)

  if ( fabs(x_i[0] - i_pre[0]) < eps &&
       fabs(x_i[1] - i_pre[1]) < eps && fabs(x_i[2] - i_pre[2]) < eps )
    return -2; // drop into a stagnation point.

  return 1;
}

int vsnStreamLines::StreamLine(DVec4 x_i, const int l) {
  int it, end = (m_maxPts - 1) * m_numSkip;
  for ( it = 0; it < end; it++ ) {
    DVec3 func;
    double t_step = GetIntegrand(x_i, func);
    if ( ! t_step ) return 0;

    if ( RKG(t_step, x_i) < 0 )
      return it; // if return value is negative, the particle is out of range.

    if ( ! ((it+1)%m_numSkip) ) {
      _gus.InterpolateCoord(x_i, _array[l].x[_array[l].cnt]);
      _array[l].cnt++;
    }
  }
  return it;
}
