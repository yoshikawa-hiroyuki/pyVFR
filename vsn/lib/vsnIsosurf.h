/*
 * This program implements the marching cubes surface tiler
 *  based on the codes written by Mike Krogh, NCSA, Feb.2,1990
 */

/*****************************************************************************
* 
* The following source code is in the public domain.
* Specifically, we give to the public domain all rights for future licensing
* of the source code, all resale rights, and all publishing rights.
* 
* We ask, but do not require, that the following message be included in all
* derived works:
* 
* Portions developed at the National Center for Supercomputing Applications at
* the University of Illinois at Urbana-Champaign.
* 
* THE UNIVERSITY OF ILLINOIS GIVES NO WARRANTY, EXPRESSED OR IMPLIED, FOR THE
* SOFTWARE AND/OR DOCUMENTATION PROVIDED, INCLUDING, WITHOUT LIMITATION,
* WARRANTY OF MERCHANTABILITY AND WARRANTY OF FITNESS FOR A PARTICULAR PURPOSE
*
* This data was developed by the NCSA Visualization Services and
* Development Group.
* 
****************************************************************************/

#ifndef _VSN_ISOSURF_H_
#define _VSN_ISOSURF_H_

#include "obj_impl.h"

inline void* Allocate(size_t size) {return malloc(size);}
inline void  DeAllocate(void *ptr) {free(ptr);}
inline void* CeAllocate(size_t nelem,size_t elsize) {
  return calloc(nelem, elsize);}
inline void* ReAllocate(void *ptr,size_t size) {return realloc(ptr, size);}
inline char* StrDuplicate(const char *string) {return strdup(string);}


class vsnIsosurf {
public:
  template<typename T>
  static VFR_BOOL IsoSurf(const size_t dims[3],
		      const vector3* coord, const T* data,
		      const T& thresh, ObjData& obj);

private:
  struct CELL_ENTRY {
    size_t nverts;
    size_t verts[8];
    size_t nedges;
    size_t edges[12];
    size_t npolys;
    size_t polys[30];
  };

  static const CELL_ENTRY cell_table[256];
  static size_t XDIMYDIM;

  template<typename T>
  static void calc_index(size_t* index, const T* data,
			 const size_t y1, const size_t z1, const size_t xdim,
			 const T thresh);
  template<typename T>
  static void get_cell_verts(const size_t* index, const T* data,
			     const size_t y1, const size_t z1,
			     const size_t xdim, const T threshold,
			     float* crossings);
  template<typename T>
  static void get_cell_verts(const size_t* index,
			     const vector3* coord, const T* data,
			     const size_t y1, const size_t z1,
			     const size_t xdim, const T threshold,
			     float* crossings);
  static size_t get_cell_polys(ObjData& obj,
			       const size_t* index, const size_t xdim,
			       const float* crossings);

  static VFR_BOOL add_polygon(ObjData& obj, const vector3 p1,
			  const vector3 p2, const vector3 p3);

  vsnIsosurf() {}; // don't create instance
};


//==================== STATIC INLINE METHODS ====================

template<typename T> inline VFR_BOOL
vsnIsosurf::IsoSurf(const size_t dims[3],
		    const vector3* coord, const T* data,
		    const T& thresh, ObjData& obj)
{
  size_t y, z;
  size_t xdim1, ydim1, zdim1;
  size_t* index;
  size_t npolys;
  float* crossings;

  zdim1 = dims[2] - 1;
  ydim1 = dims[1] - 1;
  xdim1 = dims[0] - 1;

  XDIMYDIM = dims[0] * dims[1];

  npolys = 0;
  index = (size_t*)Allocate(xdim1*sizeof(size_t));
  crossings = (float*)Allocate(xdim1*13*3*sizeof(float));
  if ( ! index || ! crossings ) return VFR_FALSE;

  obj.alcVerts(0);
  obj.alcNormals(0);

  if ( coord ) {
    for ( z = 0; z < zdim1; z++ )
      for ( y = 0; y < ydim1; y++ ) {
	calc_index(index, data, y, z, dims[0], thresh);
	get_cell_verts(index, coord, data, y, z, dims[0], thresh, crossings);
	npolys += get_cell_polys(obj, index, dims[0], crossings);
      }
  } else {
    for ( z = 0; z < zdim1; z++ )
      for ( y = 0; y < ydim1; y++ ) {
	calc_index(index, data, y, z, dims[0], thresh);
	get_cell_verts(index, data, y, z, dims[0], thresh, crossings);
	npolys += get_cell_polys(obj, index, dims[0], crossings);
      }
  }
  DeAllocate(crossings);
  DeAllocate(index);

  return VFR_TRUE;
}

