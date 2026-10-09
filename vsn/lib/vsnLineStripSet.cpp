//
// vsnLineStripSet
//
#include "gfx_impl.h"
#include "vsn_impl.h"

using namespace std;
using namespace VSN;

//------------------------------------------------------------------------
// interfaces for ctypes
//------------------------------------------------------------------------

VFR_API int VsnDrawPointSet(int nv, float* vtx,
			    int nc, float* color, int fbk)
{
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
}

VFR_API int VsnDrawLineStripSet(int nv, float* vtx,
				int nc, float* color,
				int loop, int fbk)
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
      if ( i < nc )
	glColor4fv(&color[i*4]);

      glVertex3fv(&vtx[i*3]);

      i++;
    } // end of while(i<nv)
    glEnd(); 
  }
  
  return 1;
}
