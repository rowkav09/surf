from direct.gui.DirectGui import DirectFrame, DirectButton, DirectLabel
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import TextNode

MAP_INFO = [
    {'name': 'surf_beginner',     'label': 'BEGINNER',     'reward': '$500',  'difficulty': 1},
    {'name': 'surf_intermediate', 'label': 'INTERMEDIATE', 'reward': '$1,000','difficulty': 2},
    {'name': 'surf_advanced',     'label': 'ADVANCED',     'reward': '$2,000','difficulty': 3},
]

DOT_COLORS = {
    1: (0.3, 0.85, 0.3, 1),
    2: (0.95, 0.75, 0.1, 1),
    3: (0.90, 0.15, 0.15, 1),
}


class MapSelectScreen:
    def __init__(self, base, economy, on_select, on_back):
        self.base     = base
        self.economy  = economy
        self._widgets = []

        bg = DirectFrame(
            frameColor=(0.06, 0.06, 0.10, 1),
            frameSize=(-2, 2, -1.2, 1.2),
        )
        self._widgets.append(bg)

        title = OnscreenText(
            text='SELECT MAP',
            pos=(0, 0.82),
            scale=0.08,
            fg=(1, 1, 1, 1),
            shadow=(0, 0, 0, 0.7),
            align=TextNode.ACenter,
        )
        self._widgets.append(title)

        card_xs = [-1.0, 0.0, 1.0]
        card_colors = [
            (0.10, 0.20, 0.30, 1),
            (0.08, 0.18, 0.22, 1),
            (0.22, 0.08, 0.08, 1),
        ]

        for i, info in enumerate(MAP_INFO):
            cx   = card_xs[i]
            best = economy.best_times.get(str(i))
            best_str = economy.format_time(best)
            diff_str = '★' * info['difficulty'] + '☆' * (3 - info['difficulty'])
            card = DirectFrame(
                frameColor=card_colors[i],
                frameSize=(-0.40, 0.40, -0.48, 0.48),
                pos=(cx, 0, 0.10),
            )
            self._widgets.append(card)

            lbl = OnscreenText(
                text=info['label'],
                pos=(cx, 0.52),
                scale=0.055,
                fg=(1, 1, 1, 1),
                shadow=(0, 0, 0, 0.6),
                align=TextNode.ACenter,
            )
            self._widgets.append(lbl)

            diff_lbl = OnscreenText(
                text=diff_str,
                pos=(cx, 0.40),
                scale=0.05,
                fg=DOT_COLORS[info['difficulty']],
                align=TextNode.ACenter,
            )
            self._widgets.append(diff_lbl)

            time_lbl = OnscreenText(
                text=f'BEST: {best_str}',
                pos=(cx, 0.28),
                scale=0.038,
                fg=(0.7, 0.9, 0.7, 1),
                align=TextNode.ACenter,
            )
            self._widgets.append(time_lbl)

            reward_lbl = OnscreenText(
                text=f'REWARD: {info["reward"]}',
                pos=(cx, 0.19),
                scale=0.035,
                fg=(0.9, 0.80, 0.2, 1),
                align=TextNode.ACenter,
            )
            self._widgets.append(reward_lbl)

            idx = i
            play_btn = DirectButton(
                text='PLAY',
                pos=(cx, 0, -0.30),
                frameColor=(0.20, 0.55, 0.20, 1),
                text_fg=(1, 1, 1, 1),
                text_scale=0.06,
                frameSize=(-0.30, 0.30, -0.06, 0.07),
                command=lambda mi=idx: on_select(mi),
            )
            self._widgets.append(play_btn)

        back_btn = DirectButton(
            text='BACK',
            pos=(-1.55, 0, -0.88),
            frameColor=(0.35, 0.10, 0.10, 1),
            text_fg=(1, 1, 1, 1),
            text_scale=0.055,
            frameSize=(-0.25, 0.25, -0.055, 0.065),
            command=on_back,
        )
        self._widgets.append(back_btn)

    def cleanup(self):
        for w in self._widgets:
            w.destroy()
