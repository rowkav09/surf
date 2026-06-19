from panda3d.core import (
    CollisionTraverser, CollisionNode, CollisionSphere,
    CollisionHandlerEvent, CollisionHandlerPusher,
    BitMask32, Vec3, Point3, WindowProperties,
)
from direct.showbase.ShowBase import ShowBase
from game.physics import SurfPhysics, build_wish_vector, PLAYER_HEIGHT
from game.knife import KnifeViewModel

SENSITIVITY = 0.15


class Player:
    def __init__(self, base, economy):
        self.base    = base
        self.economy = economy
        self.physics = SurfPhysics()

        self._keys = {
            'w': False, 's': False, 'a': False, 'd': False,
            'space': False,
        }
        self._mouse_dx = 0.0
        self._mouse_dy = 0.0
        self._yaw   = 0.0
        self._pitch = 0.0

        self.cam_node = base.camera
        base.disableMouse()
        self._capture_mouse(True)

        self._setup_collision()

        self.knife = KnifeViewModel(base, economy)
        self.knife.draw()

        self._register_keys()
        self._alive = True
        self.on_finish  = None
        self.map_ref    = None

    def _capture_mouse(self, capture):
        props = WindowProperties()
        if capture:
            props.setMouseMode(WindowProperties.M_confined)
            props.setCursorHidden(True)
        else:
            props.setMouseMode(WindowProperties.M_absolute)
            props.setCursorHidden(False)
        self.base.win.requestProperties(props)

    def _setup_collision(self):
        self.ctrav = CollisionTraverser('player_trav')
        self.chandler = CollisionHandlerPusher()
        self.chandler.setHorizontal(False)

        cnode = CollisionNode('player')
        cnode.setFromCollideMask(BitMask32.bit(2))
        cnode.setIntoCollideMask(BitMask32.allOff())
        cnode.addSolid(CollisionSphere(0, 0, 0, 16))
        cnode.addSolid(CollisionSphere(0, 0, 40, 14))

        self.player_np = self.base.render.attachNewNode(cnode)
        self.chandler.addCollider(self.player_np, self.player_np)
        self.ctrav.addCollider(self.player_np, self.chandler)

        self._event_handler = CollisionHandlerEvent()
        self._event_handler.addInPattern('%fn-into-%in')
        self.ctrav.addCollider(self.player_np, self._event_handler)

        self.base.accept('player-into-ramp_col', self._on_ramp_contact)
        self.base.accept('player-into-platform_col', self._on_ground_contact)
        self.base.accept('player-into-end_zone', self._on_end_zone)

    def _on_ramp_contact(self, entry):
        n = entry.getSurfaceNormal(self.base.render)
        self.physics.add_contact(n)
        p = entry.getSurfacePoint(self.base.render)
        cur = self.physics.position
        diff = cur - Vec3(p)
        if diff.length() < 18:
            self.physics.push_out(entry.getSurfaceNormal(self.base.render) * (18 - diff.length()))

    def _on_ground_contact(self, entry):
        n = entry.getSurfaceNormal(self.base.render)
        self.physics.add_contact(n)

    def _on_end_zone(self, entry):
        if self.on_finish:
            self.on_finish()

    def _register_keys(self):
        b = self.base
        b.accept('w',     lambda: self._set_key('w', True))
        b.accept('w-up',  lambda: self._set_key('w', False))
        b.accept('s',     lambda: self._set_key('s', True))
        b.accept('s-up',  lambda: self._set_key('s', False))
        b.accept('a',     lambda: self._set_key('a', True))
        b.accept('a-up',  lambda: self._set_key('a', False))
        b.accept('d',     lambda: self._set_key('d', True))
        b.accept('d-up',  lambda: self._set_key('d', False))
        b.accept('mouse1', self.knife.slash)
        b.accept('mouse3', self.knife.stab)
        b.accept('i',      self.knife.inspect)
        b.accept('r',      self._respawn)

    def _set_key(self, key, val):
        self._keys[key] = val

    def spawn(self, pos, hpr=None):
        self.physics.position = Vec3(pos)
        self.physics.velocity = Vec3(0, 0, 0)
        self.player_np.setPos(pos)
        if hpr:
            self._yaw   = hpr.x
            self._pitch = hpr.y
        self._alive = True

    def _respawn(self):
        if self.map_ref:
            pos, hpr = self.map_ref.get_spawn()
            self.spawn(pos, hpr)

    def update(self, dt):
        if not self._alive:
            return

        # mouse look
        if self.base.mouseWatcherNode.hasMouse():
            md = self.base.win.getPointer(0)
            cx, cy = self.base.win.getXSize()//2, self.base.win.getYSize()//2
            dx = md.getX() - cx
            dy = md.getY() - cy
            self.base.win.movePointer(0, cx, cy)
            self._yaw   -= dx * SENSITIVITY
            self._pitch  = max(-89, min(89, self._pitch - dy * SENSITIVITY))

        self.cam_node.setHpr(self._yaw, self._pitch, 0)

        # build wish vector
        import math as _m
        yaw_r = _m.radians(self._yaw)
        fwd   = Vec3(-_m.sin(yaw_r), _m.cos(yaw_r), 0)
        right = Vec3(_m.cos(yaw_r),  _m.sin(yaw_r), 0)

        mf = (1 if self._keys['w'] else 0) - (1 if self._keys['s'] else 0)
        mr = (1 if self._keys['d'] else 0) - (1 if self._keys['a'] else 0)
        wishdir, wishspeed = build_wish_vector(fwd, right, mf, mr)

        self.physics.tick(wishdir, wishspeed, dt)

        pos = self.physics.position
        self.player_np.setPos(pos)
        cam_pos = Vec3(pos.x, pos.y, pos.z + PLAYER_HEIGHT * 0.85)
        self.cam_node.setPos(cam_pos)

        self.ctrav.traverse(self.base.render)

        if self.map_ref and pos.z < self.map_ref.kill_z:
            self._respawn()

        self.knife.update(dt, self.cam_node)

    def cleanup(self):
        self._capture_mouse(False)
        self.base.ignoreAll()
        self.player_np.removeNode()
        self.knife.cleanup()
