/*
vfr scene-graph library

Copyright(c) RIKEN, 2008-2009, All Right Reserved.
*/
#ifndef _VFR_IMPL_H_
#define _VFR_IMPL_H_

#ifdef __APPLE__
#ifndef unix
#define unix
#endif
#include <stdlib.h>
#else // !__APPLE__
#include <malloc.h>
#endif // __APPLE__
#include <stdio.h>
#include <string.h>
#include <math.h>
#ifdef WIN32
#pragma warning(disable:4819)
#define _CRT_SECURE_NO_WARNINGS
#endif // WIN32

/* Define NONE symbol */
#ifndef NONE
#define NONE  0
#endif

/* Define Small numeric */
#ifndef EPSF
#define EPSF  1e-8
#endif

/* Define PI/2 */
#ifdef  M_PI_2
#define HALF_PI    M_PI_2
#else
#define HALF_PI    1.5707963
#endif

/* Define Boolean */
#define VFR_FALSE 0
#define VFR_TRUE !VFR_FALSE
typedef int VFR_BOOL;

#define VFR_INVALID -1

/* Define vector type */
typedef float vector4[4];
typedef float vector3[3];
typedef float vector2[2];


/* Define API prefix (with dll export) */
#ifdef WIN32
#define VFR_API extern "C" __declspec(dllexport)
#define VFR_CLASS class __declspec(dllexport)
#else
#define VFR_API extern "C"
#define VFR_CLASS class
#endif

#endif // _VFR_IMPL_H_
