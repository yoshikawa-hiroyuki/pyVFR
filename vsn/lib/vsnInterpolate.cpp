//
// vsnInterpolate
//
#include "vsnInterpolate.h"
#include "vsnIsosurf.h"

using namespace std;
using namespace VSN;

//----------------------------------------------------------------
// class vsnInterpolate
//----------------------------------------------------------------

/* constructors / destructor */

vsnInterpolate::vsnInterpolate()
  : m_pGrid2D(NULL), m_pVecd2D(NULL), m_cacheStp2D(-1)
{
  reset();
}

vsnInterpolate::vsnInterpolate(const CES::Vec3<size_t>& dims,
			       const size_t vlen, float* pgd, float* pvd,
			       unsigned char* pmsk, std::deque<float>* mskvl)
  : m_pGrid2D(NULL), m_pVecd2D(NULL), m_cacheStp2D(-1)
{
  (void)setup(dims, vlen, pgd, pvd, -1, pmsk, mskvl);
}

vsnInterpolate::~vsnInterpolate() {
  if ( m_pGrid2D )
    DeAllocate(m_pGrid2D);
  if ( m_pVecd2D )
    DeAllocate(m_pVecd2D);
}


void vsnInterpolate::reset() {
  m_dims = CES::Vec3<size_t>();
  p_grid = NULL;
  p_vecd = NULL;
  p_mask = NULL;
  m_mskvl.clear();
  m_vecLen = 0;
  m_axis1 = Not2D;
}

