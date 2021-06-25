/*
vfr scene-graph library

Copyright(c) RIKEN, 2008-2009, All Right Reserved.
*/

#include "gfx_impl.h"
#include "gfxLetters_data.h"

enum FontType{FONT_LINE =0, FONT_HELVETICA, FONT_TIMESROMAN};


//---------------------- gfxLetters_GetTextWidth ----------------------
VFR_API double gfxLetters_GetTextWidth(const int font,
				       const char* textBuf,
				       const double spaceRate)
{
  GLfloat* fontSize;
  FONTDATA* fontData;
  GLfloat fontScale = 1.0f;
  switch ( font ) {
  case FONT_LINE:
    fontSize = line_fontSize;
    fontData = line_fontData;
    fontScale = LINE_STROKE_SCALE;
    break;
  case FONT_HELVETICA:
    fontSize = helv_fontSize;
    fontData = helv_fontData;
    fontScale = FILLED_SCALE;
    break;
  case FONT_TIMESROMAN:
    fontSize = times_fontSize;
    fontData = times_fontData;
    fontScale = FILLED_SCALE;
    break;
  default:
    return 0.0;
  }
  if ( ! textBuf ) return 0.0;
  float tw = 0.f;
  float maxw = 0.f;
  int textLen = strlen(textBuf);
  int i, j;
  for ( i = 0; i < textLen; i++ ) {
    GLint mode;
    if ( textBuf[i] == '\n' ) {
      if ( tw > maxw ) maxw = tw;
      tw = 0.f;
      continue;
    }
    for ( j = 1; mode = fontData[textBuf[i]-32][j]; j += 3 )
      if ( mode == FONT_ADVANCE ) {
	tw += (float)fontData[textBuf[i]-32][j+1]*fontScale;
	tw += fontSize[0] * spaceRate;
      }
  } // end of for(i)
  if ( tw > maxw ) maxw = tw;
  return (double)maxw;
}


//---------------------- gfxLetters_DrawLetter ----------------------
VFR_API double gfxLetters_DrawLetter(const int font,
				     const char c,
				     const double spaceRate)
{
  if ( c < 0x20 || c > 0x7e )
    return 0.0;
  GLfloat* fontSize;
  FONTDATA* fontData;
  GLfloat fontScale = 1.0f;
  GLenum gltype;
  switch ( font ) {
  case FONT_LINE:
    fontSize = line_fontSize;
    fontData = line_fontData;
    fontScale = LINE_STROKE_SCALE;
    gltype = GL_LINE_STRIP;
    break;
  case FONT_HELVETICA:
    fontSize = helv_fontSize;
    fontData = helv_fontData;
    fontScale = FILLED_SCALE;
    gltype = GL_TRIANGLE_STRIP;
    break;
  case FONT_TIMESROMAN:
    fontSize = times_fontSize;
    fontData = times_fontData;
    fontScale = FILLED_SCALE;
    gltype = GL_TRIANGLE_STRIP;
    break;
  default:
    return 0.0;
  }
  int i = c - 0x20;
  GLint mode;
  GLfloat retv = 0.f;
  int j;
  for ( j = 1; mode = fontData[i][j]; j += 3 ) {
    if ( mode == FONT_BEGIN ) {
      glBegin(gltype);
      glVertex2f((float)fontData[i][j+1]*fontScale,
		 (float)fontData[i][j+2]*fontScale);
    } else if ( mode == FONT_NEXT ) {
      glVertex2f((float)fontData[i][j+1]*fontScale,
		 (float)fontData[i][j+2]*fontScale);
    } else if ( mode == FONT_END ) {
      glVertex2f((float)fontData[i][j+1]*fontScale,
		 (float)fontData[i][j+2]*fontScale);
      glEnd();
    } else if ( mode == FONT_ADVANCE ) {
      retv = (float)fontData[i][j+1]*fontScale + (fontSize[0]*spaceRate);
      glTranslatef(retv, (float)fontData[i][j+2]*fontScale, 0.f);
      break;
    }
  }
  return (double)retv;
}

