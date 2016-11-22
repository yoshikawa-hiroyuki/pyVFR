/*
 * CES Utilities
 *
 * Copyright(c) FUJITSU NAGANO SYSTEMS ENGINEERING LIMITED
 *      CES Project, 2002-2005, All Right Reserved.
 */

#ifndef _CES_UTIL_PATH_H_
#define _CES_UTIL_PATH_H_

#include <string>
#include <sstream>
#include <deque>
#include <string.h>

namespace CES {

  inline std::string DirName(const std::string& path,
			     const char dc = '/') {
    char* name = strdup( path.c_str() );
    char* p = name;
    
    for ( ; ; ++p ) {
      if ( ! *p ) {
	if ( p > name ) {
	  char rs[2] = {dc, '\0'};
	  return rs;
	} else
	  return(".");
      }
      if ( *p != dc ) break;
    }
    
    for ( ; *p; ++p );
    while ( *--p == dc ) continue;
    *++p = '\0';
    
    while ( --p >= name )
      if ( *p == dc ) break;
    ++p;
    if ( p == name ) return(".");
    
    while ( --p >= name )
      if ( *p != dc ) break;
    ++p;
    
    *p = '\0';
    if( p == name ) {
      char rs[2] = {dc, '\0'};
      return rs;
    } else {
      std::string s( name );
      free( name );
      return s;
    }
  }
  
  inline std::string BaseName(const std::string& path,
			      const std::string& suffix = std::string(""),
			      const char dc = '/') {
    char* name = strdup( path.c_str() );
    char* p = name;
    
    for ( ; ; ++p ) {
      if ( ! *p ) {
	if ( p > name ) {
	  char rs[2] = {dc, '\0'};
	  return rs;
	} else
	  return "";
      }
      if ( *p != dc ) break;
    }
    
    for ( ; *p; ++p ) continue;
    while ( *--p == dc ) continue;
    *++p = '\0';
    
    while ( --p >= name )
      if ( *p == dc ) break;
    ++p;
    
    if ( suffix.length() > 0 ) {
      const int suffixlen = suffix.length();
      const int stringlen = strlen( p );
      if ( suffixlen < stringlen ) {
	const int off = stringlen - suffixlen;
	if ( !strcmp( p + off, suffix.c_str() ) )
	  p[off] = '\0';
      }
    }

    std::string s( p );
    free( name );
    return s;
  }

  inline std::string OmitDots(const std::string& path,
			      const char dc = '/') {
    using namespace std;
    if ( path.empty() ) return path;

    deque<string> elemLst;
    istringstream ss(path);
    std::string selStr; char c;

    // decomposition
    while ( 1 ) {
      if ( ! ss.get(c) ) {
	elemLst.push_back(selStr);
	break;
      }
      if ( c == dc ) {
	elemLst.push_back(selStr);
	selStr = "";
      } else {
	selStr += c;
      }
    } // end of while(1)

    // remove null or '.' elem
    deque<string>::iterator it;
    for ( it = elemLst.begin(); it != elemLst.end(); ) {
      if ( it->empty() || (*it) == "." )
	it = elemLst.erase(it);
      else
	it ++;
    } // end of for(it)

    // remove '..' elem
    if ( ! elemLst.empty() )
      for ( it = elemLst.begin() + 1; it != elemLst.end(); ) {
	if ( (*it) == ".." ) {
	  it = elemLst.erase(--it);
	  it = elemLst.erase(it);
	} else
	  it ++;
      } // end of for(it)

    // result
    string retPath;
    if ( path[0] == dc ) retPath = dc;
    for ( it = elemLst.begin(); it != elemLst.end(); it++ ) {
      retPath += (*it);
      if ( it != elemLst.end() -1 )
	retPath += dc;
    } // end of for(it)
    return retPath;
  }

  inline char GetDelimChar() {
#ifdef WIN32
    return '\\';
#else
    return '/';
#endif
  }

  inline void AdjustDelim(std::string& path) {
#ifdef WIN32
    const char newDelim = '\\';
    const char oldDelim = '/';
#else
    const char oldDelim = '\\';
    const char newDelim = '/';
#endif
    size_t pathLen = path.size();
    for ( register size_t i = 0; i < pathLen; i++ ) {
      if ( path[i] == oldDelim )
        path[i] = newDelim;
    } // end of for(i)
  }

  inline bool HasDrive(const std::string& path) {
    if ( path.size() < 2 ) return false;
    char x = path[0];
    if ( ((x >= 'A' && x <= 'Z' ) || (x >= 'a' && x <= 'z')) &&
         path[1] == ':' )
      return true;
    return false;
  }

  inline std::string EmitDrive(std::string& path) {
    // returns drive (ex. 'C:')
    if ( ! HasDrive(path) ) return std::string();
    std::string driveStr = path.substr(0, 2);
    path = path.substr(2);
    return driveStr;
  }

  inline bool IsAbsolute(const std::string& path) {
    std::string xpath(path);
    EmitDrive(xpath);
    return (xpath[0] == GetDelimChar());
  }

  inline std::string Concat(const std::string& path1,
			    const std::string& path2) {
    std::string xpath;
    if ( ! path1.empty() ) {
      xpath = path1;
      xpath += GetDelimChar();
    }
    xpath += path2;
    return xpath;
  }

  inline std::string Normalize(const std::string& path) {
    std::string xpath(path);
    AdjustDelim(xpath);
    std::string driveStr = EmitDrive(xpath);
    xpath = CES::OmitDots(xpath, GetDelimChar());
    if ( ! driveStr.empty() )
      xpath = driveStr + xpath;
    return xpath;
  }
}; // end of namespace CES

#endif // _CES_UTIL_PATH_H_
