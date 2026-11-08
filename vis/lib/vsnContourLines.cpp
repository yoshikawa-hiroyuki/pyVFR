//
// vsnContourLines
//
#include "gfx_impl.h"
#include "obj_impl.h"

bool calcLineSegment(const vector3 p0, const vector3 p1, const vector3 p2,
		     const float val0, const float val1, const float val2,
		     const float val, vector3 lp1, vector3 lp2)
{
  using namespace CES;
 
  int i, j, idx;
  char vFlg[3] = {0, 0, 0};

  j = 0;
  if ( val0 > val ) {vFlg[0] = 1; j++;}
  if ( val1 > val ) {vFlg[1] = 1; j++;}
  if ( val2 > val ) {vFlg[2] = 1; j++;}
  if ( j == 0 || j == 3 ) return false; // contour line not crossed

  Vec3<float> pos[3] = {Vec3<float>(p0), Vec3<float>(p1), Vec3<float>(p2)};
  Vec3<float> lp;
  float vals[3] = {val0, val1, val2};
  float t;
  int top = -1; int bot[2] = {-1, -1};
  if ( j == 1 ) {
    for ( idx = 0, i = 0; i < 3; i++ )
      if ( vFlg[i] == 1 ) top = i;
      else bot[idx++] = i;
  } else {
    for ( idx = 0, i = 0; i < 3; i++ )
      if ( vFlg[i] == 0 ) top = i;
      else bot[idx++] = i;
  }

  // lp1: top---bot[0]
  if ( vals[top] == vals[bot[0]] ) return false; // something wrong
  t = (val - vals[top]) / (vals[bot[0]] - vals[top]);
  lp = pos[top] + (pos[bot[0]] - pos[top]) * t;
  lp1[0] = lp[0]; lp1[1] = lp[1]; lp1[2] = lp[2];

  // lp2 : top---bot[1]
  if ( vals[top] == vals[bot[1]] ) return false; // something wrong
  t = (val - vals[top]) / (vals[bot[1]] - vals[top]);
  lp = pos[top] + (pos[bot[1]] - pos[top]) * t;
  lp2[0] = lp[0]; lp2[1] = lp[1]; lp2[2] = lp[2];

  return true;
} 


//------------------------------------------------------------------------
// interfaces for ctypes
//------------------------------------------------------------------------

#define DSLICE(d, x, y) (d)[(y)*M + (x)]
#define CSLICE(d, x, y, z) (d)[((y)*M + (x)) * 3 + (z)]

VFR_API int CountLineSegments(float* pvd, const size_t dims[2], const float val)
{
  if ( ! pvd ) return 0;
  const int vidxs[4][3] = {{0, 1, 4}, {1, 2, 4}, {2, 3, 4}, {3, 0, 4}};
  float vv[5];
  size_t M = dims[0], N = dims[1];
  if ( M * N < 4 ) return 0;
  size_t i, j, k, cnt_vc = 0;

  for (j=0; j < N-1; j++) {
    for (i=0; i < M-1; i++) {
      int vflgs[5] = {0, 0, 0, 0, 0};
      vv[0] = DSLICE(pvd, i  , j  );
      vv[1] = DSLICE(pvd, i+1, j  );
      vv[2] = DSLICE(pvd, i+1, j+1);
      vv[3] = DSLICE(pvd, i  , j+1);
      vv[4] = (vv[0] + vv[1] + vv[2] +vv[3]) * 0.25f;
      for (k=0; k < 5; k++)
	if (vv[k] > val) vflgs[k] = 1;
      for (k=0; k < 4; k++) {
	int vfSum = vflgs[vidxs[k][0]] +vflgs[vidxs[k][1]] +vflgs[vidxs[k][2]];
	if (vfSum == 1 || vfSum == 2)
	  cnt_vc += 1;
      } // end of for(k)
    } // end of for(i)
  } // end of for(j)

  return cnt_vc;
}

