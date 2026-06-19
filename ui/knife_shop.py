from direct.gui.DirectGui import (
    DirectFrame, DirectButton, DirectLabel, DirectScrolledList
)
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import TextNode
from game.economy import KNIFE_PRICES, SKIN_PRICES, SKIN_DISPLAY_NAMES


KNIFE_DISPLAY = {
    'default':   'Default Knife',
    'karambit':  'Karambit',
    'bayonet':   'Bayonet',
    'butterfly': 'Butterfly Knife',
}

KNIFE_ORDER = ['default', 'karambit', 'bayonet', 'butterfly']

SKIN_ORDER = [
    'vanilla', 'fade', 'doppler_p1', 'doppler_p2', 'doppler_p3', 'doppler_p4',
    'doppler_ruby', 'doppler_sapphire', 'doppler_blackpearl', 'gamma_doppler',
    'marble_fade', 'tiger_tooth', 'crimson_web', 'case_hardened', 'slaughter',
    'lore', 'autotronic', 'night_stripe', 'freehand', 'stained',
    'blue_steel', 'damascus_steel', 'rust_coat', 'ultraviolet', 'bright_water',
]


class KnifeShop:
    def __init__(self, base, economy, on_back, on_equip_changed=None):
        self.base             = base
        self.economy          = economy
        self.on_back          = on_back
        self.on_equip_changed = on_equip_changed
        self._widgets         = []
        self._selected_knife  = economy.equipped_knife
        self._selected_skin   = economy.get_equipped_skin(self._selected_knife)

        self._build_ui()

    def _build_ui(self):
        bg = DirectFrame(
            frameColor=(0.05, 0.05, 0.08, 1),
            frameSize=(-2, 2, -1.2, 1.2),
        )
        self._widgets.append(bg)

        title = OnscreenText(
            text='KNIFE SHOP',
            pos=(0, 0.87),
            scale=0.08,
            fg=(1, 1, 1, 1),
            shadow=(0, 0, 0, 0.7),
            align=TextNode.ACenter,
        )
        self._widgets.append(title)

        self._balance_txt = OnscreenText(
            text=f'Balance: ${self.economy.money:,}',
            pos=(1.55, 0.87),
            scale=0.05,
            fg=(0.4, 1.0, 0.45, 1),
            align=TextNode.ARight,
        )
        self._widgets.append(self._balance_txt)

        # ── Left panel: knife list ─────────────────────────────────────────
        knife_panel = DirectFrame(
            frameColor=(0.08, 0.08, 0.12, 1),
            frameSize=(-0.42, 0.42, -0.80, 0.72),
            pos=(-1.30, 0, 0.05),
        )
        self._widgets.append(knife_panel)
        OnscreenText(text='KNIFE', pos=(-1.30, 0.77), scale=0.045,
                     fg=(0.7,0.7,0.8,1), align=TextNode.ACenter).__class__
        self._widgets.append(
            OnscreenText(text='KNIFE', pos=(-1.30, 0.77), scale=0.045,
                         fg=(0.7,0.7,0.8,1), align=TextNode.ACenter)
        )

        self._knife_btns = []
        for i, kid in enumerate(KNIFE_ORDER):
            owned = kid in self.economy.owned_knives
            price = KNIFE_PRICES[kid]
            lbl   = KNIFE_DISPLAY[kid]
            lbl   += '' if owned else f'  ${price:,}'
            col   = (0.15, 0.35, 0.15, 1) if owned else (0.25, 0.15, 0.10, 1)
            btn   = DirectButton(
                text=lbl,
                pos=(-1.30, 0, 0.52 - i * 0.28),
                frameColor=col,
                text_fg=(1,1,1,1),
                text_scale=0.045,
                frameSize=(-0.38, 0.38, -0.06, 0.075),
                command=lambda k=kid: self._select_knife(k),
            )
            self._widgets.append(btn)
            self._knife_btns.append((kid, btn))

        # ── Middle panel: skin list ────────────────────────────────────────
        skin_panel = DirectFrame(
            frameColor=(0.08, 0.08, 0.12, 1),
            frameSize=(-0.42, 0.42, -0.80, 0.72),
            pos=(0.0, 0, 0.05),
        )
        self._widgets.append(skin_panel)
        self._widgets.append(
            OnscreenText(text='FINISH', pos=(0.0, 0.77), scale=0.045,
                         fg=(0.7,0.7,0.8,1), align=TextNode.ACenter)
        )
        self._skin_btns = []
        self._build_skin_list()

        # ── Right panel: info + buy ────────────────────────────────────────
        info_panel = DirectFrame(
            frameColor=(0.08, 0.08, 0.12, 1),
            frameSize=(-0.42, 0.42, -0.80, 0.72),
            pos=(1.30, 0, 0.05),
        )
        self._widgets.append(info_panel)

        self._info_knife_txt = OnscreenText(
            text=KNIFE_DISPLAY[self._selected_knife],
            pos=(1.30, 0.70),
            scale=0.055,
            fg=(1, 1, 1, 1),
            align=TextNode.ACenter,
        )
        self._widgets.append(self._info_knife_txt)
        self._info_skin_txt = OnscreenText(
            text=SKIN_DISPLAY_NAMES[self._selected_skin],
            pos=(1.30, 0.58),
            scale=0.048,
            fg=(0.85, 0.80, 0.5, 1),
            align=TextNode.ACenter,
        )
        self._widgets.append(self._info_skin_txt)
        self._info_price_txt = OnscreenText(
            text='',
            pos=(1.30, 0.46),
            scale=0.048,
            fg=(0.9, 0.75, 0.2, 1),
            align=TextNode.ACenter,
        )
        self._widgets.append(self._info_price_txt)
        self._info_status_txt = OnscreenText(
            text='',
            pos=(1.30, 0.34),
            scale=0.042,
            fg=(0.5, 1.0, 0.5, 1),
            align=TextNode.ACenter,
        )
        self._widgets.append(self._info_status_txt)

        self._buy_btn = DirectButton(
            text='BUY',
            pos=(1.30, 0, 0.10),
            frameColor=(0.2, 0.5, 0.2, 1),
            text_fg=(1, 1, 1, 1),
            text_scale=0.06,
            frameSize=(-0.32, 0.32, -0.07, 0.08),
            command=self._on_buy,
        )
        self._widgets.append(self._buy_btn)

        self._equip_btn = DirectButton(
            text='EQUIP',
            pos=(1.30, 0, -0.08),
            frameColor=(0.15, 0.30, 0.55, 1),
            text_fg=(1, 1, 1, 1),
            text_scale=0.06,
            frameSize=(-0.32, 0.32, -0.07, 0.08),
            command=self._on_equip,
        )
        self._widgets.append(self._equip_btn)

        back_btn = DirectButton(
            text='BACK',
            pos=(-1.55, 0, -0.95),
            frameColor=(0.35, 0.10, 0.10, 1),
            text_fg=(1, 1, 1, 1),
            text_scale=0.055,
            frameSize=(-0.25, 0.25, -0.055, 0.065),
            command=self.on_back,
        )
        self._widgets.append(back_btn)

        self._update_info()

    def _build_skin_list(self):
        for old in self._skin_btns:
            old.destroy()
        self._skin_btns = []
        knife = self._selected_knife
        visible_skins = SKIN_ORDER[:13]
        scroll_items  = []
        for sid in SKIN_ORDER:
            owned = sid in self.economy.owned_skins.get(knife, ['vanilla'])
            price = SKIN_PRICES[sid]
            lbl   = SKIN_DISPLAY_NAMES[sid]
            lbl  += '' if owned else f'  ${price:,}'
            equipped = (sid == self.economy.get_equipped_skin(knife))
            col = (0.10, 0.35, 0.10, 1) if equipped else \
                  (0.12, 0.25, 0.12, 1) if owned else \
                  (0.22, 0.18, 0.10, 1)
            btn = DirectButton(
                text=lbl,
                frameColor=col,
                text_fg=(1,1,1,1),
                text_scale=0.038,
                frameSize=(-0.38, 0.38, -0.05, 0.06),
                command=lambda s=sid: self._select_skin(s),
            )
            self._skin_btns.append(btn)
            scroll_items.append(btn)

        if hasattr(self, '_skin_scroll') and self._skin_scroll:
            self._skin_scroll.destroy()
        self._skin_scroll = DirectScrolledList(
            decButton_pos=(-0.37, 0, -0.73),
            decButton_text='▼',
            decButton_text_scale=0.04,
            decButton_frameSize=(-0.38, 0.38, -0.04, 0.05),
            incButton_pos=(-0.37, 0, 0.68),
            incButton_text='▲',
            incButton_text_scale=0.04,
            incButton_frameSize=(-0.38, 0.38, -0.04, 0.05),
            frameSize=(-0.42, 0.42, -0.80, 0.72),
            frameColor=(0,0,0,0),
            pos=(0.0, 0, 0.05),
            numItemsVisible=10,
            itemFrame_frameSize=(-0.38, 0.38, -0.60, 0.62),
            itemFrame_pos=(0, 0, 0),
            items=scroll_items,
        )
        self._widgets.append(self._skin_scroll)

    def _select_knife(self, knife_id):
        self._selected_knife = knife_id
        self._selected_skin  = self.economy.get_equipped_skin(knife_id)
        self._build_skin_list()
        self._update_info()

    def _select_skin(self, skin_id):
        self._selected_skin = skin_id
        self._update_info()

    def _update_info(self):
        kid = self._selected_knife
        sid = self._selected_skin
        knife_owned = kid in self.economy.owned_knives
        skin_owned  = sid in self.economy.owned_skins.get(kid, ['vanilla'])

        self._info_knife_txt.setText(KNIFE_DISPLAY[kid])
        self._info_skin_txt.setText(SKIN_DISPLAY_NAMES[sid])
        self._balance_txt.setText(f'Balance: ${self.economy.money:,}')

        if not knife_owned:
            price = KNIFE_PRICES[kid]
            self._info_price_txt.setText(f'Knife: ${price:,}')
            self._info_status_txt.setText('NOT OWNED')
            self._buy_btn['text'] = f'BUY KNIFE'
            self._buy_btn['frameColor'] = (0.45, 0.20, 0.10, 1)
        elif not skin_owned:
            price = SKIN_PRICES[sid]
            self._info_price_txt.setText(f'Skin: ${price:,}')
            self._info_status_txt.setText('SKIN NOT OWNED')
            self._buy_btn['text'] = 'BUY SKIN'
            self._buy_btn['frameColor'] = (0.20, 0.40, 0.20, 1)
        else:
            self._info_price_txt.setText('')
            self._info_status_txt.setText('OWNED')
            self._buy_btn['text'] = 'OWNED'
            self._buy_btn['frameColor'] = (0.15, 0.15, 0.18, 1)

        equipped_knife = self.economy.equipped_knife
        equipped_skin  = self.economy.get_equipped_skin(kid)
        if kid == equipped_knife and sid == equipped_skin:
            self._equip_btn['text'] = 'EQUIPPED'
            self._equip_btn['frameColor'] = (0.10, 0.45, 0.10, 1)
        else:
            self._equip_btn['text'] = 'EQUIP'
            self._equip_btn['frameColor'] = (0.15, 0.30, 0.55, 1)

    def _on_buy(self):
        kid = self._selected_knife
        sid = self._selected_skin
        if kid not in self.economy.owned_knives:
            ok, msg = self.economy.purchase_knife(kid)
        else:
            ok, msg = self.economy.purchase_skin(kid, sid)
        self._build_skin_list()
        self._update_info()

    def _on_equip(self):
        kid = self._selected_knife
        sid = self._selected_skin
        if kid in self.economy.owned_knives:
            self.economy.equip_knife(kid)
        if sid in self.economy.owned_skins.get(kid, []):
            self.economy.equip_skin(kid, sid)
        if self.on_equip_changed:
            self.on_equip_changed(kid, sid)
        self._update_info()

    def cleanup(self):
        for w in self._widgets:
            try:
                w.destroy()
            except Exception:
                pass
        for b in self._skin_btns:
            try:
                b.destroy()
            except Exception:
                pass
