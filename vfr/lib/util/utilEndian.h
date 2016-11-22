/*
 * CES Utilities
 *
 * Copyright(c) FUJITSU NAGANO SYSTEMS ENGINEERING LIMITED
 * 	CES Project, 2002-2005, All Right Reserved.
 */

#ifndef _CES_UTIL_ENDIAN_H_
#define _CES_UTIL_ENDIAN_H_

#ifdef _WIN32
#include <io.h>
#include <fcntl.h>
#else
#include "unistd.h"
#endif
#include <stdio.h>
#include <stdlib.h>
#include <istream>
#if defined(sgi) || defined(sparc)
#include <sys/types.h>
#include <arpa/nameser.h>
#endif
#ifdef _WIN32
#define LITTLE_ENDIAN 1234
#define BIG_ENDIAN 4321
#define BYTE_ORDER LITTLE_ENDIAN
#endif


#ifndef BSWAP16
#define BSWAP_X_16(x) \
  ((((x) & 0xff00) >> 8) | (((x) & 0x00ff) << 8))
#define BSWAP16(x) \
  {register unsigned short& _x_v = (unsigned short&)(x); \
   _x_v = BSWAP_X_16(_x_v);}
#endif // BSWAP16

#ifndef SBSWAPVEC
#define SBSWAPVEC(a,n) do{register int _i; \
  for(_i=0;_i<(n);_i++){BSWAP16(a[_i]);} \
}while(0)
#endif // SBSWAPVEC

#ifndef BSWAP32
#define BSWAP_X_32(x) \
  ((((x) & 0xff000000) >> 24) | (((x) & 0x00ff0000) >>  8) | \
   (((x) & 0x0000ff00) <<  8) | (((x) & 0x000000ff) << 24))
#define BSWAP32(x) \
  {register unsigned int& _x_v = (unsigned int&)(x); \
   _x_v = BSWAP_X_32(_x_v);}
#endif // BSWAP32

#ifndef BSWAPVEC
#define BSWAPVEC(a,n) do{register int _i; \
  for(_i=0;_i<(n);_i++){BSWAP32(a[_i]);} \
}while(0)
#endif // BSWAPVEC

#ifndef BSWAP64
#define BSWAP_X_64(x) \
((((x)&0xff00000000000000ull)>>56) | (((x)&0x00ff000000000000ull)>>40) | \
 (((x)&0x0000ff0000000000ull)>>24) | (((x)&0x000000ff00000000ull)>> 8) | \
 (((x)&0x00000000ff000000ull)<< 8) | (((x)&0x0000000000ff0000ull)<<24) | \
 (((x)&0x000000000000ff00ull)<<40) | (((x)&0x00000000000000ffull)<<56))
#define BSWAP64(x) \
  {register unsigned long long& _x_v = (unsigned long long&)(x); \
   _x_v = BSWAP_X_64(_x_v);}
#endif // BSWAP64

#ifndef LBSWAPVEC
#define LBSWAPVEC(a,n) do{register int _i; \
  for(_i=0;_i<(n);_i++){BSWAP64(a[_i]);} \
}while(0)
#endif // LBSWAPVEC


namespace CES {
  typedef enum {UnKnown =0, Match, UnMatch} EMatchType;

  inline EMatchType MatchEndian(FILE* fp, const int magick) {
    EMatchType ret = UnKnown;
    if ( ! fp ) return ret;
    long here = ftell(fp);
    if ( here < 0 ) return ret;

    union {char cBuff[4]; int iBuff;} readBuf;
    if ( fread(readBuf.cBuff, 4, 1, fp) < 1 ) return ret;

    if ( readBuf.iBuff == magick )
      ret = Match;
    else {
      BSWAP32(readBuf.iBuff);
      if ( readBuf.iBuff == magick )
	ret = UnMatch;
    }
    (void)fseek(fp, here, SEEK_SET);
    return ret;
  }

  inline EMatchType MatchEndian(int fd, const int magick) {
    EMatchType ret = UnKnown;
    if ( fd < 0 ) return ret;
  
    union {char cBuff[4]; int iBuff;} readBuf;
#ifdef _WIN32
    if ( _read(fd, readBuf.cBuff, 4) < 4 ) return ret;
#else
    if ( read(fd, readBuf.cBuff, 4) < 4 ) return ret;
#endif
    if ( readBuf.iBuff == magick )
      ret = Match;
    else {
      BSWAP32(readBuf.iBuff);
      if ( readBuf.iBuff == magick )
	ret = UnMatch;
    }
#ifdef _WIN32
    (void)_lseek(fd, -4, SEEK_CUR);
#else
    (void)lseek(fd, -4, SEEK_CUR);
#endif
    return ret;
  }

  inline EMatchType MatchEndian(std::istream& is, const int magick) {
    EMatchType ret = UnKnown;
    union {char cBuff[4]; int iBuff;} readBuf;
    std::ios::pos_type here = is.tellg();

    is.read(readBuf.cBuff, 4);
    if ( ! is.good() ) return ret;

    if ( readBuf.iBuff == magick )
      ret = Match;
    else {
      BSWAP32(readBuf.iBuff);
      if ( readBuf.iBuff == magick )
	ret = UnMatch;
    }
    is.seekg(here);

    return ret;
  }

  inline bool BigEndianSys() {return (BYTE_ORDER != LITTLE_ENDIAN);}
  inline bool LittleEndianSys() {return (BYTE_ORDER == LITTLE_ENDIAN);}
}; // end of namespace CES

#endif // _CES_UTIL_ENDIAN_H_

