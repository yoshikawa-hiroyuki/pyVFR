//
// vsnInterpolate
//
#ifndef _VSN_INTERPOLATE_H_
#define _VSN_INTERPOLATE_H_

#include <deque>
#include "obj_impl.h"

namespace VSN {
  // double vertex type
  typedef double DVec3[3];
  typedef double DVec4[4];
  typedef double DMat3[3][3];
};

//----------------------------------------------------------------
// class vsnInterpolate
//----------------------------------------------------------------
class vsnInterpolate {
public:
  enum Axis1Type {Not2D =-1, XAxis =0, YAxis =1, ZAxis =2};

  CES::Vec3<size_t> m_dims;
  float*            p_grid;
  float*            p_vecd;
  size_t            m_vecLen;
  unsigned char*    p_mask;
  std::deque<float> m_mskvl;

  vsnInterpolate();
  vsnInterpolate(const CES::Vec3<size_t>& dims, const size_t vlen,
		 float* pgd, float* pvd, unsigned char* pmsk =NULL,
		 std::deque<float>* mskvl =NULL);
  ~vsnInterpolate();

  void reset();
  bool setup(const CES::Vec3<size_t>& dims, const size_t vlen,
	     float* pgd, float* pvd, const int stp2D =-1,
	     unsigned char* pmsk =NULL, std::deque<float>* mskvl =NULL);

  template<class T> bool InterpolateCoord(const VSN::DVec3 x_I, T x[3]);
  template<class T> bool InterpolateData(const VSN::DVec3 x_I,
					 const CES::Vec3<size_t>& didx,
					 T dval[3]);
  template<class T> bool InterpolateData(const VSN::DVec3 x_I,
					 const size_t dkind, T& x);

  void MatrixGradient(const VSN::DVec4 x_i, VSN::DMat3 g);
  double MatrixInverse(const VSN::DVec4 x_i, VSN::DMat3 m);
  int NewtonRapson(const VSN::DVec3 x, VSN::DVec4 x_i, const double eps);
  int ConvXtoI(const VSN::DVec3 x, VSN::DVec4 x_i);

  bool is2D() const {return (m_axis1 != Not2D);}
  Axis1Type getAxis1() const {return m_axis1;}

  // static interface
  static vsnInterpolate* GetInterpolator(const vsnInterpolate* p);
  static bool DestroyInterpolater(vsnInterpolate* p);

private:
  CES::Vec3<size_t> m_dimsOrg;
  float*            m_pGrid2D;
  float*            m_pVecd2D;
  Axis1Type         m_axis1;
  mutable int       m_cacheStp2D;

  static std::deque<vsnInterpolate*> s_pobj_list;
};


#define IDX3(d,i,j,k,l) \
(( (k)*(d)[1]*(d)[0] + (j)*(d)[0] + (i) )*3 + (l))
#define IDXV(d,i,j,k,l) \
(( (k)*(d)[1]*(d)[0] + (j)*(d)[0] + (i) )*m_vecLen +(l))
#define IDXM(d,i,j,k) \
( (k)*(d)[1]*(d)[0] + (j)*(d)[0] + (i) )


template<class T> inline bool
vsnInterpolate::InterpolateCoord(const VSN::DVec3 x_I, T x[3]) {
  if ( ! p_grid ) return false;

  double X[8];
  int i = int(x_I[0]);
  int j = int(x_I[1]);
  int k = int(x_I[2]);
  double ip = x_I[0] - double(i);
  double jp = x_I[1] - double(j);
  double kp = x_I[2] - double(k);
  double im = 1.0 - ip;
  double jm = 1.0 - jp;
  double km = 1.0 - kp;

  int n;
  for ( n = 0; n < 3; n++ ) {
    X[0] = double(p_grid[IDX3(m_dims,i,j,k,n)]); // (i,  j,  k  )
    if ( ip ) i++;
    X[1] = double(p_grid[IDX3(m_dims,i,j,k,n)]); // (i+1,j,  k  )
    if ( jp ) j++;
    X[2] = double(p_grid[IDX3(m_dims,i,j,k,n)]); // (i+1,j+1,k  )
    if ( ip ) i--;
    X[3] = double(p_grid[IDX3(m_dims,i,j,k,n)]); // (i,  j+1,k  )
    if ( kp ) k++;
    X[7] = double(p_grid[IDX3(m_dims,i,j,k,n)]); // (i,  j+1,k+1)
    if ( ip ) i++;
    X[6] = double(p_grid[IDX3(m_dims,i,j,k,n)]); // (i+1,j+1,k+1)
    if ( jp ) j--;
    X[5] = double(p_grid[IDX3(m_dims,i,j,k,n)]); // (i+1,j  ,k+1)
    if ( ip ) i--;
    X[4] = double(p_grid[IDX3(m_dims,i,j,k,n)]); // (i,  j,  k+1)
    if ( kp ) k--;
    x[n] = (T)(im*jm*km*X[0] + ip*jm*km*X[1] + ip*jp*km*X[2] + im*jp*km*X[3] +
               im*jm*kp*X[4] + ip*jm*kp*X[5] + ip*jp*kp*X[6] + im*jp*kp*X[7]);
  }
  return true;
}

