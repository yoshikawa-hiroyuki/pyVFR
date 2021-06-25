/*
vfr scene-graph library

Copyright(c) RIKEN, 2008-2009, All Right Reserved.
*/

#include "gfx_impl.h"
#include "util/utilMath.h"


//---------------------- gfxMesh2D_DrawMeshFace ----------------------
VFR_API int gfxMesh2D_DrawMeshFace(int nv, float* vtx,
				   int nn, float* normal,
				   int nc, float* color,
				   int m, int n, int ntype, int ctype, int fbk)
{
  if ( nv < 1 || ! vtx ) return 0;
  if ( m * n < 1 || m * n > nv ) return 0;

  int i, j, index, findex = 0;
  if ( fbk ) {
    for ( j = 0; j < n -1; j++ ) {
      for ( i = 0; i < m -1; i++ ) {
        glPassThrough((GLfloat)findex);
        glBegin(GL_QUADS);
        glVertex3fv(&vtx[(j*m + i)*3]);
        glVertex3fv(&vtx[(j*m + i+1)*3]);
        glVertex3fv(&vtx[((j+1)*m + i+1)*3]);
        glVertex3fv(&vtx[((j+1)*m + i)*3]);
        glEnd();
        findex++;
      }
    }
    return 1;
  }

  if ( nn > 0 && ! normal ) return 0;
  if ( nc > 0 && ! color ) return 0;
  glBegin(GL_QUADS);
  for ( j = 0; j < n -1; j++ ) {
    for ( i = 0; i < m -1; i++ ) {
      if ( ctype == AT_PER_FACE && findex < nc )
        glColor4fv(&color[findex*4]);
      if ( ntype == AT_PER_FACE && findex < nn )
        glNormal3fv(&normal[findex*3]);

      // V1
      index = j*m + i;
      if ( ctype == AT_PER_VERTEX && index < nc )
        glColor4fv(&color[index*4]);
      if ( ntype == AT_PER_VERTEX && index < nn )
        glNormal3fv(&normal[index*3]);
      glVertex3fv(&vtx[index*3]);

      // V2
      index = j*m + i +1;
      if ( ctype == AT_PER_VERTEX && index < nc )
        glColor4fv(&color[index*4]);
      if ( ntype == AT_PER_VERTEX && index < nn )
        glNormal3fv(&normal[index*3]);
      glVertex3fv(&vtx[index*3]);

      // V3
      index = (j +1)*m + i +1;
      if ( ctype == AT_PER_VERTEX && index < nc )
        glColor4fv(&color[index*4]);
      if ( ntype == AT_PER_VERTEX && index < nn )
        glNormal3fv(&normal[index*3]);
      glVertex3fv(&vtx[index*3]);

      // V4
      index = (j +1)*m + i;
      if ( ctype == AT_PER_VERTEX && index < nc )
        glColor4fv(&color[index*4]);
      if ( ntype == AT_PER_VERTEX && index < nn )
        glNormal3fv(&normal[index*3]);
      glVertex3fv(&vtx[index*3]);

      findex++;
    } // end of for(i)
  } // end of for(j)
  glEnd();

  return 1;
}


//---------------------- gfxMesh2D_DrawMeshEdge ----------------------
VFR_API int gfxMesh2D_DrawMeshEdge(int nv, float* vtx,
				   int nc, float* color,
				   int m, int n, int ctype, int fbk)
{
  if ( nv < 1 || ! vtx ) return 0;
  if ( m * n < 1 || m * n > nv ) return 0;
  int i, j, index, findex;

  if ( fbk ) {
    findex = 0;

    // Holizontal Lines
    for ( j = 0; j < n; j++ ) {
      for ( i = 0; i < m -1; i++ ) {
        glPassThrough((GLfloat)findex);
        glBegin(GL_LINES);
        glVertex3fv(&vtx[(j*m + i)*3]);
        glVertex3fv(&vtx[(j*m + i+1)*3]);
        glEnd();
        findex++;
      }
    }
    // Vartical Lines
    for ( i = 0; i < m; i++ ) {
      for ( j = 0; j < n -1; j++ ) {
        glPassThrough((GLfloat)findex);
        glBegin(GL_LINES);
        glVertex3fv(&vtx[(j*m + i)*3]);
        glVertex3fv(&vtx[((j+1)*m + i)*3]);
        glEnd();
        findex++;
      }
    }

    return 1;
  }

  if ( nc > 0 && ! color ) return 0;

  // Holizontal Lines
  for ( j = 0; j < n; j++ ) {
    glBegin(GL_LINE_STRIP);
    for ( i = 0; i < m; i++ ) {
      index = j*m + i;
      if ( j == (n -1) )
        findex = (j -1) * (m -1) + (i==(m -1) ? i -1 : i);
      else
        findex = j * (m -1) + (i==(m -1) ? i -1 : i);
      if ( ctype == AT_PER_VERTEX && index < nc )
	glColor4fv(&color[index*4]);
      else if ( ctype == AT_PER_FACE && findex < nc )
	glColor4fv(&color[findex*4]);
      glVertex3fv(&vtx[index*3]);
    } // end of for(i)
    glEnd();
  } // end of for(j)

  // Vartical Lines
  for ( i = 0; i < m; i++ ) {
    glBegin(GL_LINE_STRIP);
    for ( j = 0; j < n; j++ ) {
      index = j*m + i;
      if ( j == (n -1) )
        findex = (j -1) * (m -1) + (i==(m -1) ? i -1 : i);
      else
        findex = j * (m -1) + (i==(m -1) ? i -1 : i);
      if ( ctype == AT_PER_VERTEX && index < nc )
	glColor4fv(&color[index*4]);
      else if ( ctype == AT_PER_FACE && findex < nc )
	glColor4fv(&color[findex*4]);
      glVertex3fv(&vtx[index*3]);
    } // end of for(j)
    glEnd();
  } // end of for(i)

  return 1;
}


