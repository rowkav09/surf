import math
from panda3d.core import Vec3
from maps.base_map import BaseMap, make_ramp, make_platform, make_trigger, setup_lighting, make_kill_floor


class MapIntermediate(BaseMap):
    NAME      = 'surf_intermediate'
    MAP_INDEX = 1
    SKY_COLOR = (0.08, 0.06, 0.18, 1)
    SPAWN_POS = Vec3(50, 20, 420)
    SPAWN_HPR = Vec3(90, -10, 0)

    REWARD    = 1000
    PB_BONUS  = 300

    def build(self):
        r = self.root
        lights = setup_lighting(r)
        self._lights.extend(lights)

        TEAL    = (0.10, 0.55, 0.52, 1)
        TEAL_D  = (0.07, 0.38, 0.36, 1)
        FLOOR_C = (0.08, 0.08, 0.10, 1)

        make_platform(r, -200, -50, -100, 1200, 300, FLOOR_C)

        # --- Stage 1 ---
        # ramp 1
        make_ramp(r, x=0,   y=0, z=220, length=320, width=100, angle_deg=-30, color=TEAL, axis='x')
        # ramp 2 — opposite side (right side)
        make_ramp(r, x=360, y=100, z=80, length=280, width=100, angle_deg=-32, color=TEAL_D, axis='x')
        # ramp 3 — curved section (6 segments, each 10 deg rotation in Y)
        base_x, base_y, base_z = 680, 0, -10
        seg_len = 60
        for i in range(6):
            rot = math.radians(i * 10)
            dx = seg_len * math.cos(rot)
            dy = seg_len * math.sin(rot)
            make_ramp(r,
                      x=int(base_x + i*dx), y=int(base_y + i*dy),
                      z=int(base_z - i*8),
                      length=int(seg_len + 5), width=80,
                      angle_deg=-35, color=TEAL, axis='x')

        # mid checkpoint platform
        make_platform(r, 1050, -30, -80, 80, 160, (0.15, 0.35, 0.35, 1))

        # --- Stage 2 ---
        ox = 1130
        # left ramp
        make_ramp(r, x=ox,      y=0,   z=-60,  length=260, width=80, angle_deg=-38, color=TEAL, axis='x')
        # right ramp (opposite side, player must cross gap)
        make_ramp(r, x=ox+300,  y=100, z=-140, length=240, width=80, angle_deg=-35, color=TEAL_D, axis='x')
        # ramp 6
        make_ramp(r, x=ox+580,  y=0,   z=-200, length=220, width=90, angle_deg=-30, color=TEAL, axis='x')
        # ramp 7 — final ramp into end zone
        make_ramp(r, x=ox+830,  y=0,   z=-240, length=180, width=90, angle_deg=-28, color=TEAL, axis='x')

        # connecting platforms stage 2
        make_platform(r, ox+280, 0, -155, 30, 90, FLOOR_C)
        make_platform(r, ox+560, 0, -220, 30, 90, FLOOR_C)

        # end platform
        make_platform(r, ox+1010, 0, -270, 140, 90, (0.20, 0.55, 0.20, 1))

        self.end_trigger = make_trigger(r, ox+1080, 45, -250, 100, 90, 80, name='end_zone')

        make_kill_floor(r, -50, 400, 1200, z=-420)
        self.kill_z = -420
