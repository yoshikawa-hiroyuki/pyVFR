import wx
import sys
if not ".." in sys.path:
    sys.path = sys.path + [".."]
from vfr import drawAreaWx
from vfr import camera
from vfr import scene
from vfr import gfxNode
from vfr import gfxGroup
from vfr import primitives
from vfr import defaultActions
from vfr import utilMath
from vfr import shader_manager
import OpenGL.GL as GL

app = wx.App(False)
frame = wx.Frame(None, -1, 'stl', size=(600,400))
da = drawAreaWx.DrawAreaWx(frame)
frame.Show(True)

cam = camera.Camera3D()
cam._frustum._eye[2] = 15.0
cam._frustum._dist = 15.0
cam._antiAlias = True
da.setCamera(cam)

scn = scene.Scene(name='SCENE')
cam.setScene(scn)

cube = primitives.Cube(width=5, height=5, depth=5)
cube.setPickMode(gfxNode.PT_OBJECT)
cube.setFaceMode(gfxNode.PF_BOTH)
scn.addChild(cube)

sm = shader_manager.ShaderManager()
fragShader = """
void main() {
  gl_FragColor = vec4(0.18, 0.54, 0.34, 1.0);
}
"""
sm.setup({GL.GL_FRAGMENT_SHADER: fragShader})
cube._shader = sm

cube2 = primitives.Cube(width=5, height=5, depth=5)
cube2.setPickMode(gfxNode.PT_OBJECT)
cube2.trans([10, 0, 0])
scn.addChild(cube2)


#l = scn.getLight(1)
#l._on = True
#l.roty(utilMath.Deg2Rad(180))

defaultActions.SetDefaultAction(da)

app.MainLoop()

cube.destroy()
cam.destroy()
