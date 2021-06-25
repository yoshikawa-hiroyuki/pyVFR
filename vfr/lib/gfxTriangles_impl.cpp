/*
vfr scene-graph library

Copyright(c) RIKEN, 2008-2009, All Right Reserved.
*/

#include "gfx_impl.h"
#include "util/utilMath.h"


//---------------------- gfxNode_DrawTrias ----------------------
VFR_API int gfxTriangles_DrawTrias(int nv, float* vtx,
				   int nn, float* normal,
				   int nc, float* color,
				   int ntype, int ctype, int fbk)
{
  if ( nv < 3 || ! vtx ) return 0;
  if ( nn > 0 && ! normal ) return 0;
  if ( nc > 0 && ! color ) return 0;

  int i, v, n, c, f, nFace = nv / 3;
  if ( fbk ) {
    v = 0;
    for ( f = 0; f < nFace; f++ ) {
      glPassThrough((GLfloat)f);
      glBegin(GL_TRIANGLES);
      for ( i = 0; i < 3; i++ ) {
	glVertex3fv(&vtx[v*3]); v++;
      }
      glEnd();
    } // end of for(i)
  }
  else {
    if ( ntype == AT_WHOLE && nn > 0 )
      glNormal3fv(&normal[0]);
    
    v = n = c = 0;
    glBegin(GL_TRIANGLES);
    for ( f = 0; f < nFace; f++ ) {
      if ( ctype == AT_PER_FACE && c < nc ) {
	glColor4fv(&color[c*4]); c++;
      }
      if ( ntype == AT_PER_FACE && n < nn ) {
	glNormal3fv(&normal[n*3]); n++;
      }
      
      for ( i = 0; i < 3; i++ ) {
	if ( ctype == AT_PER_VERTEX && c < nc ) {
	  glColor4fv(&color[c*4]); c++;
	}
	if ( ntype == AT_PER_VERTEX && n < nn ) {
	  glNormal3fv(&normal[n*3]); n++;
	}
	glVertex3fv(&vtx[v*3]); v++;
      } // end of for(i)
    } // end of for(f)
    glEnd(); 
  }

  return 1;
} // end of gfxTriangles_DrawTrias()


//---------------------- Normal smoother ----------------------
#define TS_HASH_TABLE_SIZE 9967
//  both 283 and 9967 are prime number

class TriaSmoother {
public:
  VFR_BOOL SmoothNorm(int nv, vector3* vtx, int nn, vector3* normal);
  float getTolerance() const {return cosTolerance;}

  struct HASH_ENTRY {
    size_t tri, off;
    struct HASH_ENTRY* next;
    HASH_ENTRY() : tri(0), off(0), next(NULL) {}
  };

  TriaSmoother(const float tolerance =0.707f)
    : hTbl(NULL), cosTolerance(tolerance) {
    hTbl = (HASH_ENTRY**)malloc(sizeof(HASH_ENTRY*)*TS_HASH_TABLE_SIZE);
    if ( cosTolerance < 0.01f || cosTolerance > 0.99f )
      cosTolerance = 0.707f;
  }
  ~TriaSmoother() {if ( hTbl ) free(hTbl);}

private:
  HASH_ENTRY** hTbl;
  float cosTolerance;
  static size_t hashValue(const vector3 v) {
    const size_t* p = (const size_t*)v;
    return (((p[0]*283+p[1])*283)+p[2]) % TS_HASH_TABLE_SIZE;
  }

  void hashInsert(const vector3 v, const size_t t, const size_t o) {
    if ( ! hTbl ) return;
    size_t h = hashValue(v);
    HASH_ENTRY* hh = new HASH_ENTRY();
    hh->next = hTbl[h]; hTbl[h] = hh;
    hh->tri = t; hh->off = o;
  }
};