VFR_API int AddLineSegments(void* p, float* pvc, float* pvd,
			    const size_t dims[2], const float val)
{
  if ( ! pvc || ! pvd ) return 0;
  float vv[5], vc[3];
  float lp1[3], lp2[3];
  size_t M = dims[0], N = dims[1];
  if ( M * N < 4 ) return 0;
  size_t i, j;
  
  ObjData* po = static_cast<ObjData*>(p);
  if ( ! po ) return 0;

  int idx = 0;
  for (j=0; j < N-1; j++) {
    for (i=0; i < M-1; i++) {
      vv[0] = DSLICE(pvd, i  , j  );
      vv[1] = DSLICE(pvd, i+1, j  );
      vv[2] = DSLICE(pvd, i+1, j+1);
      vv[3] = DSLICE(pvd, i  , j+1);
      vv[4] = (vv[0] + vv[1] + vv[2] +vv[3]) * 0.25f;

      vc[0] = (CSLICE(pvc, i  , j  , 0) + CSLICE(pvc, i+1, j  , 0) + \
	       CSLICE(pvc, i+1, j+1, 0) + CSLICE(pvc, i  , j+1, 0)) * 0.25f;
      vc[1] = (CSLICE(pvc, i  , j  , 1) + CSLICE(pvc, i+1, j  , 1) + \
	       CSLICE(pvc, i+1, j+1, 1) + CSLICE(pvc, i  , j+1, 1)) * 0.25f;
      vc[2] = (CSLICE(pvc, i  , j  , 2) + CSLICE(pvc, i+1, j  , 2) + \
	       CSLICE(pvc, i+1, j+1, 2) + CSLICE(pvc, i  , j+1, 2)) * 0.25f;

      // triangle(0, 1, C)
      if ( calcLineSegment(&CSLICE(pvc, i,j,0), &CSLICE(pvc, i+1,j,0),
			   vc, vv[0], vv[1], vv[4], val, lp1, lp2) ) {
	po->_verts[idx][0] = lp1[0];
	po->_verts[idx][1] = lp1[1];
	po->_verts[idx][2] = lp1[2];
	idx ++;
	po->_verts[idx][0] = lp2[0];
	po->_verts[idx][1] = lp2[1];
	po->_verts[idx][2] = lp2[2];
	idx ++;
      }
      // triangle(1, 2, C)
      if ( calcLineSegment(&CSLICE(pvc, i+1,j,0), &CSLICE(pvc, i+1,j+1,0),
			   vc, vv[1], vv[2], vv[4], val, lp1, lp2) ) {
	po->_verts[idx][0] = lp1[0];
	po->_verts[idx][1] = lp1[1];
	po->_verts[idx][2] = lp1[2];
	idx ++;
	po->_verts[idx][0] = lp2[0];
	po->_verts[idx][1] = lp2[1];
	po->_verts[idx][2] = lp2[2];
	idx ++;
      }
      // triangle(2, 3, C)
      if ( calcLineSegment(&CSLICE(pvc, i+1,j+1,0), &CSLICE(pvc, i,j+1,0),
			   vc, vv[2], vv[3], vv[4], val, lp1, lp2) ) {
	po->_verts[idx][0] = lp1[0];
	po->_verts[idx][1] = lp1[1];
	po->_verts[idx][2] = lp1[2];
	idx ++;
	po->_verts[idx][0] = lp2[0];
	po->_verts[idx][1] = lp2[1];
	po->_verts[idx][2] = lp2[2];
	idx ++;
      }
      // triangle(3, 0, C)
      if ( calcLineSegment(&CSLICE(pvc, i,j+1,0), &CSLICE(pvc, i,j,0),
			   vc, vv[3], vv[0], vv[4], val, lp1, lp2) ) {
	po->_verts[idx][0] = lp1[0];
	po->_verts[idx][1] = lp1[1];
	po->_verts[idx][2] = lp1[2];
	idx ++;
	po->_verts[idx][0] = lp2[0];
	po->_verts[idx][1] = lp2[1];
	po->_verts[idx][2] = lp2[2];
	idx ++;
      }
    } // end of for(i)
  } // end of for(j)

  return idx;
}