template<typename T> inline void
vsnIsosurf::calc_index(size_t* index, const T* data,
		       const size_t y1, const size_t z1, const size_t xdim,
		       const T thresh)
{
  const T* tmp;
  T threshold = thresh;
  size_t x1;
  unsigned i = 0;

  /* first compute index of first cube */
  tmp = data + (z1 * XDIMYDIM) + (y1 * xdim) + /* x1= */ 0;
  i += (threshold <= tmp[0]);
  i += (threshold <= tmp[1]) * 2;

  tmp += xdim;
  i += (threshold <= tmp[1]) * 4;
  i += (threshold <= tmp[0]) * 8;

  tmp = tmp - xdim + XDIMYDIM;
  i += (threshold <= tmp[0]) * 16;
  i += (threshold <= tmp[1]) * 32;

  tmp += xdim;
  i += (threshold <= tmp[1]) * 64;
  i += (threshold <= tmp[0]) * 128;

  index[0] = i;

  /* now compute rest */
  tmp -= xdim + XDIMYDIM;
  for ( x1 = 1; x1 < xdim-1; x1++ ) {
    ++tmp;
    i = ((i&0x44)<<1) | ((i&0x22)>>1); /* resuse 4 of the bits */
    i += (threshold <= tmp[1]) * 2;
    i += (threshold <= tmp[xdim+1]) * 4;
    i += (threshold <= tmp[XDIMYDIM+1]) * 32;
    i += (threshold <= tmp[XDIMYDIM+xdim+1]) * 64;
    index[x1] = i;
  }
}


#define CROSSINGS(x,a,b) crossings[(x)*13*3 + (a)*3 + (b)]
#define linterp(a1,a2,a,b1,b2) \
((float)((((a)-(a1)) * (float)((b2)-(b1)) / ((a2)-(a1))) + (float)(b1)))

