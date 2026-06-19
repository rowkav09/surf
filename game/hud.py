from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import DirectFrame
from panda3d.core import TextNode, Vec4


class HUD:
    def __init__(self, base, economy, map_name):
        self.base     = base
        self.economy  = economy
        self._timer   = 0.0
        self._running = False

        bg_color = (0, 0, 0, 0.45)
        self._bar = DirectFrame(
            frameColor=bg_color,
            frameSize=(-1.8, 1.8, -0.06, 0.0),
            pos=(0, 0, -0.94),
            parent=base.aspect2d,
        )

        self._speed_txt = OnscreenText(
            text='SPEED: 0',
            pos=(-1.70, -0.96),
            scale=0.045,
            fg=(0.85, 0.90, 1.0, 1),
            shadow=(0, 0, 0, 0.7),
            align=TextNode.ALeft,
            parent=base.aspect2d,
        )
        self._timer_txt = OnscreenText(
            text='00:00.00',
            pos=(0, -0.96),
            scale=0.055,
            fg=(1, 1, 1, 1),
            shadow=(0, 0, 0, 0.8),
            align=TextNode.ACenter,
            parent=base.aspect2d,
        )
        self._money_txt = OnscreenText(
            text=f'${economy.money:,}',
            pos=(1.70, -0.96),
            scale=0.045,
            fg=(0.40, 1.0, 0.45, 1),
            shadow=(0, 0, 0, 0.7),
            align=TextNode.ARight,
            parent=base.aspect2d,
        )
        self._map_txt = OnscreenText(
            text=map_name.upper(),
            pos=(0, 0.90),
            scale=0.040,
            fg=(1, 1, 1, 0.7),
            shadow=(0, 0, 0, 0.5),
            align=TextNode.ACenter,
            parent=base.aspect2d,
        )
        self._cross_h = OnscreenText(
            text='─',
            pos=(-0.012, 0.0),
            scale=0.03,
            fg=(1, 1, 1, 0.85),
            align=TextNode.ACenter,
            parent=base.aspect2d,
        )
        self._cross_v = OnscreenText(
            text='|',
            pos=(0, 0.005),
            scale=0.040,
            fg=(1, 1, 1, 0.85),
            align=TextNode.ACenter,
            parent=base.aspect2d,
        )
        self._notify_txt = OnscreenText(
            text='',
            pos=(0, 0.60),
            scale=0.06,
            fg=(1, 0.85, 0.2, 1),
            shadow=(0, 0, 0, 0.8),
            align=TextNode.ACenter,
            parent=base.aspect2d,
        )
        self._notify_timer = 0.0

    def start_timer(self):
        self._timer   = 0.0
        self._running = True

    def stop_timer(self):
        self._running = False
        return self._timer

    def update(self, dt, speed):
        if self._running:
            self._timer += dt

        self._speed_txt.setText(f'SPEED: {int(speed)}')
        self._timer_txt.setText(self._fmt_time(self._timer))
        self._money_txt.setText(f'${self.economy.money:,}')

        if self._notify_timer > 0:
            self._notify_timer -= dt
            if self._notify_timer <= 0:
                self._notify_txt.setText('')

    def show_notify(self, msg, duration=3.0):
        self._notify_txt.setText(msg)
        self._notify_timer = duration

    def _fmt_time(self, t):
        m = int(t) // 60
        s = t % 60
        return f'{m:02d}:{s:05.2f}'

    def cleanup(self):
        for w in (self._bar, self._speed_txt, self._timer_txt,
                  self._money_txt, self._map_txt,
                  self._cross_h, self._cross_v, self._notify_txt):
            w.destroy()
