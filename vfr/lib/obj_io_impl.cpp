/*
vfr scene-graph library

Copyright(c) RIKEN, 2008-2009, All Right Reserved.
*/
#include <iostream>
#include <fstream>

#include "obj_impl.h"
#include "util/utilPath.h"
#include "util/utilGetLine.h"
#include "util/utilEndian.h"
#include "util/utilTessel.h"

#define BUFFLEN 256


// util classes
struct V3 {
  float xyz[3];
  V3() {xyz[0]=xyz[1]=xyz[2]=0.f;}
  V3(const V3& org) {*this = org;}
  void operator=(const V3& org) {
    memcpy(xyz, org.xyz, sizeof(float)*3);
  }
};
struct V2 {
  float uv[2];
  V2() {uv[0]=uv[1]=0.f;}
  V2(const V3& org) {*this = org;}
  void operator=(const V2& org) {
    memcpy(uv, org.uv, sizeof(float)*2);
  }
};
struct I3 {
  int idx[3];
  I3() {idx[0]=idx[1]=idx[2]=0;}
  I3(const I3& org) {*this = org;}
  void operator=(const I3& org) {
    memcpy(idx, org.idx, sizeof(int)*3);
  }
  bool IsValid() const {
    return (idx[0]>=0 && idx[1]>=0 && idx[2]>=0);
  }
};
struct Facet {
  float p[3][3];
  float nv[3];
  unsigned short ext;
  unsigned short _dummy; // for padding
  Facet() : ext(0), _dummy(0) {
    memset(p, 0, sizeof(float)*9); memset(nv, 0, sizeof(float)*3);
  }
  Facet(const Facet& org) {*this = org;}
  void operator=(const Facet& org) {
    memcpy(p, org.p, sizeof(float)*9); memcpy(nv, org.nv, sizeof(float)*3);
    ext = org.ext;
  }
};

// iostream operators
inline std::istream&
operator >>(std::istream& is, V3& v) {
  return is >> v.xyz[0] >> v.xyz[1] >> v.xyz[2];
}
inline std::istream&
operator >>(std::istream& is, V2& v) {
  return is >> v.uv[0] >> v.uv[1];
}
inline std::istream&
operator >>(std::istream& is, I3& v) {
  is >> v.idx[0];
  if ( is.get() == '/' ) {
    int pc = is.peek();
    if ( pc == '/' ) { // case of '//'
      is.get();
      if ( isdigit(is.peek()) )
        is >> v.idx[2];
      return is;
    }
    else if ( ! isdigit(pc) )
      return is;
    is >> v.idx[1];
    if ( is.get() == '/' ) {
      if ( isdigit(is.peek()) )
        is >> v.idx[2];
    }
  }
  return is;
}

