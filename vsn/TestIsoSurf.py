import os, sys
import ctypes as C
import numpy as N
if not ".." in sys.path:
    sys.path = sys.path + [".."]
from vfr import *

vsn_impl = N.ctypeslib.load_library('vsn_impl',
                                    os.path.join(os.path.dirname(__file__),
                                                 "lib"))
vsn_impl.GenerateIsosurfS.restype = C.c_int
vsn_impl.GenerateIsosurfS.argtypes = [
    C.c_void_p,             # p
    C.c_size_t*3,           # dims[3]
    C.POINTER(C.c_float*3), # coord
    C.POINTER(C.c_float),   # data
    C.c_float               # thresh
]

vector3 = C.c_float * 3


from pySPH import SPH
sph = SPH.SPH()
files = [f"p_{i:03d}.sph" for i in range(1, 11)]
sph.load(os.path.join("data", files[-1]))

dims = (C.c_size_t*3)(*sph.dims)
dimSz = sph.dims[0]*sph.dims[1]*sph.dims[2]


def make_coord_array(sph):
    (x0, y0, z0) = (sph.org[0], sph.org[1], sph.org[2])
    (x1, y1, z1) = (sph.org[0]+sph.pitch[0]*(sph.dims[0]-1),
                    sph.org[1]+sph.pitch[1]*(sph.dims[1]-1),
                    sph.org[2]+sph.pitch[2]*(sph.dims[2]-1))
    (nx, ny, nz) = (sph.dims[0], sph.dims[1], sph.dims[2])
    
    xs = [x0 + (x1 - x0) * i / (nx - 1) for i in range(nx)]
    ys = [y0 + (y1 - y0) * j / (ny - 1) for j in range(ny)]
    zs = [z0 + (z1 - z0) * k / (nz - 1) for k in range(nz)]

    N = nx * ny * nz
    CoordArray = vector3 * N

    coords = CoordArray()

    idx = 0
    for k in range(nz):
        for j in range(ny):
            for i in range(nx):
                coords[idx] = vector3(xs[i], ys[j], zs[k])
                idx += 1

    return coords

def make_data_array(sph):
    if sph.dtype == SPH.SPH.DT_SINGLE:
        arr = N.asarray(sph.data, dtype=N.float32)
        data_ptr = arr.ctypes.data_as(C.POINTER(C.c_float))
    elif sph.dtype == SPH.SPH.DT_DOUBLE:
        arr = N.asarray(sph.data, dtype=N.float64)
        data_ptr = arr.ctypes.data_as(C.POINTER(C.c_double))
    else:
        return None
    return data_ptr


coord = make_coord_array(sph)
data = make_data_array(sph)

iso_obj = triangles.Triangles()
ret = vsn_impl.GenerateIsosurfS(iso_obj.p_impl, dims, coord, data, 0.0)
if ret:
    iso_obj.updateObjImpl()
print(f'nVerts = {iso_obj.nVerts}')
del iso_obj

