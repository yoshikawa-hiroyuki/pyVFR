/*
vfr scene-graph library

Copyright(c) RIKEN, 2008-2009, All Right Reserved.
*/
#include "obj_impl.h"

// class ObjData
ObjData::ObjData()
  : nVerts(0), nPoolVerts(0), nNormals(0), nPoolNormals(0),
    nIndices(0), nPoolIndices(0), nColors(0),  nPoolColors(0),
    _verts(NULL), _normals(NULL), _indices(NULL), _colors(NULL) {
  _bbox[0][0] = _bbox[0][1] = _bbox[0][2] = 0.f;
  _bbox[1][0] = _bbox[1][1] = _bbox[1][2] = 0.f;
}
  
ObjData::~ObjData() {
  if ( _verts ) {
    free(_verts);
    _verts = NULL;
  }
  if ( _normals ) {
    free(_normals);
    _normals = NULL;
  }
  if ( _indices ) {
    free(_indices);
    _indices = NULL;
  }
  if ( _colors ) {
    free(_colors);
    _colors = NULL;
  }
}

VFR_BOOL ObjData::alcPools(const int nV, const int nN,
			   const int nI, const int nC) {
  // Pool verts area
  if ( nPoolVerts < nV ) {
    _verts = (vector3*)realloc(_verts, sizeof(vector3)*nV);
    if ( _verts == NULL ) {
      nPoolVerts = nVerts = 0;
      return VFR_FALSE;
    }
    nPoolVerts = nV;
  }
  
  // Pool normals area
  if ( nPoolNormals < nN ) {
    _normals = (vector3*)realloc(_normals, sizeof(vector3)*nN);
    if ( _normals == NULL ) {
      nPoolNormals = nNormals = 0;
      return VFR_FALSE;
    }
    nPoolNormals = nN;
  }
  
  // Pool indices area
  if ( nPoolIndices < nI ) {
    _indices = (int*)realloc(_indices, sizeof(int)*nI);
    if ( _indices == NULL ) {
      nPoolIndices = nIndices = 0;
      return VFR_FALSE;
    }
    nPoolIndices = nI;
  }
  
  // Pool colors area
  if ( nPoolColors < nC ) {
    _colors = (vector4*)realloc(_colors, sizeof(vector4)*nC);
    if ( _colors == NULL ) {
      nPoolColors = nColors = 0;
      return VFR_FALSE;
    }
    nPoolColors = nC;
  }
  
  return VFR_TRUE;
}
  
VFR_BOOL ObjData::alcVerts(const int nv) {
  if ( nv < 0 ) return VFR_TRUE;
  if ( nVerts < nv ) {
    if ( ! alcPools(nv, -1, -1, -1) )
      return VFR_FALSE;
  }
  for ( int i = nVerts; i < nv; i++ ) {
    _verts[i][0] = 0.0f;
    _verts[i][1] = 0.0f;
    _verts[i][2] = 0.0f;
  }
  nVerts = nv;
  return VFR_TRUE;
}

VFR_BOOL ObjData::alcNormals(const int nn) {
  if ( nn < 0 ) return VFR_TRUE;
  if ( nNormals < nn ) {
    if ( ! alcPools(-1, nn, -1, -1) )
      return VFR_FALSE;
  }
  for ( int i = nNormals; i < nn; i++ ) {
    _normals[i][0] = 0.0f;
    _normals[i][1] = 0.0f;
    _normals[i][2] = 1.0f;
  }
  nNormals = nn;
  return VFR_TRUE;
}

VFR_BOOL ObjData::alcIndices(const int n) {
  if ( n < 0 ) return VFR_TRUE;
  if ( nIndices < n ) {
    if ( ! alcPools(-1, -1, n, -1) )
      return VFR_FALSE;
  }
  for ( int i = nIndices; i < n; i++ )
    _indices[i] = -1;
  nIndices = n;
  return VFR_TRUE;
}

VFR_BOOL ObjData::alcColors(const int nc) {
  if ( nc < 0 ) return VFR_TRUE;
  if ( nColors < nc ) {
    if ( ! alcPools(-1, -1, -1, nc) )
      return VFR_FALSE;
  }
  for ( int i = nColors; i < nc; i++ ) {
    _colors[i][0] = 0.9f;
    _colors[i][1] = 0.9f;
    _colors[i][2] = 0.9f;
    _colors[i][3] = 1.0f;
  }
  nColors = nc;
  return VFR_TRUE;
}

VFR_BOOL ObjData::setVert(const int n, const vector3 vv) {
  if ( n >= nVerts )
    return VFR_FALSE;
  _verts[n][0] = vv[0];
  _verts[n][1] = vv[1];
  _verts[n][2] = vv[2];
  return VFR_TRUE;
}

VFR_BOOL ObjData::setNormal(const int n, const vector3 nv) {
  if ( n >= nNormals )
    return VFR_FALSE;
  _normals[n][0] = nv[0];
  _normals[n][1] = nv[1];
  _normals[n][2] = nv[2];
  return VFR_TRUE;
}

VFR_BOOL ObjData::setIndice(const int n, const int ind) {
  if ( n >= nIndices )
    return VFR_FALSE;
  _indices[n] = ind;
  return VFR_TRUE;
}