bool vsnInterpolate::setup(const CES::Vec3<size_t>& dims,
			   const size_t vlen, float* pgd, float* pvd,
			   const int stp2D, unsigned char* pmsk,
			   std::deque<float>* mskvl) {
  reset();
  m_dims = dims;
  p_grid = pgd;
  p_vecd = pvd;
  m_vecLen = vlen;
  if ( pmsk && mskvl ) {
    p_mask = pmsk;
    m_mskvl = *mskvl;
  }

  m_dimsOrg = m_dims;
  if ( m_dims[0] * m_dims[1] * m_dims[2] < 1 ) return false;

  int oneDflg[3] = {0, 0, 0};
  if ( m_dims[0] == 1 ) oneDflg[0] = 1;
  if ( m_dims[1] == 1 ) oneDflg[1] = 1;
  if ( m_dims[2] == 1 ) oneDflg[2] = 1;
  if ( oneDflg[0] + oneDflg[1] + oneDflg[2] != 1 ) return true;

  /* 2D data */
  if ( stp2D != -1 && m_cacheStp2D == stp2D ) {
    p_grid = m_pGrid2D;
    p_vecd = m_pVecd2D;
    if ( oneDflg[0] )      {m_axis1 = XAxis; m_dims[0] = 2;}
    else if ( oneDflg[1] ) {m_axis1 = YAxis; m_dims[1] = 2;}
    else if ( oneDflg[2] ) {m_axis1 = ZAxis; m_dims[2] = 2;}
    return true;
  }

  // allocate local data
  if ( ! pgd ) return false;
  size_t dimSz = m_dims[0] * m_dims[1] * m_dims[2] * 2;
  m_pGrid2D = (float*)ReAllocate(m_pGrid2D, dimSz * sizeof(float) * 3);
  if ( ! m_pGrid2D ) return false;
  p_grid = m_pGrid2D;

  if ( vlen > 0 && pvd ) {
    m_pVecd2D = (float*)ReAllocate(m_pVecd2D, dimSz * sizeof(float) * vlen);
    if ( ! m_pVecd2D ) return false;
    p_vecd = m_pVecd2D;
  }

  // copy grid and datas
  int i, j, k, l;
  if ( oneDflg[0] ) {
    m_axis1 = XAxis; m_dims[0] = 2;
    for ( k = 0; k < m_dims[2]; k++ )
      for ( j = 0; j < m_dims[1]; j++ )
	for ( i = 0; i < m_dims[0]; i++ ) {
	  m_pGrid2D[3*(m_dims[0]*m_dims[1]*k +m_dims[0]*j +i) +0]
	    = pgd[3*(m_dimsOrg[0]*m_dimsOrg[1]*k +m_dimsOrg[0]*j +0) +0]
	    + i - 0.5f;
	  m_pGrid2D[3*(m_dims[0]*m_dims[1]*k +m_dims[0]*j +i) +1]
	    = pgd[3*(m_dimsOrg[0]*m_dimsOrg[1]*k +m_dimsOrg[0]*j +0) +1];
	  m_pGrid2D[3*(m_dims[0]*m_dims[1]*k +m_dims[0]*j +i) +2]
	    = pgd[3*(m_dimsOrg[0]*m_dimsOrg[1]*k +m_dimsOrg[0]*j +0) +2];
	} // end of for(i)
    if ( m_pVecd2D )
      for ( k = 0; k < m_dims[2]; k++ )
	for ( j = 0; j < m_dims[1]; j++ )
	  for ( i = 0; i < m_dims[0]; i++ ) {
	    if ( p_mask &&
		 p_mask[m_dimsOrg[0]*m_dimsOrg[1]*k +m_dimsOrg[0]*j +0] ) {
	      for ( l = 0; l < vlen; l++ )
		m_pVecd2D[vlen*(m_dims[0]*m_dims[1]*k +m_dims[0]*j +i) +l]
		  = m_mskvl[l];
	    } else {
	      memcpy(&m_pVecd2D[vlen*(m_dims[0]*m_dims[1]*k+m_dims[0]*j+i)],
		     &pvd[vlen*(m_dimsOrg[0]*m_dimsOrg[1]*k+m_dimsOrg[0]*j+0)],
		     sizeof(float)*vlen);
	    }
	  } // end of for(i)
  }
  else if ( oneDflg[1] ) {
    m_axis1 = YAxis; m_dims[1] = 2;
    for ( k = 0; k < m_dims[2]; k++ )
      for ( j = 0; j < m_dims[1]; j++ )
	for ( i = 0; i < m_dims[0]; i++ ) {
	  m_pGrid2D[3*(m_dims[0]*m_dims[1]*k +m_dims[0]*j +i) +0]
	    = pgd[3*(m_dimsOrg[0]*m_dimsOrg[1]*k +m_dimsOrg[0]*0 +i) +0];
	  m_pGrid2D[3*(m_dims[0]*m_dims[1]*k +m_dims[0]*j +i) +1]
	    = pgd[3*(m_dimsOrg[0]*m_dimsOrg[1]*k +m_dimsOrg[0]*0 +i) +1]
	    + j - 0.5;
	  m_pGrid2D[3*(m_dims[0]*m_dims[1]*k +m_dims[0]*j +i) +2]
	    = pgd[3*(m_dimsOrg[0]*m_dimsOrg[1]*k +m_dimsOrg[0]*0 +i) +2];
	} // end of for(i)
    if ( m_pVecd2D )
      for ( k = 0; k < m_dims[2]; k++ )
	for ( j = 0; j < m_dims[1]; j++ )
	  for ( i = 0; i < m_dims[0]; i++ ) {
	    if ( p_mask &&
		 p_mask[m_dimsOrg[0]*m_dimsOrg[1]*k +m_dimsOrg[0]*0 +i] ) {
	      for ( l = 0; l < vlen; l++ )
		m_pVecd2D[vlen*(m_dims[0]*m_dims[1]*k +m_dims[0]*j +i) +l]
		  = m_mskvl[l];
	    } else {
	      memcpy(&m_pVecd2D[vlen*(m_dims[0]*m_dims[1]*k+m_dims[0]*j+i)],
		     &pvd[vlen*(m_dimsOrg[0]*m_dimsOrg[1]*k+m_dimsOrg[0]*0+i)],
		     sizeof(float)*vlen);
	    }
	  } // end of for(i)
  }
  else if ( oneDflg[2] ) {
    m_axis1 = ZAxis; m_dims[2] = 2;
    for ( k = 0; k < m_dims[2]; k++ )
      for ( j = 0; j < m_dims[1]; j++ )
	for ( i = 0; i < m_dims[0]; i++ ) {
	  m_pGrid2D[3*(m_dims[0]*m_dims[1]*k +m_dims[0]*j +i) + 0]
	    = pgd[3*(m_dimsOrg[0]*m_dimsOrg[1]*0 +m_dimsOrg[0]*j +i) +0];
	  m_pGrid2D[3*(m_dims[0]*m_dims[1]*k +m_dims[0]*j +i) + 1]
	    = pgd[3*(m_dimsOrg[0]*m_dimsOrg[1]*0 +m_dimsOrg[0]*j +i) +1];
	  m_pGrid2D[3*(m_dims[0]*m_dims[1]*k +m_dims[0]*j +i) + 2]
	    = pgd[3*(m_dimsOrg[0]*m_dimsOrg[1]*0 +m_dimsOrg[0]*j +i) +2]
	    + k - 0.5f;
	} // end of for(i)
    if ( m_pVecd2D )
      for ( k = 0; k < m_dims[2]; k++ )
	for ( j = 0; j < m_dims[1]; j++ )
	  for ( i = 0; i < m_dims[0]; i++ ) {
	    if ( p_mask &&
		 p_mask[m_dimsOrg[0]*m_dimsOrg[1]*0 +m_dimsOrg[0]*j +i] ) {
	      for ( l = 0; l < vlen; l++ )
		m_pVecd2D[vlen*(m_dims[0]*m_dims[1]*k +m_dims[0]*j +i) +l]
		  = m_mskvl[l];
	    } else {
	      memcpy(&m_pVecd2D[vlen*(m_dims[0]*m_dims[1]*k+m_dims[0]*j+i)],
		     &pvd[vlen*(m_dimsOrg[0]*m_dimsOrg[1]*0+m_dimsOrg[0]*j+i)],
		     sizeof(float)*vlen);
	    }
	  } // end of for(i)
  }

  m_cacheStp2D = stp2D;
  return true;
}


