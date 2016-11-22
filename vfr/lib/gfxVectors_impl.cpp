/*
vfr scene-graph library

Copyright(c) RIKEN, 2008-2009, All Right Reserved.
*/

#include "gfx_impl.h"
#include "util/utilMath.h"


//---------------------- gfxVectors_DrawVectors ----------------------
VFR_API int gfxVectors_DrawVectors(int nv, float* vtx,
				   int nn, float* nml,
				   int nc, float* color,
				   float scaleFac, int showZero, int vecPos,
				   int head, float hs, float hw,
				   int fbk)
{
  enum {VECPOS_NORMAL, VECPOS_CENTER, VECPOS_TIP};

  if ( nv < 1 || ! vtx ) return 0;
  if ( nn > 0 && ! nml ) return 0;
  if ( nc > 0 && ! color ) return 0;

  register int i;
  for ( i = 0; i < nv; i++ ) {
    if ( i >= nn ) break;
    if ( i < nc )
      glColor4fv(&color[i*4]);

    CES::Vec3<float> p(&nml[i*3]); p = p * scaleFac;
    float Lp = p.Length();
    if ( Lp < EPSF ) {
      if ( showZero ) {
	glBegin(GL_POINTS);
	glVertex3fv(&vtx[i*3]);
	glEnd();
      }
      continue;
    }

    CES::Vec3<float> v(&vtx[i*3]);
    CES::Vec3<float> pit, tip;
    switch ( vecPos ) {
    case VECPOS_NORMAL:
      tip = v + p;
      pit = v;
      break;
    case VECPOS_CENTER:
      tip = v + (p * 0.5f);
      pit = v - (p * 0.5f);
      break;
    case VECPOS_TIP:
      tip = v;
      pit = v - p;
      break;
    }

    if ( fbk ) glPassThrough((GLfloat)i);
    glBegin(GL_LINES);
    glVertex3fv(pit.m_v);
    glVertex3fv(tip.m_v);
    glEnd();

    if ( fbk ) continue;
    if ( ! head ) continue;

    CES::Vec3<float> vfr(-p[1], p[0], 0.0f);
    if ( vfr[0] == 0.0f && vfr[1] == 0.0f ) vfr[0] = 1.0f;
    CES::Vec3<float> v2, v3;
    v2 = p ^ vfr;
    v3 = p ^ v2;
    v2.UnitVec(); v3.UnitVec();

    CES::Vec3<float> p1;
    p1 = p * (1.0f - hs);
    p1 = p1 + pit;
    float mw = float(hw * Lp);

    glBegin(GL_LINE_STRIP);
    glVertex3f(p1[0] +v2[0]*mw, p1[1] +v2[1]*mw, p1[2] +v2[2]*mw);
    glVertex3fv(tip.m_v);
    glVertex3f(p1[0] -v2[0]*mw, p1[1] -v2[1]*mw, p1[2] -v2[2]*mw);
    glEnd();

    glBegin(GL_LINE_STRIP);
    glVertex3f(p1[0] +v3[0]*mw, p1[1] +v3[1]*mw, p1[2] +v3[2]*mw);
    glVertex3fv(tip.m_v);
    glVertex3f(p1[0] -v3[0]*mw, p1[1] -v3[1]*mw, p1[2] -v3[2]*mw);
    glEnd();
  } // end of for(i)

  return 1;
} // end of gfxVectors_DrawVectors()

