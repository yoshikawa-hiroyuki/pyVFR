/*
vsn visualization library

Copyright(c) YoH, 2026, All Right Reserved.
*/
#ifndef _VSN_IMPL_H_
#define _VSN_IMPL_H_

#include "obj_impl.h"

namespace VSN {
  // double vertex type
  typedef double DVec3[3];
  typedef double DVec4[4];
  typedef double DMat3[3][3];
};

inline void* Allocate(size_t size) {return malloc(size);}
inline void  DeAllocate(void *ptr) {free(ptr);}
inline void* CeAllocate(size_t nelem,size_t elsize) {
  return calloc(nelem, elsize);}
inline void* ReAllocate(void *ptr,size_t size) {return realloc(ptr, size);}
inline char* StrDuplicate(const char *string) {return strdup(string);}

#endif // _VSN_IMPL_H_
