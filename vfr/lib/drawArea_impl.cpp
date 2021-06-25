/*
vfr scene-graph library

Copyright(c) RIKEN, 2008-2009, All Right Reserved.
*/

#include "gfx_impl.h"
#include "util/utilMath.h"


//---------------------- drawArea_DragRotMatrix ----------------------
VFR_API int drawArea_DragRotMatrix(float* M,
				   const float* xPM, const float* xMM,
				   const float wz, const int* VP,
				   const int* mp0, const int* md)
{
  if ( ! M || ! xPM || ! xMM || ! VP || ! mp0 || ! md ) return 0;

  if ( VP[3] < 1 ) return 0;
  GLint l = ((VP[2] > VP[3]) ? VP[2] : VP[3]) / 2;
  if ( l < 1 ) return 0;
  const GLint vp[] = {VP[0], VP[1], VP[2], VP[3]};
  GLdouble PM[16], MM[16];
  int i;
  for ( i = 0; i < 16; i++ ) PM[i] = (GLdouble)xPM[i];
  for ( i = 0; i < 16; i++ ) MM[i] = (GLdouble)xMM[i];

  int mp1[2] = {mp0[0] + 2, mp0[1]};
  int mp2[2] = {mp0[0], mp0[1] + 2};
  GLdouble winx, winy, winz;
  GLdouble objp0[3], objp1[3], objp2[3];

  if ( wz <= 0.f || wz >= 1.f )
    winz = 0.98f;
  else
    winz = wz;

  // mp0
  winx = (GLdouble)mp0[0];
  winy = (GLdouble)vp[3] - (GLdouble)mp0[1];
  if ( gluUnProject(winx, winy, winz,  MM, PM, vp,
		    &objp0[0], &objp0[1], &objp0[2]) == GL_FALSE )
    return 0;

  // mp1
  winx = (GLdouble)mp1[0];
  winy = (GLdouble)vp[3] - (GLdouble)mp1[1];
  if ( gluUnProject(winx, winy, winz,  MM, PM, vp,
		    &objp1[0], &objp1[1], &objp1[2]) == GL_FALSE )
    return 0;

  // mp2
  winx = (GLdouble)mp2[0];
  winy = (GLdouble)vp[3] - (GLdouble)mp2[1];
  if ( gluUnProject(winx, winy, winz,  MM, PM, vp,
		    &objp2[0], &objp2[1], &objp2[2]) == GL_FALSE )
    return 0;

  CES::Vec3<float> rAx, rAy;
  float rx, ry;
  rAx[0] = objp0[0] - objp2[0];
  rAx[1] = objp0[1] - objp2[1];
  rAx[2] = objp0[2] - objp2[2];
  rx = md[0] * HALF_PI / l;
  rAy[0] = objp1[0] - objp0[0];
  rAy[1] = objp1[1] - objp0[1];
  rAy[2] = objp1[2] - objp0[2];
  ry = md[1] * HALF_PI / l;

  CES::Mat4<float> DM(M);
  if ( md[0] < md[1] ) {
    if ( md[1] )
      DM.Rotation(ry, rAy);
    if ( md[0] )
      DM.Rotation(rx, rAx);
  } else {
    if ( md[0] )
      DM.Rotation(rx, rAx);
    if ( md[1] )
      DM.Rotation(ry, rAy);
  }

  for ( i = 0; i < 16; i++ )
    M[i] = DM.m_v[i];
  return 1;
}


//---------------------- drawArea_DragTransMatrix ----------------------
VFR_API int drawArea_DragTransMatrix(float* M,
				     const float* xPM, const float* xMM,
				     const float wz, const int* VP,
				     const int* mp2, const int* md)
{
  if ( ! M || ! xPM || ! xMM || ! VP || ! mp2 || ! md ) return 0;
  if ( VP[3] < 1 ) return 0;
  GLint l = ((VP[2] > VP[3]) ? VP[2] : VP[3]) / 2;
  if ( l < 1 ) return 0;
  const GLint vp[] = {VP[0], VP[1], VP[2], VP[3]};
  GLdouble PM[16], MM[16];
  int i;
  for ( i = 0; i < 16; i++ ) PM[i] = (GLdouble)xPM[i];
  for ( i = 0; i < 16; i++ ) MM[i] = (GLdouble)xMM[i];

  int mp1[2] = {mp2[0] - md[0], mp2[1] - md[1]};
  GLdouble winx, winy, winz;
  GLdouble objp1[3], objp2[3];

  if ( wz <= 0.f || wz >= 1.f )
    winz = 0.98f;
  else
    winz = wz;

  // mp1
  winx = (GLdouble)mp1[0];
  winy = (GLdouble)vp[3] - (GLdouble)mp1[1];
  if ( gluUnProject(winx, winy, winz,  MM, PM, vp,
		    &objp1[0], &objp1[1], &objp1[2]) == GL_FALSE )
    return 0;

  // mp2
  winx = (GLdouble)mp2[0];
  winy = (GLdouble)vp[3] - (GLdouble)mp2[1];
  if ( gluUnProject(winx, winy, winz,  MM, PM, vp,
		    &objp2[0], &objp2[1], &objp2[2]) == GL_FALSE )
    return 0;

  CES::Mat4<float> DM(M);
  DM.Translate(CES::Vec3<float>(objp2[0]-objp1[0],
				objp2[1]-objp1[1],
				objp2[2]-objp1[2]));
  for ( i = 0; i < 16; i++ )
    M[i] = DM.m_v[i];
  return 1;
}


//---------------------- drawArea_DragScaleMatrix ----------------------
VFR_API int drawArea_DragScaleMatrix(float* M,
				     const int* VP,
				     const int* mp0, const int* md)
{
  if ( ! M || ! VP || ! mp0 || ! md ) return 0;
  if ( VP[3] < 1 ) return 0;
  float s;
  if ( md[1] < 0 )
    s = -md[1] / (VP[1] * 0.5) + 1.0;
  else if ( md[1] > 0 )
    s = -0.5 * md[1] / (VP[1] * 0.5) + 1.0;
  else
    return 0;
  
  CES::Mat4<float> DM(M);
  DM.Scale(CES::Vec3<float>(s, s, s));
  
  int i;
  for ( i = 0; i < 16; i++ )
    M[i] = DM.m_v[i];
  return 1;
}

