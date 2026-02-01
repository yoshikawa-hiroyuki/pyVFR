import wx
import math
import sys
if not ".." in sys.path:
    sys.path = sys.path + [".."]
from vfr import drawAreaWx
from vfr import camera
from vfr import scene
from vfr import gfxNode
from vfr import gfxGroup
from vfr import triangles
from vfr import tria_io
from vfr import image
from vfr import texture
from vfr import defaultActions
from vfr import utilMath


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

(node, fmt) = tria_io.Read("saddle.stl")
node.setPickMode(gfxNode.PT_OBJECT)
node.generateNormals()
scn.addChild(node)

img = image.PixelImage()
img.loadImage('Mandrill.jpg')
tex = texture.TexNode()
tex.setImage(img)
tex._matrix.RotZ(math.pi/4)
node.setTexture(tex)


grp = node
bblen = abs(grp._bbox[1] - grp._bbox[0])
bbc = (grp._bbox[1] + grp._bbox[0]) * (-0.5)
grp._matrix.Identity()
grp._matrix.Scale(6.0 / bblen)
grp._matrix.Translate(bbc)
grp.rotx(utilMath.Deg2Rad(85.0))

defaultActions.SetDefaultAction(da)

app.MainLoop()


