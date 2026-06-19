from panda3d.core import Vec3
from maps.base_map import BaseMap, make_ramp, make_platform, make_trigger, setup_lighting, make_kill_floor


class MapAdvanced(BaseMap):
    NAME      = 'surf_advanced'
    MAP_INDEX = 2
    SKY_COLOR = (0.04, 0.04, 0.12, 1)
    SPAWN_POS = Vec3(50, 20, 500)
    SPAWN_HPR = Vec3(90, -10, 0)

    REWARD    = 2000
    PB_BONUS  = 300

    def build(self):
        r = self.root
        lights = setup_lighting(r)
        self._lights.extend(lights)

        RED    = (0.72, 0.08, 0.08, 1)
        RED_D  = (0.50, 0.05, 0.05, 1)
        FLOOR_C = (0.06, 0.06, 0.08, 1)

        make_platform(r, -200, -50, -150, 1600, 350, FLOOR_C)

        # ---- Stage 1: Steep entry + direction reversal ----
        # steep entry ramp (50 deg)
        make_ramp(r, x=0,   y=0, z=300, length=280, width=90, angle_deg=-50, color=RED, axis='x')
        # direction reversal — ramp going back opposite
        make_ramp(r, x=320, y=110, z=60, length=260, width=90, angle_deg=-48, color=RED_D, axis='x')
        # third ramp slightly wider
        make_ramp(r, x=620, y=0, z=-70, length=240, width=90, angle_deg=-42, color=RED, axis='x')

        # stage 1 end platform
        make_platform(r, 900, 0, -170, 60, 90, (0.18, 0.08, 0.08, 1))

        # ---- Stage 2: Tight corridor (60-unit wide ramps) ----
        ox = 960
        # left wall ramp
        make_ramp(r, x=ox,      y=0,  z=-140, length=300, width=60, angle_deg=-44, color=RED,   axis='x')
        # right wall ramp, mirror
        make_ramp(r, x=ox+20,   y=70, z=-140, length=300, width=60, angle_deg=-44, color=RED_D, axis='x')
        # second corridor pair
        make_ramp(r, x=ox+340,  y=0,  z=-270, length=260, width=60, angle_deg=-40, color=RED,   axis='x')
        make_ramp(r, x=ox+360,  y=70, z=-270, length=260, width=60, angle_deg=-40, color=RED_D, axis='x')

        # stage 2 end platform
        make_platform(r, ox+650, 0, -380, 60, 90, (0.18, 0.08, 0.08, 1))

        # ---- Stage 3: Trick jump finale ----
        ox2 = ox + 710
        # downward boost ramp — player hits this and launches upward
        make_ramp(r, x=ox2,     y=0,  z=-350, length=180, width=90, angle_deg=-55, color=RED, axis='x')
        # elevated ramp — player must catch this after the jump
        make_ramp(r, x=ox2+220, y=0,  z=-240, length=220, width=90, angle_deg=-38, color=RED_D, axis='x')
        # final ramp
        make_ramp(r, x=ox2+480, y=0,  z=-310, length=200, width=90, angle_deg=-35, color=RED, axis='x')

        # narrow finishing platforms
        make_platform(r, ox2+700, 20, -380, 80, 50, (0.20, 0.55, 0.20, 1))
        make_platform(r, ox2+780, 20, -380, 80, 50, (0.20, 0.55, 0.20, 1))

        self.end_trigger = make_trigger(r, ox2+820, 45, -360, 80, 50, 80, name='end_zone')

        make_kill_floor(r, -50, 600, 1600, z=-550)
        self.kill_z = -550
