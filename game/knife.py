"""
Knife viewmodel system.
- Procedural geometry for Default, Karambit, Bayonet, Butterfly.
- Separate viewmodel camera (depth-cleared) so knife always renders on top.
- Animation state machine with keyframe lerping.
- CS2 skin texture applied via skins.py.
"""

import math
from panda3d.core import (
    GeomVertexFormat, GeomVertexData, GeomVertexWriter,
    GeomTriangles, Geom, GeomNode, NodePath,
    Vec3, Vec4, Point3, BitMask32,
    AmbientLight, DirectionalLight,
    Texture, TransparencyAttrib,
)

VM_MASK = BitMask32.bit(1)


# ─── Geometry helpers ─────────────────────────────────────────────────────────

def _vdata(n):
    fmt = GeomVertexFormat.getV3n3c4()
    vd  = GeomVertexData('k', fmt, Geom.UHStatic)
    vd.setNumRows(n)
    return vd


def _write_quad(vd, off, verts, color, normal=None):
    vw = GeomVertexWriter(vd, 'vertex')
    nw = GeomVertexWriter(vd, 'normal')
    cw = GeomVertexWriter(vd, 'color')
    vw.setRow(off); nw.setRow(off); cw.setRow(off)
    v = [Vec3(*p) for p in verts]
    if normal is None:
        e1 = v[1] - v[0]; e2 = v[3] - v[0]
        n  = e1.cross(e2); n.normalize()
    else:
        n = Vec3(*normal)
    for vi in v:
        vw.addData3(vi); nw.addData3(n); cw.addData4(*color)


def _tris_quad(off):
    t = GeomTriangles(Geom.UHStatic)
    t.addVertices(off, off+1, off+2)
    t.addVertices(off, off+2, off+3)
    t.closePrimitive()
    return t


def _make_box(parent, x0, y0, z0, x1, y1, z1, color):
    faces = [
        [(x0,y0,z0),(x1,y0,z0),(x1,y0,z1),(x0,y0,z1)],
        [(x0,y1,z0),(x0,y1,z1),(x1,y1,z1),(x1,y1,z0)],
        [(x0,y0,z0),(x0,y0,z1),(x0,y1,z1),(x0,y1,z0)],
        [(x1,y0,z0),(x1,y1,z0),(x1,y1,z1),(x1,y0,z1)],
        [(x0,y0,z0),(x0,y1,z0),(x1,y1,z0),(x1,y0,z0)],
        [(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)],
    ]
    vd = _vdata(24)
    prims = []
    for i, face in enumerate(faces):
        _write_quad(vd, i*4, face, color)
        prims.append(_tris_quad(i*4))
    geom = Geom(vd)
    for p in prims:
        geom.addPrimitive(p)
    gn = GeomNode('box')
    gn.addGeom(geom)
    np = parent.attachNewNode(gn)
    np.setTwoSided(True)
    return np


def _make_prism(parent, base_verts, height, color, color2=None):
    if color2 is None:
        color2 = (color[0]*0.7, color[1]*0.7, color[2]*0.7, color[3])
    n = len(base_verts)
    top_verts = [(x, y, z + height) for x, y, z in base_verts]
    all_verts  = base_verts + top_verts
    vd = _vdata(n * 4 + 4 + 4)
    prims = []
    # side faces
    for i in range(n):
        j = (i + 1) % n
        face = [base_verts[i], base_verts[j], top_verts[j], top_verts[i]]
        _write_quad(vd, i*4, face, color2)
        prims.append(_tris_quad(i*4))
    # bottom cap
    vw = GeomVertexWriter(vd, 'vertex'); nw = GeomVertexWriter(vd, 'normal'); cw = GeomVertexWriter(vd, 'color')
    base_off = n*4
    vw.setRow(base_off); nw.setRow(base_off); cw.setRow(base_off)
    for v in base_verts:
        vw.addData3(*v); nw.addData3(0,0,-1); cw.addData4(*color)
    t = GeomTriangles(Geom.UHStatic)
    for i in range(1, n-1):
        t.addVertices(base_off, base_off+i, base_off+i+1)
    t.closePrimitive()
    prims.append(t)
    # top cap
    top_off = n*4 + n
    vw.setRow(top_off); nw.setRow(top_off); cw.setRow(top_off)
    for v in top_verts:
        vw.addData3(*v); nw.addData3(0,0,1); cw.addData4(*color)
    t2 = GeomTriangles(Geom.UHStatic)
    for i in range(1, n-1):
        t2.addVertices(top_off, top_off+i+1, top_off+i)
    t2.closePrimitive()
    prims.append(t2)
    geom = Geom(vd)
    for p in prims:
        geom.addPrimitive(p)
    gn = GeomNode('prism')
    gn.addGeom(geom)
    np = parent.attachNewNode(gn)
    np.setTwoSided(True)
    return np


