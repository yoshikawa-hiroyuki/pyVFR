/*
vfr scene-graph library

Copyright(c) YoH, 2026, All Right Reserved.
*/
#ifndef _GFX_IMPL_H_
#define _GFX_IMPL_H_

#include "vfr_impl.h"

/* OpenGL */
#if defined(_WIN32) && !defined(__CYGWIN__)
#define WIN32_LEAN_AND_MEAN 1
#include <windows.h>
#include <GL/gl.h>
#include <GL/glu.h>
#else // WIN32
#define GL_GLEXT_PROTOTYPES 1
#ifdef __APPLE__
#include <OpenGL/gl.h>
#include <OpenGL/glu.h>
#else
#include <GL/gl.h>
#include <GL/glu.h>
#endif
#endif // WIN32

/* Attribute type */
enum AttribType {AT_WHOLE =0, AT_PER_VERTEX, AT_PER_FACE};


//---------------------- オブジェクトID ←→ 色(RGBA)の変換 ----------------------
inline void id_to_rgba(const int i, float color[4]) {
  color[0] = (i & 0xFF) / 255.0f;
  color[1] = ((i >> 8) & 0xFF) / 255.0f;
  color[2] = ((i >> 16) & 0xFF) / 255.0f;
  color[3] = ((i >> 24) & 0xFF) / 255.0f;
}

inline int rgba_to_id(const unsigned char color[4]) {
  unsigned char r = color[0], g = color[1], b = color[2], a = color[3];
  return int(r) + (int(g) << 8) + (int(b) << 16) + (int(a) << 24);
}

#endif // _GFX_IMPL_H_