VFR_BOOL TriaSmoother::SmoothNorm(int nV, vector3* vtx, int nN, vector3* normal)
{
  size_t i;
  if ( ! hTbl ) return VFR_FALSE;
  memset(hTbl, 0, sizeof(HASH_ENTRY*)*TS_HASH_TABLE_SIZE);

  size_t numV = nV;
  size_t numN = nV / 3;
  if ( numV < 3 || numN < 1 ) return VFR_FALSE;

  vector3* newNV = (vector3*)malloc(sizeof(vector3)*numV);
  if ( ! newNV ) return VFR_FALSE;
  vector3* pv = vtx;
  vector3* pn = normal;
  for ( i = 0; i < numN; i++ ) {
    CES::Vec3<float> wkn;
    memcpy(wkn.m_v, pn[i], sizeof(vector3));
    wkn.UnitVec();
    memcpy(newNV[i*3   ], wkn.m_v, sizeof(vector3));
    memcpy(newNV[i*3 +1], wkn.m_v, sizeof(vector3));
    memcpy(newNV[i*3 +2], wkn.m_v, sizeof(vector3));
  }

  // create table
  for ( i = 0; i < numV/3; i++ ) {
    hashInsert(pv[i*3   ], i, 0);
    hashInsert(pv[i*3 +1], i, 1);
    hashInsert(pv[i*3 +2], i, 2);
  }

  // smooth
  for ( i = 0; i < TS_HASH_TABLE_SIZE; i++ ) {
    while ( hTbl[i] ) {
      HASH_ENTRY *p, *nequal = NULL, *equal = hTbl[i];
      int j=0;
      CES::Vec3<float> nn, vv;
      float cs;

      vv[0] = pv[equal->tri*3 + equal->off][0];
      vv[1] = pv[equal->tri*3 + equal->off][1];
      vv[2] = pv[equal->tri*3 + equal->off][2];
      nn[0] = newNV[equal->tri*3 + equal->off][0];
      nn[1] = newNV[equal->tri*3 + equal->off][1];
      nn[2] = newNV[equal->tri*3 + equal->off][2];

      for( p = equal->next, equal->next = 0; p; ) {
        HASH_ENTRY *p1 = p->next;
        if ( pv[p->tri*3 + p->off][0] == vv[0] &&
             pv[p->tri*3 + p->off][1] == vv[1] &&
             pv[p->tri*3 + p->off][2] == vv[2] ) {
          cs = CES::Vec3<float>(newNV[p->tri*3 +p->off]) | nn;
          if ( cs > cosTolerance ) {
            p->next = equal; equal = p;
            j++;
            p = p1;
            continue;
          }
        }
        p->next = nequal; nequal = p;
        p = p1;
      } // end of for(p)

      hTbl[i] = nequal;
      if ( j == 1 ) {
        delete equal; hTbl[i] = NULL;
        continue;
      }

      /* average the normal */
      nn[0] = nn[1] = nn[2] = 0.f;
      for ( p = equal; p; p = p->next ) {
        nn[0] += newNV[p->tri*3 + p->off][0];
        nn[1] += newNV[p->tri*3 + p->off][1];
        nn[2] += newNV[p->tri*3 + p->off][2];
      }
      nn.UnitVec();

      /* put it back */
      for ( p = equal; p; ) {
        HASH_ENTRY *p1 = p->next;
        newNV[p->tri*3 + p->off][0] = nn[0];
        newNV[p->tri*3 + p->off][1] = nn[1];
        newNV[p->tri*3 + p->off][2] = nn[2];
        delete p;
        p = p1;
      }
      hTbl[i] = NULL;

    } // end while
  } // end of for(i)

  memcpy(normal, newNV, sizeof(vector3)*numV);
  free(newNV);
  return VFR_TRUE;
}


//---------------------- gfxTriangles_CalcNormals ----------------------
VFR_API VFR_BOOL gfxTriangles_CalcNormals(int nv, float* vtx,
					  int nn, float* normal, int ntype)
{
  if ( ! vtx || ! normal ) return VFR_FALSE;
  int faceNum = nv / 3;
  int vtxNum = nv;
  int nmlNum = faceNum;
  if ( ntype == AT_PER_VERTEX ) nmlNum = vtxNum;
  if ( nv < vtxNum || vtxNum < 1 ) return VFR_FALSE;
  if ( nn < nmlNum ) return VFR_FALSE;
  
  int n;
  CES::Vec3<float> v1, v2, nvec;
  for ( n = 0; n < faceNum; n++ ) {
    v1[0] = vtx[(n*3+1)*3  ] - vtx[(n*3  )*3  ];
    v1[1] = vtx[(n*3+1)*3+1] - vtx[(n*3  )*3+1];
    v1[2] = vtx[(n*3+1)*3+2] - vtx[(n*3  )*3+2];
    v2[0] = vtx[(n*3+2)*3  ] - vtx[(n*3+1)*3  ];
    v2[1] = vtx[(n*3+2)*3+1] - vtx[(n*3+1)*3+1];
    v2[2] = vtx[(n*3+2)*3+2] - vtx[(n*3+1)*3+2];
    nvec = v1 ^ v2;
    normal[n*3  ] = nvec[0];
    normal[n*3+1] = nvec[1];
    normal[n*3+2] = nvec[2];
  }

  if ( ntype == AT_PER_VERTEX ) {
    TriaSmoother smoother;
    return smoother.SmoothNorm(nv, (vector3*)vtx, nn, (vector3*)normal);
  }
  return VFR_TRUE;
}