//---------------------- gfxMesh2D_CalcNormals ----------------------
VFR_API int gfxMesh2D_CalcNormals(int nv, float* vtx,
				  int nn, float* normal,
				  int m, int n, int ntype)
{
  if ( ! vtx || ! normal ) return 0;
  int faceNum = (m-1) * (n-1);
  int vtxNum = m * n;
  int nmlNum = faceNum;
  if ( ntype == AT_PER_VERTEX ) nmlNum = vtxNum;
  if ( nv < vtxNum || vtxNum < 1 ) return 0;
  if ( nn < nmlNum ) return 0;

  typedef float DV3[3];
  DV3* faceN = new DV3[faceNum];
  if ( ! faceNum ) return 0;

  CES::Vec3<double> v1, v2, nvw;
  int i, j, idx1, idx2, idx0;

  for ( j = 0; j < n-1; j++ ) {
    for ( i = 0; i < m-1; i++ ) {
      idx1 = (j+1)*m +i;
      idx2 = j*m +i;
      idx0 = j*(m -1) +i;
      v1[0] = vtx[(idx1 +1)*3 +0] - vtx[(idx2   )*3 +0];
      v1[1] = vtx[(idx1 +1)*3 +1] - vtx[(idx2   )*3 +1];
      v1[2] = vtx[(idx1 +1)*3 +2] - vtx[(idx2   )*3 +2];
      v2[0] = vtx[(idx1   )*3 +0] - vtx[(idx2 +1)*3 +0];
      v2[1] = vtx[(idx1   )*3 +1] - vtx[(idx2 +1)*3 +1];
      v2[2] = vtx[(idx1   )*3 +2] - vtx[(idx2 +1)*3 +2];
      nvw = v1 ^ v2; nvw.UnitVec();
      faceN[idx0][0] = nvw[0];
      faceN[idx0][1] = nvw[1];
      faceN[idx0][2] = nvw[2];
    }
  }
  if ( ntype == AT_PER_FACE ) {
    memcpy(normal, faceN, sizeof(DV3)*faceNum);
    delete [] faceN;
    return 1;
  }

  // Normals per VERTEX
  for ( j = 0; j < n; j++ ) {
    for ( i = 0; i < m; i++ ) {
      DV3 Nv = {0.0, 0.0, 0.0};
      int numF = 0;

      idx1 = (j-1)*(m-1) + i;
      idx2 = j*(m-1) + i;

      // Fa
      if ( i-1 >= 0 && j-1 >= 0 ) {
        Nv[0] += faceN[idx1-1][0];
        Nv[1] += faceN[idx1-1][1];
        Nv[2] += faceN[idx1-1][2];
        numF++;
      }
      // Fb
      if ( i < m-1 && j-1 >= 0 ) {
        Nv[0] += faceN[idx1][0];
        Nv[1] += faceN[idx1][1];
        Nv[2] += faceN[idx1][2];
        numF++;
      }
      // Fc
      if ( i < m-1 && j < n-1 ) {
        Nv[0] += faceN[idx2][0];
        Nv[1] += faceN[idx2][1];
        Nv[2] += faceN[idx2][2];
        numF++;
      }
      // Fd
      if ( i-1 >= 0 && j < n-1 ) {
        Nv[0] += faceN[idx2-1][0];
        Nv[1] += faceN[idx2-1][1];
        Nv[2] += faceN[idx2-1][2];
        numF++;
      }
      if ( numF <= 0 ) {
        Nv[2] = 1.0;
	normal[(j*m +i)*3   ] = Nv[0];
	normal[(j*m +i)*3 +1] = Nv[1];
	normal[(j*m +i)*3 +2] = Nv[2];
        continue;
      }
      Nv[0] /= (float)numF;
      Nv[1] /= (float)numF;
      Nv[2] /= (float)numF;
      normal[(j*m +i)*3   ] = Nv[0];
      normal[(j*m +i)*3 +1] = Nv[1];
      normal[(j*m +i)*3 +2] = Nv[2];
    }
  }
  delete [] faceN;
  return 1;
}