template<class T> inline bool
vsnInterpolate::InterpolateData(const VSN::DVec3 x_I,
				const CES::Vec3<size_t>& didx, T dval[3])
{
  if ( p_mask &&
       p_mask[IDXM(m_dims, int(x_I[0]), int(x_I[1]), int(x_I[2]))] ) {
    dval[0] = dval[1] = dval[2] = (T)0;
    return true;
  }
  if ( ! InterpolateData(x_I, didx[0], dval[0]) ) return false;
  if ( ! InterpolateData(x_I, didx[1], dval[1]) ) return false;
  if ( didx[2] < 0  && is2D() ) {
    dval[2] = 0.0;
  } else {
    if ( ! InterpolateData(x_I, didx[2], dval[2]) ) return false;
  }
  return true;
}

template<class T> inline bool
vsnInterpolate::InterpolateData(const VSN::DVec3 x_I,
				const size_t dkind, T& dval)
{
  if ( ! p_vecd ) return false;
  if ( m_vecLen <= dkind ) return false;

  double X[8];
  int i = int(x_I[0]);
  int j = int(x_I[1]);
  int k = int(x_I[2]);
  double ip = x_I[0] - double(i);
  double jp = x_I[1] - double(j);
  double kp = x_I[2] - double(k);
  double im = 1.0 - ip;
  double jm = 1.0 - jp;
  double km = 1.0 - kp;

  if ( p_mask ) {
    X[0] = p_mask[IDXM(m_dims,i,j,k)] ? m_mskvl[dkind] :
      double(p_vecd[IDXV(m_dims,i,j,k,dkind)]); // (i,  j,  k  )
    if ( ip ) i++;
    X[1] = p_mask[IDXM(m_dims,i,j,k)] ? m_mskvl[dkind] :
      double(p_vecd[IDXV(m_dims,i,j,k,dkind)]); // (i+1,j,  k  )
    if ( jp ) j++;
    X[2] = p_mask[IDXM(m_dims,i,j,k)] ? m_mskvl[dkind] :
      double(p_vecd[IDXV(m_dims,i,j,k,dkind)]); // (i+1,j+1,k  )
    if ( ip ) i--;
    X[3] = p_mask[IDXM(m_dims,i,j,k)] ? m_mskvl[dkind] :
      double(p_vecd[IDXV(m_dims,i,j,k,dkind)]); // (i,  j+1,k  )
    if ( kp ) k++;
    X[7] = p_mask[IDXM(m_dims,i,j,k)] ? m_mskvl[dkind] :
      double(p_vecd[IDXV(m_dims,i,j,k,dkind)]); // (i,  j+1,k+1)
    if ( ip ) i++;
    X[6] = p_mask[IDXM(m_dims,i,j,k)] ? m_mskvl[dkind] :
      double(p_vecd[IDXV(m_dims,i,j,k,dkind)]); // (i+1,j+1,k+1)
    if ( jp ) j--;
    X[5] = p_mask[IDXM(m_dims,i,j,k)] ? m_mskvl[dkind] :
      double(p_vecd[IDXV(m_dims,i,j,k,dkind)]); // (i+1,j  ,k+1)
    if ( ip ) i--;
    X[4] = p_mask[IDXM(m_dims,i,j,k)] ? m_mskvl[dkind] :
      double(p_vecd[IDXV(m_dims,i,j,k,dkind)]); // (i,  j,  k+1)
    if ( kp ) k--;
  }
  else {
    X[0] = double(p_vecd[IDXV(m_dims,i,j,k,dkind)]); // (i,  j,  k  )
    if ( ip ) i++;
    X[1] = double(p_vecd[IDXV(m_dims,i,j,k,dkind)]); // (i+1,j,  k  )
    if ( jp ) j++;
    X[2] = double(p_vecd[IDXV(m_dims,i,j,k,dkind)]); // (i+1,j+1,k  )
    if ( ip ) i--;
    X[3] = double(p_vecd[IDXV(m_dims,i,j,k,dkind)]); // (i,  j+1,k  )
    if ( kp ) k++;
    X[7] = double(p_vecd[IDXV(m_dims,i,j,k,dkind)]); // (i,  j+1,k+1)
    if ( ip ) i++;
    X[6] = double(p_vecd[IDXV(m_dims,i,j,k,dkind)]); // (i+1,j+1,k+1)
    if ( jp ) j--;
    X[5] = double(p_vecd[IDXV(m_dims,i,j,k,dkind)]); // (i+1,j  ,k+1)
    if ( ip ) i--;
    X[4] = double(p_vecd[IDXV(m_dims,i,j,k,dkind)]); // (i,  j,  k+1)
    if ( kp ) k--;
  }

  dval = (T)(im*jm*km*X[0] + ip*jm*km*X[1] + ip*jp*km*X[2] + im*jp*km*X[3] +
	     im*jm*kp*X[4] + ip*jm*kp*X[5] + ip*jp*kp*X[6] + im*jp*kp*X[7]);
  return true;
}

#undef IDX3
#undef IDXV
#undef IDXM

#endif // _VSN_INTERPLATE_H_