// Wavefront OBJ loader
VFR_API VFR_BOOL ObjData_LoadOBJ(void* p, const char* cpath) {
  using namespace std;
  int i, j;
  string buff;
  deque<V3> m_vl;
  deque<V3> m_nl;
  deque<V2> m_tl;
  deque<I3> m_vlIdx;
  deque<I3> m_nlIdx;
  deque<I3> m_tlIdx;

  ObjData* pnode = (ObjData*)p;
  if ( ! pnode ) return VFR_FALSE;

  //// OPEN INFILE ////
#ifdef WIN32
  locale::global(locale("japanese"));
#endif // WIN32
  string path(cpath);
  ifstream sf(path.c_str());
  if ( ! sf ) return VFR_FALSE;

  //// READ INFILE ////
  i = 0;
  string keyword, token;
  while ( ! sf.eof() ) {
    CES::GetLine(sf, buff);
    if ( buff.size() < 1 ) continue;

    // continued line
    while ( buff[buff.size() -1] == '\\' ) {
      buff[buff.size() -1] = ' ';
      string buff2;
      CES::GetLine(sf, buff2);
      if ( sf.eof() ) break;
      buff.append(buff2);
    }

    // string stream from read buff
    istringstream iss(buff);

    // get keyword
    iss >> keyword;
    if ( keyword.empty() ) continue;

    // keyword is 'v' --- vertex ---
    if ( keyword == "v" ) {
      V3 vert;
      iss >> vert;
      m_vl.push_back(vert);
      continue;
    } // End of if keyword is 'v'

    // keyword is 'vn' --- vertex normal ---
    if ( keyword == "vn" ) {
      V3 norm;
      iss >> norm;
      m_nl.push_back(norm);
      continue;
    } // End of if keyword is 'vn'

    // keyword is 'vt' --- texture coord ---
    if ( keyword == "vt" ) {
      V2 texc;
      iss >> texc;
      m_tl.push_back(texc);
      continue;
    } // End of if keyword is 'vt'

    // keyword is 'f' --- face ---
    if ( keyword == "f" ) {
      deque<I3> idxLst;
      I3 wkf, face;

      iss >> wkf;
      while ( 1 ) {
        if ( wkf.idx[0] > 0 ) face.idx[0] = wkf.idx[0] -1;
        else if ( wkf.idx[0] < 0 ) face.idx[0] = m_vl.size() + wkf.idx[0];
        else face.idx[0] = -1;

        if ( wkf.idx[1] > 0 ) face.idx[1] = wkf.idx[1] -1;
        else if ( wkf.idx[1] < 0 ) face.idx[1] = m_tl.size() + wkf.idx[1];
        else face.idx[1] = -1;

        if ( wkf.idx[2] > 0 ) face.idx[2] = wkf.idx[2] -1;
        else if ( wkf.idx[2] < 0 ) face.idx[2] = m_nl.size() + wkf.idx[2];
        else face.idx[2] = -1;

        idxLst.push_back(face);

        if ( iss.eof() ) break;
        iss >> wkf;
      } // end of while

      if ( idxLst.size() < 3 )
        ;
      else if ( idxLst.size() == 3 ) {
        face.idx[0] = idxLst[0].idx[0];
        face.idx[1] = idxLst[1].idx[0];
        face.idx[2] = idxLst[2].idx[0];
        if ( ! face.IsValid() ) continue;
        m_vlIdx.push_back(face);
        face.idx[0] = idxLst[0].idx[1];
        face.idx[1] = idxLst[1].idx[1];
        face.idx[2] = idxLst[2].idx[1];
        m_tlIdx.push_back(face);
        face.idx[0] = idxLst[0].idx[2];
        face.idx[1] = idxLst[1].idx[2];
        face.idx[2] = idxLst[2].idx[2];
        m_nlIdx.push_back(face);
      }
      else { // over 3 vertices, do tesselation
        Vector3F* pvtx = new Vector3F[idxLst.size()];
        int idx;
        for ( idx = 0; idx < idxLst.size(); idx++ )
          pvtx[idx] = m_vl[idxLst[idx].idx[0]].xyz;
        utilTessel tessel;
        deque<Vector3I> tessedLst
          = tessel.Triangulate(pvtx, idxLst.size());
        delete[] pvtx;

        if ( tessedLst.size() > 0 ) { // tesselation succeed
          for ( idx = 0; idx < tessedLst.size(); idx ++ ) {
            face.idx[0] = idxLst[tessedLst[idx].m_v[0]].idx[0];
            face.idx[1] = idxLst[tessedLst[idx].m_v[1]].idx[0];
            face.idx[2] = idxLst[tessedLst[idx].m_v[2]].idx[0];
            if ( ! face.IsValid() )
              break;
            m_vlIdx.push_back(face);
            face.idx[0] = idxLst[tessedLst[idx].m_v[0]].idx[1];
            face.idx[1] = idxLst[tessedLst[idx].m_v[1]].idx[1];
            face.idx[2] = idxLst[tessedLst[idx].m_v[2]].idx[1];
            m_tlIdx.push_back(face);
            face.idx[0] = idxLst[tessedLst[idx].m_v[0]].idx[2];
            face.idx[1] = idxLst[tessedLst[idx].m_v[1]].idx[2];
            face.idx[2] = idxLst[tessedLst[idx].m_v[2]].idx[2];
            m_nlIdx.push_back(face);
          } // end of for(idx)
        }
        else { // tesselation failed
          I3 texc, norm;
          face.idx[0] = idxLst[0].idx[0];
          face.idx[1] = idxLst[1].idx[0];
          face.idx[2] = idxLst[2].idx[0];
          if ( ! face.IsValid() )
            continue;
          m_vlIdx.push_back(face);
          texc.idx[0] = idxLst[0].idx[1];
          texc.idx[1] = idxLst[1].idx[1];
          texc.idx[2] = idxLst[2].idx[1];
          m_tlIdx.push_back(texc);
          norm.idx[0] = idxLst[0].idx[2];
          norm.idx[1] = idxLst[1].idx[2];
          norm.idx[2] = idxLst[2].idx[2];
          m_nlIdx.push_back(norm);

          for ( idx = 3; idx < idxLst.size(); idx++ ) {
            face.idx[1] = face.idx[2];
            face.idx[2] = idxLst[idx].idx[0];
            if ( ! face.IsValid() )
              break;
            m_vlIdx.push_back(face);
            texc.idx[1] = texc.idx[2];
            texc.idx[2] = idxLst[idx].idx[1];
            m_tlIdx.push_back(texc);
            norm.idx[1] = norm.idx[2] ;
            norm.idx[2] = idxLst[idx].idx[2];
            m_nlIdx.push_back(norm);
          } // end of for(idx)
        }
      }

      continue;
    } // End of if keyword is 'f'
  } // End of while(1)

  //// SET ObjData ////
  bool nlExist = ( m_nl.size() > 0 );
  pnode->alcVerts(m_vlIdx.size() * 3);
  if ( nlExist )
    pnode->alcNormals(m_nlIdx.size() * 3);

  // set verts...
  vector3* pv = pnode->_verts;
  vector3* pn = pnode->_normals;
  for ( i = 0; i < m_vlIdx.size(); i++ ) {
    j = i*3;
    memcpy(pv[j  ], m_vl[m_vlIdx[i].idx[0]].xyz, sizeof(vector3));
    memcpy(pv[j+1], m_vl[m_vlIdx[i].idx[1]].xyz, sizeof(vector3));
    memcpy(pv[j+2], m_vl[m_vlIdx[i].idx[2]].xyz, sizeof(vector3));

    if ( nlExist && m_nlIdx[i].IsValid() ) {
      memcpy(pn[j  ], m_nl[m_nlIdx[i].idx[0]].xyz, sizeof(vector3));
      memcpy(pn[j+1], m_nl[m_nlIdx[i].idx[1]].xyz, sizeof(vector3));
      memcpy(pn[j+2], m_nl[m_nlIdx[i].idx[2]].xyz, sizeof(vector3));
    }
  } // end of for(i)

  return VFR_TRUE;
}

