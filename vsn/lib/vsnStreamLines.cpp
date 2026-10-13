//
// vsnStreamLines
//
#include "gfx_impl.h"

#include "vsnStreamLines.h"

using namespace std;
using namespace VSN;

#define SQR(x) ((x)*(x))


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

double vsnStreamLines::GetIntegrand(const DVec4 x_i, DVec3 func,
				    VSN::DVec3* resV)
{
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

  if ( resV ) {
    (*resV)[0] = v[0];
    (*resV)[1] = v[1];
    (*resV)[2] = v[2];
  }

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
    DVec3 func, resV;
    double t_step = GetIntegrand(x_i, func, &resV);
    if ( ! t_step ) return 0;

    if ( RKG(t_step, x_i) < 0 )
      return it; // if return value is negative, the particle is out of range.

    if ( ! ((it+1)%m_numSkip) ) {
      _gus.InterpolateCoord(x_i, _array[l].x[_array[l].cnt]);
      _array[l].x[_array[l].cnt][3]
	= sqrt(SQR(resV[0])+SQR(resV[1])+SQR(resV[2]));
      _array[l].cnt++;
    }
  }
  return it;
}


//------------------------------------------------------------------------
// interfaces for ctypes
//------------------------------------------------------------------------

VFR_API void* CreateStreamLineObj(int divTime, int numSkip, int maxPts)
{
  vsnStreamLines* p = new vsnStreamLines(divTime, numSkip, maxPts);
  return (void*)p;
}

VFR_API VFR_BOOL DeleteStreamLineObj(void* p)
{
  vsnStreamLines* psl = static_cast<vsnStreamLines*>(p);
  if ( ! psl )
    return VFR_FALSE;
  delete psl;
  return VFR_TRUE;
}

VFR_API VFR_BOOL CalcStreamLines(void* p, void *q,
				 const size_t ns, const vector3* samplePts,
				 const size_t dims[3],
				 vector3* coord, float* data,
				 const int reqCol)
{
  vsnStreamLines* psl = static_cast<vsnStreamLines*>(p);
  ObjData* po = static_cast<ObjData*>(q);
  if ( ! psl || ! po ) return VFR_FALSE;
  int i, l;

  // alloc _x0
  psl->_x0 = (DVec3*)ReAllocate(psl->_x0, sizeof(DVec3)*ns);
  if ( ! psl->_x0 )
    return VFR_FALSE;
  for ( i = 0; i < ns; i++ ) {
    psl->_x0[i][0] = (double)samplePts[i][0];
    psl->_x0[i][1] = (double)samplePts[i][1];
    psl->_x0[i][2] = (double)samplePts[i][2];
  }

  // alloc _array
  if ( psl->_array ) delete [] psl->_array;
  psl->_array = new vsnStreamLines::PTarray[ns];
  if ( ! psl->_array )
    return VFR_FALSE;
  for ( i = 0; i < ns; i++ ) {
    psl->_array[i].x = (vector4*)Allocate(sizeof(vector4) * psl->m_maxPts);
    memset(psl->_array[i].x, 0, sizeof(vector4) * psl->m_maxPts);
  }

  // set data/coord to _gus
  if ( ! psl->_gus.setup(CES::Vec3<size_t>(dims), 3, (float*)coord, data) )
    return VFR_FALSE;
  size_t dimSz = psl->_gus.m_dims[0]* psl->_gus.m_dims[1]* psl->_gus.m_dims[2];

  // calculate bbox
  CES::Vec3<float> pbb[2];
  vsnInterpolate::CalcBBox(CES::Vec3<size_t>(dims), (float*)coord, pbb);

  // calculate streamlines
  DVec4 x_i;
  size_t num_pts = 0;
  for ( l = 0; l < ns; l++ ) {
    // pre-check using bbox
    if ( ! psl->_gus.is2D() &&
	 (psl->_x0[l][0] < pbb[0].m_v[0] || psl->_x0[l][0] > pbb[1].m_v[0] ||
          psl->_x0[l][1] < pbb[0].m_v[1] || psl->_x0[l][1] > pbb[1].m_v[1] ||
          psl->_x0[l][2] < pbb[0].m_v[2] || psl->_x0[l][2] > pbb[1].m_v[2]) )
      continue;

    if ( psl->_gus.ConvXtoI(psl->_x0[l], x_i) < 0 )
      continue;

    psl->_gus.InterpolateCoord(x_i, psl->_array[l].x[0]);
    psl->_array[l].cnt++;

    x_i[3] = 0.0;
    psl->StreamLine(x_i, l);
    num_pts += psl->_array[l].cnt;
  } // end of for(l)

  // alloc lines data in po
  if ( ! po->alcVerts(num_pts) || ! po->alcIndices(ns) )
    return VFR_FALSE;
  vector3* vl = po->_verts;
  int* il = po->_indices;
  vector4* cl = NULL;
  if ( reqCol == 2 ) { // Col_Velo
    if ( ! po->alcColors(num_pts) )
      return VFR_FALSE;
    cl = po->_colors;
  } else if ( reqCol == 1 ) { // Col_SmplPt
    if ( ! po->alcColors(ns) )
      return VFR_FALSE;
    cl = po->_colors;
  }
  
  int idx = 0, cidx = 0;
  for ( l = 0; l < ns; l++ ) {
    // set vertex
    for ( i = 0; i < psl->_array[l].cnt; i++ ) {
      vl[idx][0] = psl->_array[l].x[i][0];
      vl[idx][1] = psl->_array[l].x[i][1];
      vl[idx][2] = psl->_array[l].x[i][2];
      idx++;
    } // end of for(i)

    // indices
    il[l] = psl->_array[l].cnt;

    // colors
    // |v| is passed from _array[l].x[i][3] to _colors[j][4]
    if ( reqCol == 2 && cl ) {
      for ( i = 0; i < psl->_array[l].cnt; i++ ) {
	cl[cidx][3] = psl->_array[l].x[i][3];
	cidx++;
      } // end of for(i)
    }
  } // end of for(l)

  return VFR_TRUE;
}
