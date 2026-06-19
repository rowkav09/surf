import json
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'player_data.json')

KNIFE_PRICES = {
    'default':   0,
    'karambit':  2500,
    'bayonet':   2000,
    'butterfly': 3000,
}

SKIN_PRICES = {
    'vanilla':         0,
    'fade':          400,
    'doppler_p1':    500,
    'doppler_p2':    500,
    'doppler_p3':    500,
    'doppler_p4':    500,
    'doppler_ruby':  800,
    'doppler_sapphire': 800,
    'doppler_blackpearl': 1200,
    'gamma_doppler': 500,
    'marble_fade':   600,
    'tiger_tooth':   350,
    'crimson_web':   450,
    'case_hardened': 400,
    'slaughter':     350,
    'lore':          600,
    'autotronic':    400,
    'night_stripe':  250,
    'freehand':      300,
    'stained':       200,
    'blue_steel':    200,
    'damascus_steel': 300,
    'rust_coat':     150,
    'ultraviolet':   350,
    'bright_water':  350,
}

SKIN_DISPLAY_NAMES = {
    'vanilla':            'Vanilla',
    'fade':               'Fade',
    'doppler_p1':         'Doppler Phase 1',
    'doppler_p2':         'Doppler Phase 2',
    'doppler_p3':         'Doppler Phase 3',
    'doppler_p4':         'Doppler Phase 4',
    'doppler_ruby':       'Doppler Ruby',
    'doppler_sapphire':   'Doppler Sapphire',
    'doppler_blackpearl': 'Doppler Black Pearl',
    'gamma_doppler':      'Gamma Doppler',
    'marble_fade':        'Marble Fade',
    'tiger_tooth':        'Tiger Tooth',
    'crimson_web':        'Crimson Web',
    'case_hardened':      'Case Hardened',
    'slaughter':          'Slaughter',
    'lore':               'Lore',
    'autotronic':         'Autotronic',
    'night_stripe':       'Night Stripe',
    'freehand':           'Freehand',
    'stained':            'Stained',
    'blue_steel':         'Blue Steel',
    'damascus_steel':     'Damascus Steel',
    'rust_coat':          'Rust Coat',
    'ultraviolet':        'Ultraviolet',
    'bright_water':       'Bright Water',
}

MAP_REWARDS = {0: 500, 1: 1000, 2: 2000}
PB_BONUS = 300

_DEFAULT_DATA = {
    'money': 0,
    'owned_knives': ['default'],
    'equipped_knife': 'default',
    'best_times': {'0': None, '1': None, '2': None},
    'knife_skins': {
        'default':   'vanilla',
        'karambit':  'vanilla',
        'bayonet':   'vanilla',
        'butterfly': 'vanilla',
    },
    'owned_skins': {
        'default':   ['vanilla'],
        'karambit':  ['vanilla'],
        'bayonet':   ['vanilla'],
        'butterfly': ['vanilla'],
    },
}


class Economy:
    def __init__(self):
        os.makedirs(os.path.dirname(os.path.abspath(DATA_PATH)), exist_ok=True)
        self.load()

    def load(self):
        try:
            with open(DATA_PATH, 'r') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {}
        self.money          = data.get('money', _DEFAULT_DATA['money'])
        self.owned_knives   = set(data.get('owned_knives', _DEFAULT_DATA['owned_knives']))
        self.equipped_knife = data.get('equipped_knife', _DEFAULT_DATA['equipped_knife'])
        self.best_times     = data.get('best_times', dict(_DEFAULT_DATA['best_times']))
        self.knife_skins    = data.get('knife_skins', dict(_DEFAULT_DATA['knife_skins']))
        raw_owned_skins     = data.get('owned_skins', _DEFAULT_DATA['owned_skins'])
        self.owned_skins    = {k: list(v) for k, v in raw_owned_skins.items()}
        for knife in ('default', 'karambit', 'bayonet', 'butterfly'):
            self.owned_skins.setdefault(knife, ['vanilla'])
            self.knife_skins.setdefault(knife, 'vanilla')

    def save(self):
        tmp = DATA_PATH + '.tmp'
        payload = {
            'money':        self.money,
            'owned_knives': list(self.owned_knives),
            'equipped_knife': self.equipped_knife,
            'best_times':   self.best_times,
            'knife_skins':  self.knife_skins,
            'owned_skins':  self.owned_skins,
        }
        with open(tmp, 'w') as f:
            json.dump(payload, f, indent=2)
        os.replace(tmp, DATA_PATH)

    def complete_map(self, map_index, time_seconds):
        key = str(map_index)
        current_best = self.best_times.get(key)
        pb_beaten = (current_best is None or time_seconds < current_best)
        reward = MAP_REWARDS.get(map_index, 0)
        if pb_beaten:
            reward += PB_BONUS
            self.best_times[key] = round(time_seconds, 2)
        self.money += reward
        self.save()
        return reward, pb_beaten

    def purchase_knife(self, knife_id):
        if knife_id in self.owned_knives:
            return False, 'Already owned'
        price = KNIFE_PRICES.get(knife_id, 0)
        if self.money < price:
            return False, 'Insufficient funds'
        self.money -= price
        self.owned_knives.add(knife_id)
        self.save()
        return True, 'Purchased'

    def purchase_skin(self, knife_id, skin_id):
        owned = self.owned_skins.get(knife_id, [])
        if skin_id in owned:
            return False, 'Already owned'
        price = SKIN_PRICES.get(skin_id, 0)
        if self.money < price:
            return False, 'Insufficient funds'
        self.money -= price
        owned.append(skin_id)
        self.owned_skins[knife_id] = owned
        self.save()
        return True, 'Purchased'

    def equip_knife(self, knife_id):
        if knife_id in self.owned_knives:
            self.equipped_knife = knife_id
            self.save()
            return True
        return False

    def equip_skin(self, knife_id, skin_id):
        if skin_id in self.owned_skins.get(knife_id, []):
            self.knife_skins[knife_id] = skin_id
            self.save()
            return True
        return False

    def get_equipped_skin(self, knife_id=None):
        if knife_id is None:
            knife_id = self.equipped_knife
        return self.knife_skins.get(knife_id, 'vanilla')

    def format_time(self, seconds):
        if seconds is None:
            return '--:--.--'
        m = int(seconds) // 60
        s = seconds % 60
        return f'{m:02d}:{s:05.2f}'