/* methods */

void vsnInterpolate::MatrixGradient(const VSN::DVec4 x_i, VSN::DMat3 g) {
  int ixi[3] = {int(x_i[0]), int(x_i[1]), int(x_i[2])};
  DVec4 x_I[6] = {double(ixi[0]), x_i[1], x_i[2], x_i[3],
                  double(ixi[0] + 1), x_i[1], x_i[2], x_i[3],
                  x_i[0], double(ixi[1]), x_i[2], x_i[3],
                  x_i[0], double(ixi[1] + 1), x_i[2], x_i[3],
                  x_i[0], x_i[1], double(ixi[2]), x_i[3],
                  x_i[0], x_i[1], double(ixi[2] + 1), x_i[3]};
  int n;
  for ( n = 0; n < 3; n++ )
    if ( int(x_i[n]) == m_dims[n] - 1) { // shift for upper boundary
      x_I[2*n][n] -= 1.0;
      x_I[2*n+1][n] -= 1.0;
    }

  DVec3 x[6];
  for ( n = 0; n < 6; n++ )
    InterpolateCoord(x_I[n], x[n]);

  for ( n = 0; n < 3; n++ ) {
    g[n][0] = x[1][n] - x[0][n];
    g[n][1] = x[3][n] - x[2][n];
    g[n][2] = x[5][n] - x[4][n];
  }
}

double vsnInterpolate::MatrixInverse(const VSN::DVec4 x_i, VSN::DMat3 m) {
  DMat3 g;
  MatrixGradient(x_i, g);

  double J = (g[0][0]*g[1][1]*g[2][2] +
	      g[0][1]*g[1][2]*g[2][0] +
	      g[0][2]*g[1][0]*g[2][1] -
	      g[0][0]*g[1][2]*g[2][1] -
	      g[0][1]*g[1][0]*g[2][2] -
	      g[0][2]*g[1][1]*g[2][0]);
  if ( ! J ) return 0.0;

  m[0][0] =   (g[1][1]*g[2][2] - g[1][2]*g[2][1]) / J;
  m[1][0] = - (g[1][0]*g[2][2] - g[1][2]*g[2][0]) / J;
  m[2][0] =   (g[1][0]*g[2][1] - g[1][1]*g[2][0]) / J;
  m[0][1] = - (g[0][1]*g[2][2] - g[0][2]*g[2][1]) / J;
  m[1][1] =   (g[0][0]*g[2][2] - g[0][2]*g[2][0]) / J;
  m[2][1] = - (g[0][0]*g[2][1] - g[0][1]*g[2][0]) / J;
  m[0][2] =   (g[0][1]*g[1][2] - g[0][2]*g[1][1]) / J;
  m[1][2] = - (g[0][0]*g[1][2] - g[0][2]*g[1][0]) / J;
  m[2][2] =   (g[0][0]*g[1][1] - g[0][1]*g[1][0]) / J;

  return J;
}