template<typename T> inline void
vsnIsosurf::get_cell_verts(const size_t* index, const T* data,
			   const size_t y1, const size_t z1,
			   const size_t xdim, const T threshold,
			   float* crossings)
{
  size_t x1, y2, z2;

  y2 = y1 + 1;
  z2 = z1 + 1;
  for ( x1 = 0; x1 < xdim-1; x1++ ) {
    float cx, cy, cz;
    size_t nedges;
    size_t crnt_edge;
    size_t x2 = x1 + 1;
    size_t i;
    const T *v1, *v4, *v5, *v8;

    if ( ! index[x1] ) continue;

    v1 = data + z1*XDIMYDIM + y1*xdim + x1;
    v4 = v1 + xdim;
    v5 = v1 + XDIMYDIM;
    v8 = v4 + XDIMYDIM;

    nedges = cell_table[index[x1]].nedges;
    for ( i = 0; i < nedges; i++ ) {
      crnt_edge = cell_table[index[x1]].edges[i];
      cx = cy = cz = 0.f;
      switch (crnt_edge) {
      case 1:
	cx += linterp(v1[0], v1[1], threshold, x1, x2);
	cy += (float) y1;
	cz += (float) z1;
	break;

      case 2:
	cy += linterp(v1[1], v4[1], threshold, y1, y2);
	cx += (float) x2;
	cz += (float) z1;
	break;

      case 3:
	cx += linterp(v4[0], v4[1], threshold, x1, x2);
	cy += (float) y2;
	cz += (float) z1;
	break;

      case 4:
	cy += linterp(v1[0], v4[0], threshold, y1, y2);
	cx += (float) x1;
	cz += (float) z1;
	break;

      case 5:
	cx += linterp(v5[0], v5[1], threshold, x1, x2);
	cy += (float) y1;
	cz += (float) z2;
	break;

      case 6:
	cy += linterp(v5[1], v8[1], threshold, y1, y2);
	cx += (float) x2;
	cz += (float) z2;
	break;

      case 7:
	cx += linterp(v8[0], v8[1], threshold, x1, x2);
	cy += (float) y2;
	cz += (float) z2;
	break;

      case 8:
	cy += linterp(v5[0], v8[0], threshold, y1, y2);
	cx += (float) x1;
	cz += (float) z2;
	break;

      case 9:
	cz += linterp(v1[0], v5[0], threshold, z1, z2);
	cy += (float) y1;
	cx += (float) x1;
	break;

      case 10:
	cz += linterp(v1[1], v5[1], threshold, z1, z2);
	cy += (float) y1;
	cx += (float) x2;
	break;

      case 11:
	cz += linterp(v4[0], v8[0], threshold, z1, z2);
	cy += (float) y2;
	cx += (float) x1;
	break;

      case 12:
	cz += linterp(v4[1], v8[1], threshold, z1, z2);
	cy += (float) y2;
	cx += (float) x2;
	break;

      } /* end of switch */

      CROSSINGS(x1,crnt_edge,0) = cx;
      CROSSINGS(x1,crnt_edge,1) = cy;
      CROSSINGS(x1,crnt_edge,2) = cz;
    } /* end of for */
  }
}

#define linterpA(a1,a2,a) ((float)((a)-(a1)) / (float)((a2)-(a1)))
#define linterpB(b1,b2,a) ((float)((b2)-(b1)) * (a) + (float)(b1)) 
#define CRDXYZ(i,j,k,l) coord[XDIMYDIM*(k) + xdim*(j) + (i)][(l)]

