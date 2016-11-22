/*
vfr scene-graph library

Copyright(c) RIKEN, 2008-2009, All Right Reserved.
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

#endif // _GFX_IMPL_H_