VFR_BOOL ObjData::setColor3(const int n, const vector3 cv) {
  if ( n >= nColors )
    return VFR_FALSE;
  _colors[n][0] = cv[0];
  _colors[n][1] = cv[1];
  _colors[n][2] = cv[2];
  return VFR_TRUE;
}

VFR_BOOL ObjData::setColor4(const int n, const vector4 cv) {
  if ( n >= nColors )
    return VFR_FALSE;
  _colors[n][0] = cv[0];
  _colors[n][1] = cv[1];
  _colors[n][2] = cv[2];
  _colors[n][3] = cv[3];
  return VFR_TRUE;
}

void ObjData::generateBbox() {
  if ( nVerts < 1 ) {
    _bbox[0][0] = _bbox[0][1] = _bbox[0][2] = 0.0f;
    _bbox[1][0] = _bbox[1][1] = _bbox[1][2] = 1e-6f;
    return;
  }
  int i;
  memcpy(_bbox[0], _verts[0], sizeof(vector3));
  memcpy(_bbox[1], _verts[0], sizeof(vector3));
  for ( i = 1; i < nVerts; i++ ) {
    if ( _bbox[0][0] > _verts[i][0] ) _bbox[0][0] = _verts[i][0];
    if ( _bbox[1][0] < _verts[i][0] ) _bbox[1][0] = _verts[i][0];
    if ( _bbox[0][1] > _verts[i][1] ) _bbox[0][1] = _verts[i][1];
    if ( _bbox[1][1] < _verts[i][1] ) _bbox[1][1] = _verts[i][1];
    if ( _bbox[0][2] > _verts[i][2] ) _bbox[0][2] = _verts[i][2];
    if ( _bbox[1][2] < _verts[i][2] ) _bbox[1][2] = _verts[i][2];
  } // end of f or(i)
}


//------------------------------------------------------------------------
// interfaces for ctypes
//------------------------------------------------------------------------
VFR_API void* ObjData_Create() {
  ObjData* p = new ObjData();
  return (void*)p;
}

VFR_API void ObjData_Delete(void* p) {
  ObjData* po = (ObjData*)p;
  if ( ! po ) return;
  delete po;
}

VFR_API VFR_BOOL ObjData_AlcPools(void* p, const int nV, const int nN,
				  const int nI, const int nC) {
  ObjData* po = (ObjData*)p;
  if ( ! po ) return VFR_FALSE;
  VFR_BOOL ret = po->alcPools(nV, nN, nI, nC);
  return ret;
}

VFR_API VFR_BOOL ObjData_AlcVerts(void* p, const int nV) {
  ObjData* po = (ObjData*)p;
  if ( ! po ) return VFR_FALSE;
  VFR_BOOL ret = po->alcVerts(nV);
  return ret;
}

VFR_API VFR_BOOL ObjData_AlcNormals(void* p, const int nN) {
  ObjData* po = (ObjData*)p;
  if ( ! po ) return VFR_FALSE;
  VFR_BOOL ret = po->alcNormals(nN);
  return ret;
}

VFR_API VFR_BOOL ObjData_AlcIndices(void* p, const int nI) {
  ObjData* po = (ObjData*)p;
  if ( ! po ) return VFR_FALSE;
  VFR_BOOL ret = po->alcIndices(nI);
  return ret;
}

VFR_API VFR_BOOL ObjData_AlcColors(void* p, const int nC) {
  ObjData* po = (ObjData*)p;
  if ( ! po ) return VFR_FALSE;
  VFR_BOOL ret = po->alcColors(nC);
  return ret;
}

VFR_API int ObjData_GetNumVerts(void* p) {
  ObjData* po = (ObjData*)p;
  if ( ! po ) return VFR_INVALID;
  return po->nVerts;
}
VFR_API int ObjData_GetNumNormals(void* p) {
  ObjData* po = (ObjData*)p;
  if ( ! po ) return VFR_INVALID;
  return po->nNormals;
}
VFR_API int ObjData_GetNumIndices(void* p) {
  ObjData* po = (ObjData*)p;
  if ( ! po ) return VFR_INVALID;
  return po->nIndices;
}
VFR_API int ObjData_GetNumColors(void* p) {
  ObjData* po = (ObjData*)p;
  if ( ! po ) return VFR_INVALID;
  return po->nColors;
}

VFR_API vector3* ObjData_GetVerts(void* p) {
  ObjData* po = (ObjData*)p;
  if ( ! po ) return NULL;
  return po->_verts;
}
VFR_API vector3* ObjData_GetNormals(void* p) {
  ObjData* po = (ObjData*)p;
  if ( ! po ) return NULL;
  return po->_normals;
}
VFR_API int* ObjData_GetIndices(void* p) {
  ObjData* po = (ObjData*)p;
  if ( ! po ) return NULL;
  return po->_indices;
}
VFR_API vector4* ObjData_GetColors(void* p) {
  ObjData* po = (ObjData*)p;
  if ( ! po ) return NULL;
  return po->_colors;
}

VFR_API void ObjData_GenerateBbox(void* p) {
  ObjData* po = (ObjData*)p;
  if ( ! po ) return;
  po->generateBbox();
}
VFR_API vector3* ObjData_GetBbox(void* p) {
  ObjData* po = (ObjData*)p;
  if ( ! po ) return NULL;
  return po->_bbox;
}
