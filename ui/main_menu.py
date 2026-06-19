from direct.gui.DirectGui import DirectFrame, DirectButton, DirectLabel
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import TextNode


class MainMenu:
    def __init__(self, base, on_play, on_shop, on_quit):
        self.base = base
        self._widgets = []

        bg = DirectFrame(
            frameColor=(0.06, 0.06, 0.10, 1),
            frameSize=(-2, 2, -1.2, 1.2),
            pos=(0, 0, 0),
        )
        self._widgets.append(bg)

        title = OnscreenText(
            text='SURF',
            pos=(0, 0.65),
            scale=0.22,
            fg=(0.9, 0.35, 0.05, 1),
            shadow=(0, 0, 0, 0.8),
            align=TextNode.ACenter,
        )
        self._widgets.append(title)

        subtitle = OnscreenText(
            text='CS2 INSPIRED',
            pos=(0, 0.50),
            scale=0.05,
            fg=(0.7, 0.7, 0.8, 1),
            align=TextNode.ACenter,
        )
        self._widgets.append(subtitle)

        btn_kw = dict(
            text_scale=0.07,
            frameSize=(-0.45, 0.45, -0.065, 0.075),
            relief=1,
        )

        play_btn = DirectButton(
            text='PLAY',
            pos=(0, 0, 0.20),
            frameColor=(0.15, 0.55, 0.15, 1),
            text_fg=(1, 1, 1, 1),
            command=on_play,
            **btn_kw,
        )
        self._widgets.append(play_btn)

        shop_btn = DirectButton(
            text='KNIFE SHOP',
            pos=(0, 0, 0.03),
            frameColor=(0.15, 0.30, 0.55, 1),
            text_fg=(1, 1, 1, 1),
            command=on_shop,
            **btn_kw,
        )
        self._widgets.append(shop_btn)

        quit_btn = DirectButton(
            text='QUIT',
            pos=(0, 0, -0.14),
            frameColor=(0.45, 0.10, 0.10, 1),
            text_fg=(1, 1, 1, 1),
            command=on_quit,
            **btn_kw,
        )
        self._widgets.append(quit_btn)

        hint = OnscreenText(
            text='W/A/S/D — move    MOUSE — look    LMB — slash    RMB — stab    I — inspect    R — respawn',
            pos=(0, -0.88),
            scale=0.033,
            fg=(0.5, 0.5, 0.6, 1),
            align=TextNode.ACenter,
        )
        self._widgets.append(hint)

    def cleanup(self):
        for w in self._widgets:
            w.destroy()