def _cylinder(parent, radius, height, segs, color):
    verts = [(radius * math.cos(2*math.pi*i/segs),
              radius * math.sin(2*math.pi*i/segs), 0) for i in range(segs)]
    return _make_prism(parent, verts, height, color)


# ─── Knife geometry builders ──────────────────────────────────────────────────

STEEL  = (0.78, 0.78, 0.82, 1)
HANDLE = (0.15, 0.10, 0.08, 1)
GUARD  = (0.50, 0.48, 0.45, 1)


def _build_default(root):
    blade_verts = [(-0.01, 0, 0), (0.01, 0, 0), (0.005, 0, 0.32), (-0.005, 0, 0.32)]
    blade  = _make_prism(root, blade_verts, 0.005, STEEL)
    blade.setPos(0, 0, 0.04)
    _make_box(root, -0.025, -0.01, 0.02, 0.025, 0.01, 0.04, GUARD)
    _cylinder(root, 0.018, 0.16, 8, HANDLE)
    return root


def _build_karambit(root):
    segs = 14
    r_outer = 0.18
    r_inner = 0.13
    blade_root = root.attachNewNode('blade_root')
    for i in range(segs):
        a0 = math.pi * i / segs
        a1 = math.pi * (i + 1) / segs
        x00 = r_outer * math.cos(a0); y00 = r_outer * math.sin(a0)
        x01 = r_outer * math.cos(a1); y01 = r_outer * math.sin(a1)
        x10 = r_inner * math.cos(a0); y10 = r_inner * math.sin(a0)
        x11 = r_inner * math.cos(a1); y11 = r_inner * math.sin(a1)
        face = [(x00,y00,0),(x01,y01,0),(x11,y11,0.003),(x10,y10,0.003)]
        vd = _vdata(4)
        _write_quad(vd, 0, face, STEEL)
        g = Geom(vd); g.addPrimitive(_tris_quad(0))
        gn = GeomNode('blade_seg'); gn.addGeom(g)
        blade_root.attachNewNode(gn)
    blade_root.setPos(0, 0, 0.05)
    # finger ring
    ring_segs = 16
    ring_r = 0.025
    torus_cx, torus_cy = 0.0, 0.0
    ring_verts = [(torus_cx + ring_r*math.cos(2*math.pi*i/ring_segs),
                   torus_cy + ring_r*math.sin(2*math.pi*i/ring_segs), 0)
                  for i in range(ring_segs)]
    _make_prism(root, ring_verts, 0.006, STEEL)
    _cylinder(root, 0.020, 0.13, 8, HANDLE).setPos(0, 0, 0)
    root.setHpr(0, -15, 0)
    return root


def _build_bayonet(root):
    # long tapered blade
    blade_verts = [(-0.012, 0, 0), (0.012, 0, 0), (0.004, 0, 0.42), (-0.004, 0, 0.42)]
    blade = _make_prism(root, blade_verts, 0.006, STEEL)
    blade.setPos(0, 0, 0.05)
    # serrated back edge (small steps)
    for i in range(6):
        notch_z = 0.06 + i * 0.04
        _make_box(root, 0.010, -0.003, notch_z, 0.016, 0.003, notch_z+0.012,
                  (0.65, 0.65, 0.68, 1))
    _make_box(root, -0.030, -0.012, 0.03, 0.030, 0.012, 0.05, GUARD)
    _cylinder(root, 0.020, 0.18, 8, HANDLE)
    return root