template<typename T> inline void
vsnIsosurf::get_cell_verts(const size_t* index,
			   const vector3* coord, const T* data,
			   const size_t y1, const size_t z1,
			   const size_t xdim, const T threshold,
			   float* crossings)
{
  size_t x1, y2, z2;
  float A, xx1, yy1, zz1, xx2, yy2, zz2;

  y2 = y1 + 1;
  z2 = z1 + 1;
  for ( x1 = 0; x1 < xdim-1; x1++ ) {
    size_t nedges;
    size_t crnt_edge;
    size_t x2 = x1 + 1;
    size_t i;
    const T *v1, *v4, *v5, *v8;

    if ( ! index[x1] ) continue;

    v1 = data + z1*XDIMYDIM + y1*xdim + x1;
    v4 = v1 + xdim;
    v5 = v1 + XDIMYDIM;
    v8 = v4 + XDIMYDIM;

    nedges = cell_table[index[x1]].nedges;
    for ( i = 0; i < nedges; i++ ) {
      crnt_edge = cell_table[index[x1]].edges[i];
      switch (crnt_edge) {
      case 1:
	A = linterpA(v1[0], v1[1], threshold);
	xx1 = CRDXYZ(x1, y1, z1, 0); xx2 = CRDXYZ(x2, y1, z1, 0);
	yy1 = CRDXYZ(x1, y1, z1, 1); yy2 = CRDXYZ(x2, y1, z1, 1);
	zz1 = CRDXYZ(x1, y1, z1, 2); zz2 = CRDXYZ(x2, y1, z1, 2);
	break;

      case 2:
	A = linterpA(v1[1], v4[1], threshold);
	xx1 = CRDXYZ(x2, y1, z1, 0); xx2 = CRDXYZ(x2, y2, z1, 0);
	yy1 = CRDXYZ(x2, y1, z1, 1); yy2 = CRDXYZ(x2, y2, z1, 1);
	zz1 = CRDXYZ(x2, y1, z1, 2); zz2 = CRDXYZ(x2, y2, z1, 2);
	break;

      case 3:
	A = linterpA(v4[0], v4[1], threshold);
	xx1 = CRDXYZ(x1, y2, z1, 0); xx2 = CRDXYZ(x2, y2, z1, 0);
	yy1 = CRDXYZ(x1, y2, z1, 1); yy2 = CRDXYZ(x2, y2, z1, 1);
	zz1 = CRDXYZ(x1, y2, z1, 2); zz2 = CRDXYZ(x2, y2, z1, 2);
	break;

      case 4:
	A = linterpA(v1[0], v4[0], threshold);
	xx1 = CRDXYZ(x1, y1, z1, 0); xx2 = CRDXYZ(x1, y2, z1, 0);
	yy1 = CRDXYZ(x1, y1, z1, 1); yy2 = CRDXYZ(x1, y2, z1, 1);
	zz1 = CRDXYZ(x1, y1, z1, 2); zz2 = CRDXYZ(x1, y2, z1, 2);
	break;

      case 5:
	A = linterpA(v5[0], v5[1], threshold);
	xx1 = CRDXYZ(x1, y1, z2, 0); xx2 = CRDXYZ(x2, y1, z2, 0);
	yy1 = CRDXYZ(x1, y1, z2, 1); yy2 = CRDXYZ(x2, y1, z2, 1);
	zz1 = CRDXYZ(x1, y1, z2, 2); zz2 = CRDXYZ(x2, y1, z2, 2);
	break;

      case 6:
	A = linterpA(v5[1], v8[1], threshold);
	xx1 = CRDXYZ(x2, y1, z2, 0); xx2 = CRDXYZ(x2, y2, z2, 0);
	yy1 = CRDXYZ(x2, y1, z2, 1); yy2 = CRDXYZ(x2, y2, z2, 1);
	zz1 = CRDXYZ(x2, y1, z2, 2); zz2 = CRDXYZ(x2, y2, z2, 2);
	break;

      case 7:
	A = linterpA(v8[0], v8[1], threshold);
	xx1 = CRDXYZ(x1, y2, z2, 0); xx2 = CRDXYZ(x2, y2, z2, 0);
	yy1 = CRDXYZ(x1, y2, z2, 1); yy2 = CRDXYZ(x2, y2, z2, 1);
	zz1 = CRDXYZ(x1, y2, z2, 2); zz2 = CRDXYZ(x2, y2, z2, 2);
	break;

      case 8:
	A = linterpA(v5[0], v8[0], threshold);
	xx1 = CRDXYZ(x1, y1, z2, 0); xx2 = CRDXYZ(x1, y2, z2, 0);
	yy1 = CRDXYZ(x1, y1, z2, 1); yy2 = CRDXYZ(x1, y2, z2, 1);
	zz1 = CRDXYZ(x1, y1, z2, 2); zz2 = CRDXYZ(x1, y2, z2, 2);
	break;

      case 9:
	A = linterpA(v1[0], v5[0], threshold);
	xx1 = CRDXYZ(x1, y1, z1, 0); xx2 = CRDXYZ(x1, y1, z2, 0);
	yy1 = CRDXYZ(x1, y1, z1, 1); yy2 = CRDXYZ(x1, y1, z2, 1);
	zz1 = CRDXYZ(x1, y1, z1, 2); zz2 = CRDXYZ(x1, y1, z2, 2);
	break;

      case 10:
	A = linterpA(v1[1], v5[1], threshold);
	xx1 = CRDXYZ(x2, y1, z1, 0); xx2 = CRDXYZ(x2, y1, z2, 0);
	yy1 = CRDXYZ(x2, y1, z1, 1); yy2 = CRDXYZ(x2, y1, z2, 1);
	zz1 = CRDXYZ(x2, y1, z1, 2); zz2 = CRDXYZ(x2, y1, z2, 2);
	break;

      case 11:
	A = linterpA(v4[0], v8[0], threshold);
	xx1 = CRDXYZ(x1, y2, z1, 0); xx2 = CRDXYZ(x1, y2, z2, 0);
	yy1 = CRDXYZ(x1, y2, z1, 1); yy2 = CRDXYZ(x1, y2, z2, 1);
	zz1 = CRDXYZ(x1, y2, z1, 2); zz2 = CRDXYZ(x1, y2, z2, 2);
	break;

      case 12:
	A = linterpA(v4[1], v8[1], threshold);
	xx1 = CRDXYZ(x2, y2, z1, 0); xx2 = CRDXYZ(x2, y2, z2, 0);
	yy1 = CRDXYZ(x2, y2, z1, 1); yy2 = CRDXYZ(x2, y2, z2, 1);
	zz1 = CRDXYZ(x2, y2, z1, 2); zz2 = CRDXYZ(x2, y2, z2, 2);
	break;

      } /* end of switch */

      CROSSINGS(x1,crnt_edge,0) = linterpB(xx1, xx2, A);
      CROSSINGS(x1,crnt_edge,1) = linterpB(yy1, yy2, A);
      CROSSINGS(x1,crnt_edge,2) = linterpB(zz1, zz2, A);
    } /* end of for */
  }
}