int vsnInterpolate::NewtonRapson(const VSN::DVec3 x, VSN::DVec4 x_i,
				 const double eps)
{
  int n, iter = 0;

  for ( int n_throw = 0; n_throw < 5 && iter < 100; ) {
    DVec3 dx;
    InterpolateCoord(x_i, dx);
    for ( n = 0; n < 3; n++ ) dx[n] -= x[n];

    double norm = sqrt(dx[0]*dx[0] + dx[1]*dx[1] + dx[2]*dx[2]);
    if ( norm < eps )
      return 1;

    DMat3 m;
    if ( ! MatrixInverse(x_i, m) ) break;
    for ( n = 0; n < 3; n++ )
      x_i[n] -= m[n][0]*dx[0] + m[n][1]*dx[1] + m[n][2]*dx[2];

    for ( n = 0; n < 3; n++ ) {
      double upper = double(m_dims[n] - 1);
      if (x_i[n] - upper < 1e-1 && x_i[n] - upper > 0.0 ) {
        // 1e-1 is empirical value.
        x_i[n] = upper;
        n_throw++; // throw back to the field edge.
      }
      else if ( x_i[n] > -1e-1 && x_i[n] < 0.0 ) {
        x_i[n] = 0.0;
        n_throw++;
      }
      if ( x_i[n] < 0.0 || x_i[n] > upper ) {
        n_throw = 999;
        break;    // it's ok, initial condition is out of range.
      }
    }
    iter++;
  }
  return -1;
}

int vsnInterpolate::ConvXtoI(const VSN::DVec3 x, VSN::DVec4 x_i) {
  int prec = -1;
  int i, j, k;

  x_i[3] = 0.0;

  for ( i = 0; i < 3; i++ )
    if ( fabs(x[i]) > 1e-6 )
      if ( floor(log10(fabs(x[i]))) > prec )
        prec = (int)floor(log10(fabs(x[i])));
  double eps = pow(10.0, prec - 5);

  for ( k = 0; k < m_dims[2] - 1; k++ )
    for ( j = 0; j < m_dims[1] - 1; j++ )
      for ( i = 0; i < m_dims[0] - 1; i++ ) {
        x_i[0] = i + 0.5;
        x_i[1] = j + 0.5;
        x_i[2] = k + 0.5;

        if ( NewtonRapson(x, x_i, eps) > 0 )
          return 1;
      } // end of for(i)

  return -1;
}

// static interface
deque<vsnInterpolate*> vsnInterpolate::s_pobj_list;

vsnInterpolate* vsnInterpolate::GetInterpolator(const vsnInterpolate* p) {
  if ( ! p ) { // allocate a new interpolator
    vsnInterpolate* np = new vsnInterpolate();
    if ( ! np )
      return NULL;
    s_pobj_list.push_back(np);
    return np;
  } else { // search p
    auto it = find(s_pobj_list.begin(), s_pobj_list.end(), p);
    if ( it != s_pobj_list.end() )
      return (*it);
    else
      return NULL;
  }
}

bool vsnInterpolate::DestroyInterpolater(vsnInterpolate* p) {
  if ( ! p ) return true;
  auto it = find(s_pobj_list.begin(), s_pobj_list.end(), p);
  if ( it == s_pobj_list.end() ) // not found
    return false;
  // found, remove and destroy
  s_pobj_list.erase(it);
  delete p;
  return true;
}


//------------------------------------------------------------------------
// interfaces for ctypes
//------------------------------------------------------------------------

VFR_API void* CreateInterpolator()
{
  vsnInterpolate* p = vsnInterpolate::GetInterpolator(NULL);
  return (void*)p;
}

