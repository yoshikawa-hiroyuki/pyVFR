#
# Simple Volume Renderer
#
import os, sys
import numpy as np
from OpenGL.GL import *

from vfr.utilMath import *
from program_object import ProgramObject
from shader_object import VertexShaderObject, FragmentShaderObject

#----------------------------------------------------------------------
vs_code = '''
uniform mat4 modelview_matrix_inverse;
varying vec3 p;
varying vec3 t;
varying vec3 l;
void main() {
  gl_ClipVertex = gl_Vertex;
  gl_Position = gl_ProjectionMatrix * gl_Vertex;
  p = ( gl_ModelViewMatrix * gl_Vertex ).xyz;
  t = ( modelview_matrix_inverse * gl_Vertex ).xyz;
  l = ( modelview_matrix_inverse * gl_LightSource[0].position ).xyz;
}
'''

fs_code = '''
uniform sampler3D texture_data;
uniform float thickness;
varying vec3 t;
vec4 DensityToColor( float d );
void main() {
  float d = texture3D( texture_data, t ).x;
  vec4  c = DensityToColor( d );
  c.a = c.a * thickness;
  gl_FragColor = c;
}
'''

fs_code_density_to_color = '''
uniform sampler2D texture_lut;
varying vec3 p;
varying vec3 t;
varying vec3 l;
vec4 DensityToColor( float d ) {
  vec4 color = texture2D( texture_lut, vec2(d, 0) );
  return color;
 }
'''


