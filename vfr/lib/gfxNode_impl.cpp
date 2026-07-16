/*
vfr scene-graph library

Copyright(c) YoH, 2026, All Right Reserved.
*/

#include "gfx_impl.h"

enum SymbolType {SYM_NORMAL =0, SYM_PLUS, SYM_CROSS,
		 SYM_CIRCLE, SYM_CIRCFILL, SYM_SQUARE, SYM_SQUAFILL,
		 SYM_TRIANGLE, SYM_TRIAFILL};


//---------------------- gfxNode_DrawPoints ----------------------
VFR_API int gfxNode_DrawPoints(int nv, float* vtx,
			       int nc, float* color,
			       int sym, int fbk)
{
  // bit patterns for point symbol
  const GLubyte symbolBits[][8] = {
    { 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 }, // Blank(failsafe)
    { 0x18, 0x18, 0x18, 0xff, 0xff, 0x18, 0x18, 0x18 }, // Plus
    { 0x81, 0x42, 0x24, 0x18, 0x18, 0x24, 0x42, 0x81 }, // Cross
    { 0x3c, 0x42, 0x81, 0x81, 0x81, 0x81, 0x42, 0x3c }, // Circle
    { 0x3c, 0x7e, 0xff, 0xff, 0xff, 0xff, 0x7e, 0x3c }, // Circle(Filled)
    { 0xff, 0x81, 0x81, 0x81, 0x81, 0x81, 0x81, 0xff }, // Square
    { 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff }, // Square(Filled)
    { 0xff, 0x81, 0x42, 0x42, 0x24, 0x24, 0x18, 0x18 }, // Triangle
    { 0xff, 0xff, 0x7e, 0x7e, 0x3c, 0x3c, 0x18, 0x18 }  // Triangle(Filled)
  };
  const GLsizei PT_SYM_WIDTH = 8;
  const GLsizei PT_SYM_HEIGHT = 8;
  const GLfloat PT_SYM_WIDTH2 = 4.f;
  const GLfloat PT_SYM_HEIGHT2 = 4.f;
  
  if ( nv < 1 || ! vtx ) return 0;
  if ( nc > 0 && ! color ) return 0;

  int i;
  if ( fbk ) {
    float vcolor[4];
    glBegin(GL_POINTS);
    for ( i = 0; i < nv; i++ ) {
      id_to_rgba(i+1, vcolor); // offset id
      glColor4fv(vcolor);
      glVertex3fv(&vtx[i*3]);
    } // end of for(i)
    glEnd();
  }
  else if ( sym > SYM_NORMAL && sym <= SYM_TRIAFILL ) {
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1);
    for ( i = 0; i < nv; i++ ) {
      if ( i < nc )
	glColor4fv(&color[i*4]);
      glRasterPos3fv(&vtx[i*3]);
      glBitmap(PT_SYM_WIDTH, PT_SYM_HEIGHT,
	       PT_SYM_WIDTH2, PT_SYM_HEIGHT2,
	       0.0f, 0.0f, symbolBits[sym]);
    } // end of for(i)
  }
  else {
    glBegin(GL_POINTS);
    for ( i = 0; i < nv; i++ ) {
      if ( i < nc )
	glColor4fv(&color[i*4]);
      glVertex3fv(&vtx[i*3]);
    } // end of for(i)
    glEnd();
  }

  return 1;
} // end of gfxNode_DrawPoints()


//---------------------- gfxNode_DrawLines ----------------------
VFR_API int gfxNode_DrawLines(int nv, float* vtx,
			      int nc, float* color,
			      int ctype, int fbk)
{
  if ( nv < 2 || ! vtx ) return 0;
  if ( nc > 0 && ! color ) return 0;

  int i, v, c, e, nEdge = nv / 2;
  if ( fbk ) {
    float vcolor[4];
    v = 0;
    glBegin(GL_LINES);
    for ( e = 0; e < nEdge; e++ ) {
      id_to_rgba(e+1, vcolor); // offset id
      glColor4fv(vcolor);
      for ( i = 0; i < 2; i++ ) {
	glVertex3fv(&vtx[v*3]); v++;
      }
    } // end of for(i)
    glEnd();
  }
  else {
    v = c = 0;
    glBegin(GL_LINES);
    for ( e = 0; e < nEdge; e++ ) {
      if ( ctype == AT_PER_FACE && c < nc ) {
	glColor4fv(&color[c*4]); c++;
      }

      for ( i = 0; i < 2; i++ ) {
	if ( ctype == AT_PER_VERTEX && c < nc ) {
	  glColor4fv(&color[c*4]); c++;
	}
	glVertex3fv(&vtx[v*3]); v++;
      } // end of for(i)
    } // end of for(e)
    glEnd(); 
  }

  return 1;
}


//---------------------- gfxNode_DrawLineStrip ----------------------
VFR_API int gfxNode_DrawLineStrip(int nv, float* vtx,
				  int nc, float* color,
				  int ctype, int loop, int fbk)
{
  if ( nv < 2 || ! vtx ) return 0;
  if ( nc > 0 && ! color ) return 0;

  int i;
  if ( fbk ) {
    float vcolor[4];
    glBegin(GL_LINES);
    for ( i = 0; i < nv -1; i++ ) {
      id_to_rgba(i+1, vcolor); // offset id
      glColor4fv(vcolor);
      glVertex3fv(&vtx[i*3]);
      glVertex3fv(&vtx[(i+1)*3]);
    } // end of for(i)
    if ( loop ) {
      id_to_rgba(nv, vcolor); // offset id
      glColor4fv(vcolor);
      glVertex3fv(&vtx[(nv-1)*3]);
      glVertex3fv(&vtx[0]);
    }
    glEnd();
  }
  else {
    i = 0;
    if ( loop )
      glBegin(GL_LINE_LOOP);
    else
      glBegin(GL_LINE_STRIP);
    while ( i < nv ) {
      if ( ctype == AT_PER_FACE || ctype == AT_PER_VERTEX ) {
	if ( i < nc )
	  glColor4fv(&color[i*4]);
      }

      glVertex3fv(&vtx[i*3]);
    } // end of while(i<nv)
    glEnd(); 
  }
  
  return 1;
}

