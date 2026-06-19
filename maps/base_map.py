from panda3d.core import (
    GeomVertexFormat, GeomVertexData, GeomVertexWriter,
    GeomTriangles, Geom, GeomNode, NodePath,
    CollisionNode, CollisionPolygon, CollisionBox,
    Vec3, Vec4, Point3, BitMask32, TransparencyAttrib,
    AmbientLight, DirectionalLight
)
import math


SURF_MASK  = BitMask32.bit(2)
WORLD_MASK = BitMask32.bit(0)


def _make_quad_geom(verts, color):
    fmt  = GeomVertexFormat.getV3n3c4()
    vdata = GeomVertexData('quad', fmt, Geom.UHStatic)
    vdata.setNumRows(4)
    vw = GeomVertexWriter(vdata, 'vertex')
    nw = GeomVertexWriter(vdata, 'normal')
    cw = GeomVertexWriter(vdata, 'color')

    v0, v1, v2, v3 = [Vec3(*v) for v in verts]
    edge1 = v1 - v0
    edge2 = v3 - v0
    normal = edge1.cross(edge2)
    if normal.length() > 0.0001:
        normal.normalize()

    for v in (v0, v1, v2, v3):
        vw.addData3(v)
        nw.addData3(normal)
        cw.addData4(*color)

    tris = GeomTriangles(Geom.UHStatic)
    tris.addVertices(0, 1, 2)
    tris.addVertices(0, 2, 3)
    tris.closePrimitive()

    geom = Geom(vdata)
    geom.addPrimitive(tris)
    return geom, normal


def make_ramp(parent_np, x, y, z, length, width, angle_deg, color=(0.6, 0.4, 0.2, 1), axis='x'):
    angle = math.radians(angle_deg)
    ca, sa = math.cos(angle), math.sin(angle)

    if axis == 'x':
        bl = (x,          y,          z)
        br = (x,          y + width,  z)
        tr = (x + length, y + width,  z + length * sa)
        tl = (x + length, y,          z + length * sa)
    else:
        bl = (x,         y,          z)
        br = (x + width, y,          z)
        tr = (x + width, y + length, z + length * sa)
        tl = (x,         y + length, z + length * sa)

    geom, normal = _make_quad_geom([bl, br, tr, tl], color)
    gnode = GeomNode('ramp')
    gnode.addGeom(geom)
    np = parent_np.attachNewNode(gnode)

    cnode = CollisionNode('ramp_col')
    cnode.setFromCollideMask(BitMask32.allOff())
    cnode.setIntoCollideMask(SURF_MASK)
    cnode.addSolid(CollisionPolygon(Point3(*bl), Point3(*br), Point3(*tr), Point3(*tl)))
    cnp = np.attachNewNode(cnode)

    sides = [
        [bl, tl, tr, br],
    ]
    for side_verts in sides:
        sg, _ = _make_quad_geom(side_verts, (color[0]*0.5, color[1]*0.5, color[2]*0.5, 1))
        sgnode = GeomNode('ramp_side')
        sgnode.addGeom(sg)
        np.attachNewNode(sgnode)

    return np, normal


def make_platform(parent_np, x, y, z, size_x, size_y, color=(0.25, 0.25, 0.28, 1)):
    bl = (x,          y,          z)
    br = (x,          y + size_y, z)
    tr = (x + size_x, y + size_y, z)
    tl = (x + size_x, y,          z)
    geom, normal = _make_quad_geom([bl, br, tr, tl], color)
    gnode = GeomNode('platform')
    gnode.addGeom(geom)
    np = parent_np.attachNewNode(gnode)

    cnode = CollisionNode('platform_col')
    cnode.setFromCollideMask(BitMask32.allOff())
    cnode.setIntoCollideMask(SURF_MASK)
    cnode.addSolid(CollisionPolygon(Point3(*bl), Point3(*br), Point3(*tr), Point3(*tl)))
    np.attachNewNode(cnode)
    return np


def make_trigger(parent_np, cx, cy, cz, sx, sy, sz, name='trigger'):
    cnode = CollisionNode(name)
    cnode.setFromCollideMask(BitMask32.allOff())
    cnode.setIntoCollideMask(BitMask32.bit(3))
    half = Vec3(sx/2, sy/2, sz/2)
    cnode.addSolid(CollisionBox(Point3(cx, cy, cz), half.x, half.y, half.z))
    return parent_np.attachNewNode(cnode)


def make_kill_floor(parent_np, y_start, y_end, width, z=-200):
    make_platform(parent_np, -width/2, y_start, z, width, y_end - y_start, color=(0.15,0.05,0.05,1))


def setup_lighting(render):
    alight = AmbientLight('ambient')
    alight.setColor(Vec4(0.35, 0.35, 0.40, 1))
    alnp = render.attachNewNode(alight)
    render.setLight(alnp)

    dlight = DirectionalLight('sun')
    dlight.setColor(Vec4(0.9, 0.85, 0.75, 1))
    dlnp = render.attachNewNode(dlight)
    dlnp.setHpr(45, -60, 0)
    render.setLight(dlnp)
    return alnp, dlnp


class BaseMap:
    NAME       = 'Map'
    MAP_INDEX  = 0
    SKY_COLOR  = (0.1, 0.15, 0.25, 1)
    SPAWN_POS  = Vec3(0, 0, 300)
    SPAWN_HPR  = Vec3(0, 0, 0)

    def __init__(self, render, base):
        self.render = render
        self.base   = base
        self.root   = render.attachNewNode(f'map_{self.MAP_INDEX}')
        self._lights = []
        self.end_trigger = None
        self.kill_z = -400

    def build(self):
        raise NotImplementedError

    def cleanup(self):
        self.root.removeNode()
        for lnp in self._lights:
            self.render.clearLight(lnp)

    def get_spawn(self):
        return Vec3(self.SPAWN_POS), Vec3(self.SPAWN_HPR)
