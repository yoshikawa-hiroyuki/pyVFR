/*
vfr scene-graph library

Copyright(c) YoH, 2026, All Right Reserved.
*/

#include "gfx_impl.h"
#include "util/utilMath.h"
#include <deque>


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
    float vcolor[4];
    v = 0;
    glBegin(GL_TRIANGLES);
    for ( f = 0; f < nFace; f++ ) {
      id_to_rgba(f+1, vcolor); // offset id
      glColor4fv(vcolor);
      for ( i = 0; i < 3; i++ ) {
	glVertex3fv(&vtx[v*3]); v++;
      }
    } // end of for(i)
    glEnd();
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
    HASH_ENTRY(const size_t t =0, const size_t o =0) : tri(t), off(o) {}
  };

  TriaSmoother(const float tolerance =0.f) : cosTolerance(tolerance) {
    if ( cosTolerance < 0.f ) cosTolerance = 0.f;
    if ( cosTolerance > 0.99f ) cosTolerance = 0.99f;
  }
  ~TriaSmoother() {}

private:
  std::deque<HASH_ENTRY> hTbl[TS_HASH_TABLE_SIZE];
  float cosTolerance;
  static size_t hashValue(const vector3 v) {
    return (size_t)fabs(((v[0]*283+v[1])*283)+v[2]) % TS_HASH_TABLE_SIZE;
  }

  void hashInsert(const vector3 v, const size_t t, const size_t o) {
    size_t h = hashValue(v);
    HASH_ENTRY hh(t, o);
    hTbl[h].push_back(hh);
  }
};

VFR_BOOL TriaSmoother::SmoothNorm(int nV, vector3* vtx, int nN, vector3* normal)
{
  size_t i;
  for ( i = 0; i < TS_HASH_TABLE_SIZE; i++ )
    hTbl[i].clear();

  size_t numV = nV;
  size_t numN = nV / 3;
  if ( numV < 3 || numN < 1 ) return VFR_FALSE;
  if ( numN < numV / 3 ) return VFR_FALSE; // Normals not generated

  vector3* newNV = (vector3*)malloc(sizeof(vector3)*numV);
  if ( ! newNV ) return VFR_FALSE;
  vector3* pv = vtx;
  vector3* pn = normal;
  for ( i = 0; i < numN; i++ ) {
    float len = (float)sqrt(pn[i][0]*pn[i][0] +
                            pn[i][1]*pn[i][1] + pn[i][2]*pn[i][2]);
    if ( len <= 1e-8f ) {
      pn[i][0] = 0.f; pn[i][1] = 0.f; pn[i][2] = 1.f;
    } else {
      pn[i][0] /= len; pn[i][1] /= len; pn[i][2] /= len;
    }
    memcpy(newNV[i*3   ], pn[i], sizeof(vector3));
    memcpy(newNV[i*3 +1], pn[i], sizeof(vector3));
    memcpy(newNV[i*3 +2], pn[i], sizeof(vector3));
  }

  // create table
  for ( i = 0; i < numV/3; i++ ) {
    hashInsert(pv[i*3   ], i, 0);
    hashInsert(pv[i*3 +1], i, 1);
    hashInsert(pv[i*3 +2], i, 2);
  }

  // smooth
  for ( i = 0; i < TS_HASH_TABLE_SIZE; i++ ) {
    while ( ! hTbl[i].empty() ) {
      std::deque<HASH_ENTRY> vset;
      std::deque<HASH_ENTRY>::iterator it = hTbl[i].begin();
      CES::Vec3<float> nn, vv;
      float cs;

      vv[0] = pv[it->tri*3 + it->off][0];
      vv[1] = pv[it->tri*3 + it->off][1];
      vv[2] = pv[it->tri*3 + it->off][2];
      nn[0] = pn[it->tri][0];
      nn[1] = pn[it->tri][1];
      nn[2] = pn[it->tri][2];
      
      it++;
      while ( it != hTbl[i].end() ) {
        if ( fabs(pv[it->tri*3 + it->off][0] - vv[0]) < 1e-6 &&
             fabs(pv[it->tri*3 + it->off][1] - vv[1]) < 1e-6 &&
             fabs(pv[it->tri*3 + it->off][2] - vv[2]) < 1e-6 ) {
          cs = CES::Vec3<float>(pn[it->tri]) | nn;
          if ( fabs(cs) > cosTolerance ) {
            vset.push_back(*it);
            it = hTbl[i].erase(it);
            continue;
          }
        }
        it++;
      } // end of while(it)

      if ( vset.size() == 0 ) {
        hTbl[i].erase(hTbl[i].begin());
        continue;
      }
      
      /* average the normal */
      for ( it = vset.begin(); it != vset.end(); it++ ) {
        nn[0] += pn[it->tri][0];
        nn[1] += pn[it->tri][1];
        nn[2] += pn[it->tri][2];
      } // end of for(it)
      nn.UnitVec();

      /* put it back */
      it = hTbl[i].begin();
      newNV[it->tri*3 + it->off][0] = nn[0];
      newNV[it->tri*3 + it->off][1] = nn[1];
      newNV[it->tri*3 + it->off][2] = nn[2];
      for ( it = vset.begin(); it != vset.end(); it++ ) {
        newNV[it->tri*3 + it->off][0] = nn[0];
        newNV[it->tri*3 + it->off][1] = nn[1];
        newNV[it->tri*3 + it->off][2] = nn[2];
      } // end of for(it)

      hTbl[i].erase(hTbl[i].begin());
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
    TriaSmoother smoother(0.25f);
    return smoother.SmoothNorm(nv, (vector3*)vtx, nn, (vector3*)normal);
  }
  return VFR_TRUE;
}