// STL/Ascii loader
VFR_API VFR_BOOL ObjData_LoadSLA(void* p, const char* path) {
  using namespace std;
  deque<Facet> fl;
  char buff[BUFFLEN];
  char ds[64];
  
  ObjData* pnode = (ObjData*)p;
  if ( ! pnode ) return VFR_FALSE;

  //// OPEN INFILE ////
#ifdef WIN32
  locale::global(locale("japanese"));
#endif // WIN32
  ifstream sf(path);
  if ( ! sf )  {
    return VFR_FALSE;
  }

  //// READ INFILE ////
  int vcount = 0;
  Facet face;

  while ( ! sf.eof() ) {
    CES::GetLine(sf, buff, BUFFLEN);

    // beginning of the face
    if ( strstr(buff, "facet normal") || strstr(buff, "FACET NORMAL") ) {
      float nv[3];
      if ( sscanf(buff, "%s %s %f %f %f",
                  ds, ds, &nv[0], &nv[1], &nv[2]) < 5 ) {
        continue;
      }
      memcpy(face.nv, nv, sizeof(float)*3);
      continue;
    }
    if ( strstr(buff, "outer loop") || strstr(buff, "OUTER LOOP") ) {
      vcount = 0;
      continue;
    }

    // vertex
    if ( strstr(buff, "vertex") || strstr(buff, "VERTEX") ) {
      float v[3];
      if ( sscanf(buff, "%s %f %f %f", ds, &v[0], &v[1], &v[2]) < 4 ) {
        continue;
      }
      if ( vcount < 0 ) continue;
      if ( vcount < 2 ) {
        memcpy(face.p[vcount++], v, sizeof(float)*3);
      } else if ( vcount == 2 ) {
        memcpy(face.p[vcount++], v, sizeof(float)*3);
        fl.push_back(face);
      } else {
        memcpy(face.p[1], face.p[2], sizeof(float)*3);
        memcpy(face.p[2], v, sizeof(float)*3);
        fl.push_back(face);
        vcount++;
      }
      continue;
    } // End of 'vertex' line

    // end of the face
    if ( strstr(buff, "endloop") || strstr(buff, "ENDLOOP") ) {
      vcount = -1;
      continue;
    }

  } // End of while(1)

  // SET ObjData
  int nVtx = fl.size() * 3;
  pnode->alcVerts(nVtx);
  pnode->alcNormals(nVtx);
  vector3* pv = pnode->_verts;
  vector3* pn = pnode->_normals;

  int i, j;
  for ( i = 0; i < fl.size(); i++ ) {
    j = i*3;
    memcpy(pv[j  ], fl[i].p[0], sizeof(vector3));
    memcpy(pv[j+1], fl[i].p[1], sizeof(vector3));
    memcpy(pv[j+2], fl[i].p[2], sizeof(vector3));
    memcpy(pn[j  ], fl[i].nv, sizeof(vector3));
    memcpy(pn[j+1], fl[i].nv, sizeof(vector3));
    memcpy(pn[j+2], fl[i].nv, sizeof(vector3));
  } // end of for(i)

  return VFR_TRUE;
}