VFR_API VFR_BOOL InterpolatorSetup(void* p,
				   const size_t dims[3], const size_t vlen,
				   float* pgd, float* pvd, const int stp2D)
{
  vsnInterpolate* pIntp = static_cast<vsnInterpolate*>(p);
  if ( ! pIntp )
    return VFR_FALSE;
  if ( ! pIntp->setup(dims, vlen, pgd, pvd, stp2D) )
    return VFR_FALSE;
  return VFR_TRUE;
}

VFR_API VFR_BOOL InterpolatorConvXtoI(void* p,
				      const double x[3], double x_i[4])
{
  vsnInterpolate* pIntp = static_cast<vsnInterpolate*>(p);
  if ( ! pIntp )
    return VFR_FALSE;
  if ( pIntp->ConvXtoI(x, x_i) < 0 )
    return VFR_FALSE;
  else
    return VFR_TRUE;
}

VFR_API double InterpolatorMatrixInverse(void* p,
					 const double x_i[4],
					 double m[3][3]) {
  vsnInterpolate* pIntp = static_cast<vsnInterpolate*>(p);
  if ( ! pIntp )
    return 0.0;

  return pIntp->MatrixInverse(x_i, m);
}

VFR_API VFR_BOOL InterpolateCoordS(void* p,
				   const double x_I[3],
				   float x[3]) {
  vsnInterpolate* pIntp = static_cast<vsnInterpolate*>(p);
  if ( ! pIntp )
    return VFR_FALSE;

  if ( ! pIntp->InterpolateCoord(x_I, x) )
    return VFR_FALSE;
  else
    return VFR_TRUE;
}

VFR_API VFR_BOOL InterpolateCoordD(void* p,
				   const double x_I[3],
				   double x[3]) {
  vsnInterpolate* pIntp = static_cast<vsnInterpolate*>(p);
  if ( ! pIntp )
    return VFR_FALSE;

  if ( ! pIntp->InterpolateCoord(x_I, x) )
    return VFR_FALSE;
  else
    return VFR_TRUE;
}

VFR_API VFR_BOOL InterpolateData1S(void* p,
				   const double x_I[3],
				   const size_t didx,
				   float* dval) {
  vsnInterpolate* pIntp = static_cast<vsnInterpolate*>(p);
  if ( ! pIntp )
    return VFR_FALSE;

  if ( ! pIntp->InterpolateData(x_I, didx, *dval) )
    return VFR_FALSE;

  return VFR_TRUE;
}

VFR_API VFR_BOOL InterpolateData1D(void* p,
				   const double x_I[3],
				   const size_t didx,
				   double* dval) {
  vsnInterpolate* pIntp = static_cast<vsnInterpolate*>(p);
  if ( ! pIntp )
    return VFR_FALSE;

  if ( ! pIntp->InterpolateData(x_I, didx, *dval) )
    return VFR_FALSE;

  return VFR_TRUE;
}

VFR_API VFR_BOOL InterpolateData3S(void* p,
				   const double x_I[3],
				   float dval[3]) {
  vsnInterpolate* pIntp = static_cast<vsnInterpolate*>(p);
  if ( ! pIntp )
    return VFR_FALSE;

  if ( ! pIntp->InterpolateData(x_I, CES::Vec3<size_t>(0, 1, 2), dval) )
    return VFR_FALSE;

  return VFR_TRUE;
}

VFR_API VFR_BOOL InterpolateData3D(void* p,
				   const double x_I[3],
				   double dval[3]) {
  vsnInterpolate* pIntp = static_cast<vsnInterpolate*>(p);
  if ( ! pIntp )
    return VFR_FALSE;

  if ( ! pIntp->InterpolateData(x_I, CES::Vec3<size_t>(0, 1, 2), dval) )
    return VFR_FALSE;

  return VFR_TRUE;
}

VFR_API VFR_BOOL DeleteInterpolator(void* p)
{
  vsnInterpolate* pIntp = static_cast<vsnInterpolate*>(p);
  if ( ! pIntp )
    return VFR_FALSE;
  if ( ! vsnInterpolate::DestroyInterpolater(pIntp) )
    return VFR_FALSE;
  return VFR_TRUE;
}
