import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from direct.showbase.ShowBase import ShowBase
from panda3d.core import WindowProperties, Vec3, loadPrcFileData

loadPrcFileData('', 'window-title Surf')
loadPrcFileData('', 'win-size 1280 720')
loadPrcFileData('', 'framebuffer-multisample 1')
loadPrcFileData('', 'multisamples 4')

from game.economy import Economy
from game.skins   import generate_all


class SurfGame(ShowBase):
    def __init__(self):
        super().__init__()

        self.economy = Economy()
        generate_all()

        self._scene   = None
        self._player  = None
        self._hud     = None
        self._map_obj = None

        self.accept('escape', self._on_escape)
        self.taskMgr.add(self._update, 'main_update')

        self._show_main_menu()

    # ── Scene transitions ──────────────────────────────────────────────────

    def _clear_scene(self):
        if self._hud:
            self._hud.cleanup()
            self._hud = None
        if self._player:
            self._player.cleanup()
            self._player = None
        if self._map_obj:
            self._map_obj.cleanup()
            self._map_obj = None
        if self._scene:
            self._scene.cleanup()
            self._scene = None
        self.render.clearLight()

    def _show_main_menu(self):
        self._clear_scene()
        self.setBackgroundColor(0.06, 0.06, 0.10, 1)
        from ui.main_menu import MainMenu
        self._scene = MainMenu(
            self,
            on_play=self._show_map_select,
            on_shop=self._show_shop,
            on_quit=sys.exit,
        )

    def _show_map_select(self):
        self._clear_scene()
        self.setBackgroundColor(0.06, 0.06, 0.10, 1)
        from ui.map_select import MapSelectScreen
        self._scene = MapSelectScreen(
            self,
            self.economy,
            on_select=self._start_map,
            on_back=self._show_main_menu,
        )

    def _show_shop(self, return_to_game=False):
        if self._player:
            self._player.cleanup()
            self._player = None
        if self._hud:
            self._hud.cleanup()
            self._hud = None

        self._shop_return_game = return_to_game
        self._clear_scene()
        self.setBackgroundColor(0.05, 0.05, 0.08, 1)
        from ui.knife_shop import KnifeShop
        self._scene = KnifeShop(
            self,
            self.economy,
            on_back=self._on_shop_back,
            on_equip_changed=None,
        )

    def _on_shop_back(self):
        if self._shop_return_game and self._pending_map_index is not None:
            self._start_map(self._pending_map_index)
        else:
            self._show_main_menu()

    def _start_map(self, map_index):
        self._pending_map_index = map_index
        self._clear_scene()

        map_classes = self._get_map_classes()
        MapClass    = map_classes[map_index]

        self._map_obj = MapClass(self.render, self)
        self._map_obj.build()

        sky = self._map_obj.SKY_COLOR
        self.setBackgroundColor(*sky)

        from game.player import Player
        from game.hud    import HUD

        self._player = Player(self, self.economy)
        self._player.map_ref  = self._map_obj
        self._player.on_finish = self._on_map_finish

        pos, hpr = self._map_obj.get_spawn()
        self._player.spawn(pos, hpr)

        self._hud = HUD(self, self.economy, self._map_obj.NAME)
        self._hud.start_timer()
        self._map_index = map_index

    def _get_map_classes(self):
        from maps.map_beginner     import MapBeginner
        from maps.map_intermediate import MapIntermediate
        from maps.map_advanced     import MapAdvanced
        return [MapBeginner, MapIntermediate, MapAdvanced]

    def _on_map_finish(self):
        if not self._hud:
            return
        elapsed = self._hud.stop_timer()
        reward, pb = self.economy.complete_map(self._map_index, elapsed)
        msg = f'FINISHED!  +${reward:,}'
        if pb:
            msg += '  ★ NEW BEST'
        self._hud.show_notify(msg, 4.0)

    def _on_escape(self):
        if self._player:
            self._player._capture_mouse(False)
            self._show_main_menu()
        elif self._scene:
            self._show_main_menu()
        else:
            self._show_main_menu()

    # ── Main loop ──────────────────────────────────────────────────────────

    def _update(self, task):
        dt = self.taskMgr.globalClock.getDt()
        dt = min(dt, 0.05)
        if self._player:
            self._player.update(dt)
        if self._hud and self._player:
            speed = self._player.physics.velocity.length()
            self._hud.update(dt, speed)
        return task.cont


if __name__ == '__main__':
    game = SurfGame()
    game.run()
