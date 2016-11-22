#ifndef _UTIL_TESSEL_H_
#define _UTIL_TESSEL_H_

#include <float.h>
#include <deque>
#include "utilMath.h"

typedef CES::Vec3<float> Vector3F;
typedef CES::Vec3<int>   Vector3I;


class utilTessel {
public:
  enum {convex     =  1,
	degenerate =  0,
	concave    = -1
  };

  utilTessel() {m_nIndex=NULL; m_nMaxPoints=0;}
  virtual ~utilTessel() {if ( m_nIndex ) delete[] m_nIndex;}

  // Tesselation
  std::deque<Vector3I>
  Triangulate(const Vector3F* points, int nCount) {
    std::deque<Vector3I> vtxLst;
    if ( nCount < 3 ) return vtxLst;

    register int i, j, k;
    Vector3F v01 = points[1] - points[0];
    Vector3F normal = v01 ^ (points[2] - points[0]);
    for ( i = 3; i < nCount; i++ ) {
      Vector3F vn = v01 ^ (points[i] - points[0]);
      if ( (normal | normal) < (vn | vn) )
	normal = vn;
    } // end of for(i)
    normal.UnitVec();

    int nVertex = nCount;
    AllocIndex(nCount);
    bool bNoErrors = true;

    while ( nVertex >= 3 && bNoErrors ) {
      // tri to remove one vertex...
      bNoErrors = false;
      for ( i = 0 , j = 1 , k = 2 ; k < nVertex ; ) {
	switch ( TriangleArea(points, m_nIndex[i], m_nIndex[j], m_nIndex[k],
			      normal) ) {
	  // ok. flush face && remove vertex j
	case convex:
	  // Testing containement
	  if ( IsAnyPointInside(points, i, j, k, nVertex) ) {
	    // go ahead..
	    i = j;
	    j = k;
	    k++;
	  } else {
	    vtxLst.push_back(Vector3I(m_nIndex[i], m_nIndex[j], m_nIndex[k]));

	    // remove vertex j
	    nVertex = RemoveVertex(j, nVertex);
	    bNoErrors = true;
	  }
	  break;
	case concave:
	  // go ahead..
	  i = j;
	  j = k;
	  k++;
	  break;
	case degenerate:
	  // remove vertex j
	  nVertex = RemoveVertex(j, nVertex);
	  bNoErrors = true;
	  break;
	} // end of switch
      } // end of for(i,j,k)
    } // end of while

    return vtxLst;
  }

  // Utility Test Polygon Convexity ...
  static bool IsConvex(const Vector3F* points,
		       int nPoints, const Vector3F& normal) {
    Vector3F vi(points[1]); vi = vi - points[0];
    Vector3F vj, n;
    int nP = nPoints - 1;

    register int i, j, k;
    for ( i = 0, j = 1; j < nPoints; i++, j++ ) {
      k  = (j + 1) % nP;
      vj = points[k];
      vj = vj - points[j];
      n = vi ^ vj;
      if ( (n[0]*normal[0]) < 0.0f ||
	   (n[1]*normal[1]) < 0.0f ||
	   (n[2]*normal[2]) < 0.0f ) break;
      vi = vj;
    } // end of for(i, j)
    return ((j == nPoints) ? true : false);
  }

protected:
  int*        m_nIndex;
  Vector3F    m_e0;
  Vector3F    m_e1;
  Vector3F    m_N;
  float       m_A;  // 2 area

  int RemoveVertex(int j, int nVertex) {
    while ( ++j < nVertex )
      m_nIndex[j-1]=m_nIndex[j];
    return (nVertex-1);
  }

  bool IsAnyPointInside(const Vector3F* points,
			int i, int j, int k, int nVertex) const {
    int ik = m_nIndex[k];
    register int ip;
    for ( ip = 0; ip < nVertex; ip++ )
      if ( ( ip < i || ip > k ) &&
	   IsPointInside(points[m_nIndex[ip]],points[ik]) ) {
	return true;
      }
    return false;
  }

  bool IsPointInside(const Vector3F point, const Vector3F q2) const {
    Vector3F pmq2 = point;
    pmq2 = pmq2 - q2;
    Vector3F ntmp;
    float B0, B1;

    ntmp = pmq2 ^ m_e1;
    if ( (B0 = m_N|ntmp) <= 0.0 ) return false;
    ntmp = m_e0 ^ pmq2;
    if ( (B1 = m_N|ntmp) <= 0.0 ) return false;
    return (((m_A - B0 - B1) > 0.0) ? true : false);
  }

  int TriangleArea(const Vector3F* points,
		   int i, int j, int k, const Vector3F& normal) {
    m_e0 = points[i]; m_e0 = m_e0 - points[k];
    m_e1 = points[j]; m_e1 = m_e1 - points[k];

    m_N = m_e0 ^ m_e1;
    m_A = m_N | m_N;

    // j is alligned from i to k ?
    if ( (-FLT_EPSILON) < m_A && m_A < FLT_EPSILON )
      return degenerate;

    // test convexity :
    return ((m_N|normal) < 0.0 ? concave : convex);
  }

private:
  int m_nMaxPoints;

  void AllocIndex(int nCount) {
    if ( nCount > m_nMaxPoints ) {
      if ( m_nIndex ) delete [] m_nIndex;
      m_nMaxPoints = nCount + 2;
      m_nIndex = new int[m_nMaxPoints];
    }
    register int i;
    for ( i = 0; i < nCount; i++ )
      m_nIndex[i] = i;
  }
};

#endif // _UTIL_TESSEL_H_
