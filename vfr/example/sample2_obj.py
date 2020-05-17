import wx
import sys
if not ".." in sys.path:
    sys.path = sys.path + ["../.."]
from vfr import drawAreaWx
from vfr import camera
from vfr import scene
from vfr import gfxNode
from vfr import gfxGroup
from vfr import triangles
from vfr import tria_io
from vfr import primitives
from vfr import defaultActions
from vfr import utilMath


app = wx.App(False)
frame = wx.Frame(None, -1, 'obj', size=(600,400))
da = drawAreaWx.DrawAreaWx(frame)
frame.Show(True)

cam = camera.Camera3D()
cam._frustum._eye[2] = 15.0
cam._frustum._dist = 15.0
cam._antiAlias = True
da.setCamera(cam)

scn = scene.Scene('SCENE')
cam.setScene(scn)

grp = gfxGroup.GfxGroup('GROUP')
grp.setPickMode(gfxNode.PT_OBJECT)
scn.addChild(grp)

node = tria_io.ReadOBJ('bunny.obj')
node.setPickMode(gfxNode.PT_OBJECT)
grp.addChild(node)

bblen = abs(grp._bbox[1] - grp._bbox[0])
bbc = (grp._bbox[1] + grp._bbox[0]) * (-0.5)
grp._matrix.Identity()
grp._matrix.Scale(6.0 / bblen)
grp._matrix.Translate(bbc)

defaultActions.SetDefaultAction(da)

app.MainLoop()

node.destroy()
cam.destroy()