def _build_butterfly(root):
    # blade
    blade_verts = [(-0.010, 0, 0), (0.010, 0, 0), (0.004, 0, 0.30), (-0.004, 0, 0.30)]
    blade = _make_prism(root, blade_verts, 0.005, STEEL)
    blade.setPos(0, 0, 0.04)
    _make_box(root, -0.025, -0.010, 0.02, 0.025, 0.010, 0.04, GUARD)
    # two handle plates as separate nodes (animated on draw)
    h1 = root.attachNewNode('handle_a')
    h2 = root.attachNewNode('handle_b')
    _make_box(h1, -0.015, -0.006, -0.18, 0.015, 0.006, 0, HANDLE)
    _make_box(h2, -0.015, -0.006, -0.18, 0.015, 0.006, 0,
              (0.20, 0.14, 0.11, 1))
    h1.setPos(0, -0.007, 0); h2.setPos(0,  0.007, 0)
    return root, h1, h2


# ─── Animation ────────────────────────────────────────────────────────────────

class Keyframe:
    __slots__ = ('time', 'pos', 'hpr')
    def __init__(self, time, pos, hpr):
        self.time = time
        self.pos  = Vec3(*pos)
        self.hpr  = Vec3(*hpr)


def _lerp_vec3(a, b, t):
    return Vec3(a.x + (b.x - a.x)*t,
                a.y + (b.y - a.y)*t,
                a.z + (b.z - a.z)*t)


