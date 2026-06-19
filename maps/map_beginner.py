from panda3d.core import Vec3
from maps.base_map import BaseMap, make_ramp, make_platform, make_trigger, setup_lighting, make_kill_floor


class MapBeginner(BaseMap):
    NAME      = 'surf_beginner'
    MAP_INDEX = 0
    SKY_COLOR = (0.55, 0.72, 0.90, 1)
    SPAWN_POS = Vec3(50, 20, 380)
    SPAWN_HPR = Vec3(90, -10, 0)

    REWARD    = 500
    PB_BONUS  = 300

    def build(self):
        r = self.root
        lights = setup_lighting(r)
        self._lights.extend(lights)

        ORANGE  = (0.85, 0.45, 0.10, 1)
        FLOOR_C = (0.18, 0.18, 0.20, 1)

        make_platform(r, -300, -50,  -60, 700, 250, FLOOR_C)
        make_platform(r, -300, -50, -300, 700, 250, (0.1, 0.1, 0.1, 1))

        # ramp 1 — gentle entry, 22 degrees, player spawns at high end
        make_ramp(r, x=0,   y=0,  z=200, length=300, width=120, angle_deg=-22, color=ORANGE, axis='x')
        # ramp 2 — slightly steeper
        make_ramp(r, x=340, y=0,  z=80,  length=280, width=120, angle_deg=-25, color=ORANGE, axis='x')
        # ramp 3 — left side ramp (Y axis), curves the route
        make_ramp(r, x=380, y=130,z=10,  length=200, width=100, angle_deg=-28, color=(0.75, 0.40, 0.08, 1), axis='y')
        # ramp 4 — final short ramp into end zone
        make_ramp(r, x=470, y=0,  z=-30, length=150, width=120, angle_deg=-20, color=ORANGE, axis='x')

        # connecting platforms between ramps
        make_platform(r, 300, 0, 68, 40, 120, FLOOR_C)
        make_platform(r, 620, 0, -42, 50, 120, FLOOR_C)

        # end platform
        make_platform(r, 620, 0, -60, 120, 120, (0.20, 0.55, 0.20, 1))

        # end trigger
        self.end_trigger = make_trigger(r, 680, 60, -40, 100, 120, 80, name='end_zone')

        make_kill_floor(r, -50, 200, 700, z=-350)

        self.kill_z = -350