inline size_t
vsnIsosurf::get_cell_polys(ObjData& obj,
			   const size_t* index, const size_t xdim,
			   const float* crossings)
{
  size_t num_o_polys, polys = 0;
  size_t poly;
  const float *p1, *p2, *p3;
  size_t x1;

  for ( x1 = 0; x1 < xdim-1; x1++ ) {
    if ( ! index[x1] ) continue;
    num_o_polys = cell_table[index[x1]].npolys;
    for ( poly = 0; poly < num_o_polys; poly++ ) {
      p1 = &CROSSINGS(x1,cell_table[index[x1]].polys[poly*3],0);
      p2 = &CROSSINGS(x1,cell_table[index[x1]].polys[poly*3 + 1],0);
      p3 = &CROSSINGS(x1,cell_table[index[x1]].polys[poly*3 + 2],0);
      if ((p1[0] == p2[0] && p1[1] == p2[1] && p1[2] == p2[2]) ||
	  (p1[0] == p3[0] && p1[1] == p3[1] && p1[2] == p3[2]) ||
	  (p2[0] == p3[0] && p2[1] == p3[1] && p2[2] == p3[2]))  {
	polys--;
	continue;
      }

      if ( ! add_polygon(obj, p1, p2, p3) ) {
	polys--;
	continue;
      }
    }

    polys += num_o_polys;
  }
  return polys;
}


#define VERT_INCR 20000

inline VFR_BOOL
vsnIsosurf::add_polygon(ObjData& obj, const vector3 p1,
			const vector3 p2, const vector3 p3)
{
  int nv = obj.nVerts;
  if ( ! obj.setVert(nv, p1) ) {
    if ( ! obj.alcPools(nv + VERT_INCR, -1, -1, -1) ) return VFR_FALSE;
    obj.alcVerts(nv+1);
    if ( ! obj.setVert(nv, p1) ) return VFR_FALSE;
  }
  if ( ! obj.setVert(++nv, p2) ) {
    if ( ! obj.alcPools(nv + VERT_INCR, -1, -1, -1) ) return VFR_FALSE;
    obj.alcVerts(nv+1);
    if ( ! obj.setVert(nv, p2) ) return VFR_FALSE;
  }
  if ( ! obj.setVert(++nv, p3) ) {
    if ( ! obj.alcPools(nv + VERT_INCR, -1, -1, -1) ) return VFR_FALSE;
    obj.alcVerts(nv+1);
    if ( ! obj.setVert(nv, p3) ) return VFR_FALSE;
  }
  return VFR_TRUE;
}

#undef CROSSINGS
#undef linterp
#undef linterpA
#undef linterpB
#undef CRDXYZ
#undef VERT_INCR

#endif // _VSN_ISOSURF_H_