#----------------------------------------------------------------------
class VolumeRender(object):
    def __init__(self, n_clip=0.1, f_clip=500.1, n_layer=256, is_frame=False,
                 margin=0.01):
        self.m_texture_data = 0
        self.m_texture_lut = 0
        self.m_size = [0, 0, 0]
        self.m_near_clipping_length = n_clip
        self.m_far_clipping_length = f_clip
        self.m_num_of_layers = n_layer
        self.m_is_init_shader = False
        self.m_po = None
        self.m_is_draw_frame = is_frame
        self.m_frame_margin_ratio = margin
        self.m_p0 = [0.0, 0.0, 0.0]
        self.m_p1 = [1.0, 1.0, 1.0]
        self.ResetClipPlane()
        return

    def __del__(self):
        if glIsTexture(self.m_texture_data):
            glDeleteTextures(1, [self.m_texture_data])
        if glIsTexture(self.m_texture_lut):
            glDeleteTextures(1, [self.m_texture_lut])
        return

    def SetVolume(self, data, n_size_x, n_size_y, n_size_z):
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        if glIsTexture(self.m_texture_data):
            glDeleteTextures(1, [self.m_texture_data])

        self.m_texture_data = glGenTextures(1)
        glBindTexture(GL_TEXTURE_3D, self.m_texture_data)
        glTexParameteri(GL_TEXTURE_3D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_3D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_3D, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_3D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_3D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)

        self.m_size[0] = n_size_x
        self.m_size[1] = n_size_y
        self.m_size[2] = n_size_z
        glTexImage3D(GL_TEXTURE_3D, 0, GL_LUMINANCE,
                     self.m_size[0], self.m_size[1], self.m_size[2],
                     0, GL_LUMINANCE, GL_UNSIGNED_BYTE, data)
        return
    
    def UpdateVolume(self, data, n_size_x, n_size_y, n_size_z):
        if glIsTexture(self.m_texture_data):
            return
        glBindTexture(GL_TEXTURE_3D, self.m_texture_data)

        if self.m_size[0] != n_size_x or \
           self.m_size[1] != n_size_y or self.m_size[2] != n_size_z:
            self.m_size[0] = n_size_x
            self.m_size[1] = n_size_y
            self.m_size[2] = n_size_z
            glTexImage3D(GL_TEXTURE_3D, 0, GL_LUMINANCE,
                         self.m_size[0], self.m_size[1], self.m_size[2],
                         0, GL_LUMINANCE, GL_UNSIGNED_BYTE, data)
        else:
            glTexSubImage3D(GL_TEXTURE_3D, 0, 0, 0, 0,
                            self.m_size[0], self.m_size[1], self.m_size[2],
                            GL_LUMINANCE, GL_UNSIGNED_BYTE, data)
        return

    def SetLUT(self, lut):
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)

        if glIsTexture(self.m_texture_lut):
            glDeleteTextures(1, [self.m_texture_lut])
        self.m_texture_lut = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.m_texture_lut)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 256, 1, 0,
                     GL_RGBA, GL_UNSIGNED_BYTE, lut)
        return

    def UpdateLUT(self, lut):
        if not glIsTexture(self.m_texture_lut):
            return
        glBindTexture(GL_TEXTURE_2D, self.m_texture_lut)

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 256, 1, 0,
                     GL_RGBA, GL_UNSIGNED_BYTE, lut)
        return

    def SetBbox(self, p0, p1):
        dx = p1[0] - p0[0]
        dy = p1[1] - p0[1]
        dz = p1[2] - p0[2]
        if dx < 1e-8 or dy < 1e-8 or dz < 1e-8:
            return
        self.m_p0[0] = p0[0]; self.m_p0[1] = p0[1]; self.m_p0[2] = p0[2]
        self.m_p1[0] = p1[0]; self.m_p1[1] = p1[1]; self.m_p1[2] = p1[2]
        return

    def SetClipPlane(self, p):
        for i in range(6):
            if p[i] < 0.0: self.m_clip_plane[i][3] = 0.0
            elif p[i] > 1.0: self.m_clip_plane[i][3] = 1.0
            else: self.m_clip_plane[i][3] = p[i]
        self.m_clip_plane[0][3] *= -1
        self.m_clip_plane[2][3] *= -1
        self.m_clip_plane[4][3] *= -1
        return

    def GetClipPlane(self):
        p = self.m_clip_plane[:, 3]
        return p

    def CalcBoundingBox(self):
        m = glGetFloatv(GL_MODELVIEW_MATRIX).reshape([16])

        x_min = m[ 3 * 4 + 0 ]
        x_max = m[ 3 * 4 + 0 ]
        for i in range(3):
            if m[ i * 4 + 0 ] < 0:
                x_min += m[ i * 4 + 0 ]
            else:
                x_max += m[ i * 4 + 0 ]

        y_min = m[ 3 * 4 + 1 ]
        y_max = m[ 3 * 4 + 1 ]
        for i in range(3):
            if m[ i * 4 + 1 ] < 0:
                y_min += m[ i * 4 + 1 ]
            else:
                y_max += m[ i * 4 + 1 ]

        z_min = m[ 3 * 4 + 2 ]
        z_max = m[ 3 * 4 + 2 ]
        for i in range(3):
            if m[ i * 4 + 2 ] < 0:
                z_min += m[ i * 4 + 2 ]
            else:
                z_max += m[ i * 4 + 2 ]

        if z_max > -self.m_near_clipping_length:
            z_max = -self.m_near_clipping_length
        if z_min < -self.m_far_clipping_length:
            z_min = -self.m_far_clipping_length

        return (x_min, x_max, y_min, y_max, z_min, z_max)

    def InitShader(self):
        self.m_po = ProgramObject()

        vs = VertexShaderObject(vs_code)
        self.m_po.Attach(vs)

        fs = FragmentShaderObject(fs_code)
        self.m_po.Attach(fs)

        fs = FragmentShaderObject(fs_code_density_to_color)
        self.m_po.Attach(fs)

        self.m_po.Link()

        self.m_is_init_shader = True
        return

    def DrawFrame(self):
        glPushMatrix()

        m = self.m_frame_margin_ratio
        glTranslatef(-m, -m, -m)

        s = 1.0 + m * 2
        glScalef(s, s, s)

        glDisable(GL_LIGHTING)
        glColor3f(1.0, 1.0, 1.0)

        glBegin(GL_LINES)
        for i in (0, 1):
            for j in ( 0, 1):
                glVertex3i( i, j, 0 )
                glVertex3i( i, j, 1 )
                glVertex3i( i, 0, j )
                glVertex3i( i, 1, j )
                glVertex3i( 0, i, j )
                glVertex3i( 1, i, j )
        glEnd()

        glPopMatrix()
        return

    def EnableClipPlane(self):
        for i in range(6):
            glClipPlane(GL_CLIP_PLANE0 + i, self.m_clip_plane[ i ])
            glEnable(GL_CLIP_PLANE0 + i)
        return

    def DisableClipPlane(self):
        for i in range(6):
            glDisable(GL_CLIP_PLANE0 + i)
        return

    def ResetClipPlane(self):
        self.m_clip_plane = np.array([[ 1,  0,  0, 0],
                                      [-1,  0,  0, 1],
                                      [ 0,  1,  0, 0],
                                      [ 0, -1,  0, 1],
                                      [ 0,  0,  1, 0],
                                      [ 0,  0, -1, 1]])
        return

    def Draw(self):
        if not self.m_is_init_shader:
            self.InitShader()

        glPushMatrix()
        glTranslatef(self.m_p0[0], self.m_p0[1], self.m_p0[2])
        glScalef(self.m_p1[0] - self.m_p0[0],
                 self.m_p1[1] - self.m_p0[1],
                 self.m_p1[2] - self.m_p0[2])

        if self.m_is_draw_frame:
            self.DrawFrame()

        (x_min, x_max, y_min, y_max, z_min, z_max) = self.CalcBoundingBox()
        thickness = ( z_max - z_min ) / self.m_num_of_layers

        resol = self.m_size[0]
        if resol < self.m_size[1]: resol = self.m_size[1]
        if resol < self.m_size[2]: resol = self.m_size[2]
        thickness1 = resol / self.m_num_of_layers
        resolution = [1/self.m_size[0], 1/self.m_size[1], 1/self.m_size[2]]
        
        self.EnableClipPlane()

        glDisable(GL_CULL_FACE)
        glDisable(GL_LIGHTING)

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_3D, self.m_texture_data)

        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, self.m_texture_lut)

        m = glGetFloatv(GL_MODELVIEW_MATRIX).reshape([16])
        M = Mat4(m)
        iM = M.inverse()

        self.m_po.Enable()
        self.m_po.SetUniform1i("texture_data", 0) # TEXTURE0
        self.m_po.SetUniform1i("texture_lut",  1) # TEXTURE1
        self.m_po.SetUniform1f("thickness", thickness1)
        self.m_po.SetUniform3f("resolution",
                               resolution[0], resolution[1], resolution[2])
        self.m_po.SetMatrix4fv("modelview_matrix_inverse", 1, GL_FALSE, iM.m_v)
  
        glPushMatrix()
        glBegin(GL_QUADS)
        for i in range(self.m_num_of_layers):
            z = z_min + thickness * i
            glVertex3f( x_min, y_min, z )
            glVertex3f( x_max, y_min, z )
            glVertex3f( x_max, y_max, z )
            glVertex3f( x_min, y_max, z )
        glEnd()
        glPopMatrix()

        self.m_po.Disable()
        glDisable(GL_BLEND)
        self.DisableClipPlane()

        glPopMatrix()
        return
    
#----------------------------------------------------------------------
def GetMax3DTexSize(startSz):
    _MIN_SAMPLE_SZ = 64

    maxTex3DSz = glGetIntegerv(GL_MAX_3D_TEXTURE_SIZE)
    if maxTex3DSz < 1: maxTex3DSz = 512
    rDims = [maxTex3DSz, maxTex3DSz, maxTex3DSz]
    for i in range(3):
        while rDims[i] > 1:
            if rDims[i] <= startSz[i]: break
            rDims[i] /= 2
            continue # while
        if rDims[i] < _MIN_SAMPLE_SZ: rDims[i] = _MIN_SAMPLE_SZ
        continue # i
    irDims = [int(rDims[0]), int(rDims[1]), int(rDims[2])]
    return irDims