ANIMS = {
    'default': {
        'draw':    [Keyframe(0,   (0.30,-0.10,-0.20), (0,-30, 0)),
                    Keyframe(0.4, (0.20, 0.00, 0.00), (0,  0, 0))],
        'idle':    [Keyframe(0,   (0.20, 0.00, 0.00), (0,  0, 0)),
                    Keyframe(1.0, (0.20, 0.00, 0.02), (0,  0, 0)),
                    Keyframe(2.0, (0.20, 0.00, 0.00), (0,  0, 0))],
        'slash':   [Keyframe(0,   (0.20, 0.00, 0.00), (  0,  0,  0)),
                    Keyframe(0.15,(0.05, 0.05, 0.00), (-35, 10, 20)),
                    Keyframe(0.5, (0.20, 0.00, 0.00), (  0,  0,  0))],
        'stab':    [Keyframe(0,   (0.20, 0.00, 0.00), (0, 0, 0)),
                    Keyframe(0.25,(0.20, 0.15, 0.00), (0, 0, 0)),
                    Keyframe(0.7, (0.20, 0.00, 0.00), (0, 0, 0))],
        'inspect': [Keyframe(0,   (0.20, 0.00, 0.00), (  0,  0,  0)),
                    Keyframe(0.5, (0.10, 0.05,-0.05), (-20,-10,-15)),
                    Keyframe(1.5, (0.10, 0.05,-0.05), ( 15,-10, 20)),
                    Keyframe(2.5, (0.20, 0.00, 0.00), (  0,  0,  0))],
        'holster': [Keyframe(0,   (0.20, 0.00, 0.00), (0, 0, 0)),
                    Keyframe(0.3, (0.30,-0.10,-0.25), (0,-30, 0))],
    },
    'karambit': {
        'draw':    [Keyframe(0,   (0.25,-0.10,-0.25), (0,-45, 0)),
                    Keyframe(0.5, (0.22, 0.00,-0.05), (0,-15, 0))],
        'idle':    [Keyframe(0,   (0.22, 0.00,-0.05), ( 0,-15, 0)),
                    Keyframe(1.2, (0.22, 0.00,-0.03), ( 0,-15, 0)),
                    Keyframe(2.4, (0.22, 0.00,-0.05), ( 0,-15, 0))],
        'slash':   [Keyframe(0,   (0.22, 0.00,-0.05), (  0,-15,   0)),
                    Keyframe(0.2, (0.10, 0.05, 0.00), (-20,-10, 180)),
                    Keyframe(0.4, (0.22, 0.00,-0.05), (  0,-15, 360))],
        'stab':    [Keyframe(0,   (0.22, 0.00,-0.05), (  0,-15,  0)),
                    Keyframe(0.3, (0.22, 0.12,-0.05), (-10,-15, 45)),
                    Keyframe(0.7, (0.22, 0.00,-0.05), (  0,-15,  0))],
        'inspect': [Keyframe(0,   (0.22, 0.00,-0.05), ( 0,-15,   0)),
                    Keyframe(0.6, (0.10, 0.05,-0.10), (-15,-20, 180)),
                    Keyframe(1.8, (0.10, 0.05,-0.10), (-15,-20, 360)),
                    Keyframe(2.5, (0.22, 0.00,-0.05), ( 0,-15,   0))],
        'holster': [Keyframe(0,   (0.22, 0.00,-0.05), (0,-15, 0)),
                    Keyframe(0.35,(0.28,-0.12,-0.28), (0,-45, 0))],
    },
    'bayonet': {
        'draw':    [Keyframe(0,   (0.35,-0.05,-0.15), (20,-20, 0)),
                    Keyframe(0.4, (0.22, 0.00, 0.00), ( 0,  0, 0))],
        'idle':    [Keyframe(0,   (0.22, 0.00, 0.00), (0, 0, 0)),
                    Keyframe(1.5, (0.22, 0.00, 0.02), (0, 0, 0)),
                    Keyframe(3.0, (0.22, 0.00, 0.00), (0, 0, 0))],
        'slash':   [Keyframe(0,   (0.22, 0.00, 0.00), (  0, 0,  0)),
                    Keyframe(0.2, (0.05, 0.05, 0.00), (-40, 5, 15)),
                    Keyframe(0.6, (0.22, 0.00, 0.00), (  0, 0,  0))],
        'stab':    [Keyframe(0,   (0.22, 0.00, 0.00), (0, 0, 0)),
                    Keyframe(0.35,(0.22, 0.20, 0.00), (0, 0, 0)),
                    Keyframe(0.8, (0.22, 0.00, 0.00), (0, 0, 0))],
        'inspect': [Keyframe(0,   (0.22, 0.00, 0.00), (  0,  0,  0)),
                    Keyframe(0.6, (0.08, 0.05,-0.05), (-25,-15,-20)),
                    Keyframe(1.8, (0.08, 0.05,-0.05), ( 20,-15, 25)),
                    Keyframe(2.5, (0.22, 0.00, 0.00), (  0,  0,  0))],
        'holster': [Keyframe(0,   (0.22, 0.00, 0.00), ( 0,  0, 0)),
                    Keyframe(0.3, (0.35,-0.05,-0.18), (20,-20, 0))],
    },
    'butterfly': {
        'draw':    [Keyframe(0,   (0.30,-0.08,-0.20), (0,-25, 90)),
                    Keyframe(0.35,(0.22, 0.00, 0.00), (0,  0,  0))],
        'idle':    [Keyframe(0,   (0.22, 0.00, 0.00), ( 0,  0,  0)),
                    Keyframe(1.0, (0.22, 0.00, 0.01), ( 0,  2,  0)),
                    Keyframe(2.0, (0.22, 0.00, 0.00), ( 0,  0,  0))],
        'slash':   [Keyframe(0,   (0.22, 0.00, 0.00), (  0,  0,   0)),
                    Keyframe(0.15,(0.22, 0.00, 0.00), (  0,  0,  45)),
                    Keyframe(0.3, (0.05, 0.05, 0.00), (-30, 10,  20)),
                    Keyframe(0.6, (0.22, 0.00, 0.00), (  0,  0,   0))],
        'stab':    [Keyframe(0,   (0.22, 0.00, 0.00), (  0,  0,  0)),
                    Keyframe(0.15,(0.22, 0.00, 0.00), (  0,  0, 45)),
                    Keyframe(0.4, (0.22, 0.18, 0.00), (  0,  0,  0)),
                    Keyframe(0.75,(0.22, 0.00, 0.00), (  0,  0,  0))],
        'inspect': [Keyframe(0,   (0.22, 0.00, 0.00), (  0,  0,   0)),
                    Keyframe(0.4, (0.10, 0.04,-0.06), (-15,-10,  90)),
                    Keyframe(1.2, (0.10, 0.04,-0.06), (-15,-10, 270)),
                    Keyframe(2.5, (0.22, 0.00, 0.00), (  0,  0,   0))],
        'holster': [Keyframe(0,   (0.22, 0.00, 0.00), (0,   0, 0)),
                    Keyframe(0.3, (0.30,-0.08,-0.22), (0, -25, 0))],
    },
}