// STL/Binary loader
VFR_API VFR_BOOL ObjData_LoadSLB(void* p, const char* path) {
  using namespace std;
  deque<Facet> fl;
  int nFacet;
  int i, j;
  Facet face;
  union {
    char cb[50];
    float fb[4][3];
  } ub;
  unsigned short* p_ext = (unsigned short*)(&ub.cb[48]);

  ObjData* pnode = (ObjData*)p;
  if ( ! pnode ) return VFR_FALSE;

  // endian conversion
  bool eCvt = false;

  // open file
  FILE* fp = fopen(path, "rb");
  if ( ! fp ) {
    return VFR_FALSE;
  }

  // skip header (80bytes);
  if ( fseek(fp, 80, SEEK_SET) != 0 ) {
    return VFR_FALSE;
  }

  // main loop
  while ( 1 ) {
    // read #of facet
    if ( fread(&nFacet, 4, 1, fp) < 1 ) break;
    if ( nFacet > 500000000 || nFacet < 0 ) {
      BSWAP32(nFacet);
      if ( nFacet > 500000000 || nFacet < 0 )
	return VFR_FALSE;
      eCvt = true;
    }

    // facet loop
    for ( i = 0; i < nFacet; i++ ) {
      // read to buffer
      fread(ub.cb, 1, 50, fp);
      if ( feof(fp) ) break;

      // endian convert
      if ( eCvt ) {
        BSWAPVEC(ub.fb[0], 12);
        SBSWAPVEC(p_ext, 1);
      }

      // copy to face
      memcpy(face.nv, ub.fb[0], sizeof(float)*3);
      memcpy(face.p, ub.fb[1], sizeof(float)*9);
      face.ext = (*p_ext);

      // push to list
      fl.push_back(face);
    } // end of for(i)
  } // end of while(1)

  // create Node
  int nVtx = fl.size() * 3;
  if ( ! pnode->alcVerts(nVtx) || ! pnode->alcNormals(nVtx) ) {
    return VFR_FALSE;
  }
  vector3* pv = pnode->_verts;
  vector3* pn = pnode->_normals;

  for ( i = 0; i < fl.size(); i++ ) {
    j = i*3;
    memcpy(pv[j  ], fl[i].p[0], sizeof(vector3));
    memcpy(pv[j+1], fl[i].p[1], sizeof(vector3));
    memcpy(pv[j+2], fl[i].p[2], sizeof(vector3));
    memcpy(pn[j  ], fl[i].nv, sizeof(vector3));
    memcpy(pn[j+1], fl[i].nv, sizeof(vector3));
    memcpy(pn[j+2], fl[i].nv, sizeof(vector3));
  } // end of for(i)

  if ( pnode->alcIndices(fl.size()) ) {
    int* pind = pnode->_indices;
    for ( i = 0; i < fl.size(); i++ )
      pind[i] = (const int)fl[i].ext;
  }

  return VFR_TRUE;
}

VFR_API VFR_BOOL ObjData_IsStlAscii(const char* cpath) {
  using namespace std;
#ifdef WIN32
  locale::global(locale("japanese"));
#endif // WIN32
  char buff[BUFFLEN];
  ifstream sf(cpath);
  if ( ! sf ) return VFR_FALSE;
  CES::GetLine(sf, buff, BUFFLEN);
  if ( sf.eof() ) return VFR_FALSE;
  if ( strstr(buff, "solid") )
    return VFR_TRUE;
  return VFR_FALSE;
}

VFR_API VFR_BOOL ObjData_Load(void* p, const char* cpath, const char* cfmt) {
  using namespace std;
  ObjData* po = (ObjData*)p;
  if ( ! po ) return VFR_FALSE;
  if ( ! cpath || strlen(cpath) < 1 ) return VFR_FALSE;
  string path(cpath);

  string fmt;
  if ( ! cfmt || strlen(cfmt) < 1 ) {
    string sfx[] = {".obj", ".wfo", ".stl", ".sla", ".stla", ".slb", ".stlb",
		    ".OBJ", ".WFO", ".STL", ".SLA", ".STLA", ".SLB", ".STLB"};
    size_t i;
    for ( i = 0; i < sizeof(sfx)/sizeof(string*); i++ ) {
      if ( path.rfind(sfx[i]) != string::npos ) break;
    } // end of for(i)
    switch ( i ) {
    case 0: case 1: case 7: case 8:
      fmt = "obj"; break;
    case 3: case 4: case 10: case 11:
      fmt = "sla"; break;
    case 5: case 6: case 12: case 13:
      fmt = "slb"; break;
    case 2: case 9:
      if ( ObjData_IsStlAscii(cpath) ) fmt = "sla";
      else fmt = "slb";
      break;
    default:
      return VFR_FALSE;
    }
  }
  else fmt = cfmt;

  VFR_BOOL ret = VFR_FALSE;
  if ( fmt == "obj" )
    ret = ObjData_LoadOBJ(p, cpath);
  else if ( fmt == "sla" )
    ret = ObjData_LoadSLA(p, cpath);
  else if ( fmt == "slb" )
    ret = ObjData_LoadSLB(p, cpath);
  return ret;
}