ANIM_DURATIONS = {
    'draw':    {'default':0.4, 'karambit':0.5, 'bayonet':0.4, 'butterfly':0.35},
    'slash':   {'default':0.5, 'karambit':0.4, 'bayonet':0.6, 'butterfly':0.6},
    'stab':    {'default':0.7, 'karambit':0.7, 'bayonet':0.8, 'butterfly':0.75},
    'inspect': {'default':2.5, 'karambit':2.5, 'bayonet':2.5, 'butterfly':2.5},
    'holster': {'default':0.3, 'karambit':0.35,'bayonet':0.3, 'butterfly':0.3},
}


class KnifeViewModel:
    def __init__(self, base, economy):
        self.base    = base
        self.economy = economy
        self._state  = 'idle'
        self._timer  = 0.0
        self._idle_t = 0.0
        self._knife  = economy.equipped_knife

        self._setup_camera()
        self._vm_root    = None
        self._handle_a   = None
        self._handle_b   = None
        self._butterfly_flip = 0.0
        self._build_knife(self._knife)

    def _setup_camera(self):
        self.base.camNode.setCameraMask(BitMask32.bit(0))
        self._vm_cam = self.base.makeCamera(self.base.win, sort=10)
        self._vm_cam.node().setCameraMask(VM_MASK)
        lens = self._vm_cam.node().getLens()
        lens.setFov(65)
        lens.setNear(0.01)
        lens.setFar(50)
        dr = self._vm_cam.node().getDisplayRegion(0)
        dr.setClearDepthActive(True)

        alight = AmbientLight('vm_ambient')
        alight.setColor(Vec4(0.6, 0.6, 0.6, 1))
        self._vm_alight = self.base.render.attachNewNode(alight)
        dlight = DirectionalLight('vm_sun')
        dlight.setColor(Vec4(1.0, 0.95, 0.85, 1))
        self._vm_dlight = self.base.render.attachNewNode(dlight)
        self._vm_dlight.setHpr(30, -60, 0)

    def _build_knife(self, knife_id):
        if self._vm_root:
            self._vm_root.removeNode()
        self._handle_a = None
        self._handle_b = None

        self._vm_root = self.base.render.attachNewNode('vm_root')
        self._vm_root.setLight(self._vm_alight)
        self._vm_root.setLight(self._vm_dlight)
        self._vm_root.hide(BitMask32.bit(0))
        self._vm_root.show(VM_MASK)

        if knife_id == 'default':
            _build_default(self._vm_root)
        elif knife_id == 'karambit':
            _build_karambit(self._vm_root)
        elif knife_id == 'bayonet':
            _build_bayonet(self._vm_root)
        elif knife_id == 'butterfly':
            _, self._handle_a, self._handle_b = _build_butterfly(self._vm_root)

        skin_id = self.economy.get_equipped_skin(knife_id)
        from game.skins import apply_skin_to_node
        apply_skin_to_node(self._vm_root, skin_id, self.base.loader)

        self._knife = knife_id
        self._state = 'holstered'
        self._timer = 0.0

    def draw(self):
        if self._state == 'holstered':
            self._state = 'draw'
            self._timer = 0.0
            if self._knife == 'butterfly' and self._handle_a:
                self._butterfly_flip = 0.0

    def holster(self):
        if self._state == 'idle':
            self._state = 'holster'
            self._timer = 0.0

    def slash(self):
        if self._state == 'idle':
            self._state = 'slash'
            self._timer = 0.0

    def stab(self):
        if self._state == 'idle':
            self._state = 'stab'
            self._timer = 0.0

    def inspect(self):
        if self._state == 'idle':
            self._state = 'inspect'
            self._timer = 0.0

    def switch_knife(self, knife_id):
        if knife_id == self._knife:
            return
        if self._state not in ('idle', 'holstered'):
            return
        self._build_knife(knife_id)
        self.draw()

    def refresh_skin(self):
        skin_id = self.economy.get_equipped_skin(self._knife)
        from game.skins import apply_skin_to_node
        apply_skin_to_node(self._vm_root, skin_id, self.base.loader)

    def update(self, dt, cam_np):
        if not self._vm_root:
            return
        if self._state == 'holstered':
            self._vm_root.hide()
            return
        self._vm_root.show(VM_MASK)

        self._timer += dt
        state = self._state if self._state != 'holster' else 'holster'
        knife  = self._knife
        frames = ANIMS.get(knife, ANIMS['default']).get(state, ANIMS['default']['idle'])
        dur    = ANIM_DURATIONS.get(state, {}).get(knife, 1.0) if state != 'idle' else 2.0

        if state == 'idle':
            self._idle_t += dt
            t = self._idle_t % 2.0
            frames = ANIMS.get(knife, ANIMS['default'])['idle']
        else:
            t = self._timer

        pos, hpr = self._eval_frames(frames, t)

        if self._knife == 'butterfly' and self._handle_a:
            if state == 'draw':
                flip_t = min(self._timer / dur, 1.0)
                angle  = 90 * (1 - flip_t)
                self._handle_a.setH(-angle)
                self._handle_b.setH( angle)
            elif state == 'idle':
                bob = math.sin(self._idle_t * 2.5) * 2.0
                self._handle_a.setH(-bob)
                self._handle_b.setH( bob)

        self._vm_root.setPos(cam_np.getPos(self.base.render))
        self._vm_root.setHpr(cam_np.getHpr(self.base.render))
        self._vm_root.setScale(1)
        child_np = self._vm_root.getChildren()[0] if self._vm_root.getNumChildren() else self._vm_root
        self._vm_root.setPos(
            cam_np.getPos(self.base.render)
            + cam_np.getQuat(self.base.render).xform(pos)
        )
        self._vm_root.setHpr(
            cam_np.getHpr(self.base.render).x + hpr.x,
            cam_np.getHpr(self.base.render).y + hpr.y,
            cam_np.getHpr(self.base.render).z + hpr.z,
        )
        self._vm_root.setScale(3.0)

        if state not in ('idle',) and self._timer >= dur:
            if state == 'draw':
                self._state = 'idle'
            elif state in ('slash', 'stab', 'inspect'):
                self._state = 'idle'
            elif state == 'holster':
                self._state = 'holstered'

    def _eval_frames(self, frames, t):
        if len(frames) == 1:
            return frames[0].pos, frames[0].hpr
        for i in range(len(frames) - 1):
            f0, f1 = frames[i], frames[i+1]
            if f0.time <= t <= f1.time:
                span = f1.time - f0.time
                if span < 0.0001:
                    return f1.pos, f1.hpr
                lt = (t - f0.time) / span
                return _lerp_vec3(f0.pos, f1.pos, lt), _lerp_vec3(f0.hpr, f1.hpr, lt)
        last = frames[-1]
        return last.pos, last.hpr

    def cleanup(self):
        if self._vm_root:
            self._vm_root.removeNode()
        self._vm_alight.removeNode()
        self._vm_dlight.removeNode()
