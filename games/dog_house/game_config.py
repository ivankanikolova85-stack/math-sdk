"""Dog House - game configuration.

5x3 lines game, 20 paylines, RTP 96%, wincap 5000x.
Base mode  : 1x cost, scatter trigger on reels 1/3/5 (indices 0/2/4).
Bonus mode : 100x cost, direct freegame buy.

Special mechanics
-----------------
* Scatter (S) – only on reels 1, 3, 5 (indices 0, 2, 4). Max 3 per board.
* Wild (W)    – cannot land on reel 1 (index 0). Sticky in freegame; starts at mult 1x.
* DogBooster (DB) – freegame-only symbol; adds +2 to every sticky wild multiplier.
* Freegame spins: random 8-15 on trigger, +10 on retrigger.
* Wincap: 5000x base bet.
"""

import os
from src.config.config import Config
from src.config.distributions import Distribution
from src.config.betmode import BetMode


class GameConfig(Config):

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()
        self.game_id = "dog_house"
        self.provider_number = 0
        self.working_name = "Dog House"
        self.wincap = 5000.0
        self.win_type = "lines"
        self.rtp = 0.9600
        self.construct_paths()

        # Dimensions
        self.num_reels = 5
        self.num_rows = [3] * self.num_reels

        # Paytable — multipliers of total bet / num_lines per line win
        # Wild has no independent pay — substitute only (cannot land on reel 1,
        # so a 5-reel Wild line is mathematically impossible)
        self.paytable = {
            (5, "H1"): 18.75, (4, "H1"): 3.75, (3, "H1"): 1.50,
            (5, "H2"): 12.50, (4, "H2"): 2.50, (3, "H2"): 1.00,
            (5, "H3"):  7.50, (4, "H3"): 1.25, (3, "H3"): 0.75,
            (5, "H4"):  5.00, (4, "H4"): 0.75, (3, "H4"): 0.50,
            (5, "L1"):  3.75, (4, "L1"): 0.50, (3, "L1"): 0.25,
            (5, "L2"):  2.50, (4, "L2"): 0.25, (3, "L2"): 0.20,
            (5, "L3"):  2.50, (4, "L3"): 0.25, (3, "L3"): 0.20,
            (5, "L4"):  2.00, (4, "L4"): 0.25, (3, "L4"): 0.15,
        }

        # 20 paylines — identical pattern to Pragmatic Dog House reference
        self.paylines = {
            1:  [1, 1, 1, 1, 1],
            2:  [0, 0, 0, 0, 0],
            3:  [2, 2, 2, 2, 2],
            4:  [0, 1, 2, 1, 0],
            5:  [2, 1, 0, 1, 2],
            6:  [0, 0, 1, 2, 2],
            7:  [2, 2, 1, 0, 0],
            8:  [1, 0, 0, 0, 1],
            9:  [1, 2, 2, 2, 1],
            10: [1, 0, 1, 2, 1],
            11: [1, 2, 1, 0, 1],
            12: [0, 1, 0, 1, 0],
            13: [2, 1, 2, 1, 2],
            14: [0, 1, 1, 1, 0],
            15: [2, 1, 1, 1, 2],
            16: [1, 1, 0, 1, 1],
            17: [1, 1, 2, 1, 1],
            18: [0, 0, 2, 0, 0],
            19: [2, 2, 0, 2, 2],
            20: [0, 2, 1, 0, 2],
        }

        self.include_padding = True

        # W=wild substitute, S=scatter, DB=DogBooster (freegame special)
        self.special_symbols = {
            "wild":       ["W"],
            "scatter":    ["S"],
            "dogbooster": ["DB"],
        }

        # Minimum scatter counts to enter/retrigger freegame
        # Actual spin count randomised in game_executables (8-15 on trigger, +10 retrigger)
        self.freespin_triggers = {
            self.basegame_type: {3: 8},   # 3 scatters minimum for basegame trigger
            self.freegame_type: {3: 10},  # retrigger always +10
        }
        self.anticipation_triggers = {
            self.basegame_type: 2,
            self.freegame_type: 2,
        }

        # Freespin random grant range
        self.fs_spin_range = list(range(8, 16))   # 8..15 inclusive
        self.fs_retrigger_amount = 10

        # Reel strips
        reels_map = {"BR0": "BR0.csv", "FR0": "FR0.csv"}
        self.reels = {}
        for rid, fname in reels_map.items():
            self.reels[rid] = self.read_reels_csv(os.path.join(self.reels_path, fname))

        self.padding_reels[self.basegame_type] = self.reels["BR0"]
        self.padding_reels[self.freegame_type] = self.reels["FR0"]

        # ── Bet-mode condition blocks ──────────────────────────────────────────
        base_wincap = {
            "reel_weights": {
                self.basegame_type: {"BR0": 1},
                self.freegame_type: {"FR0": 1},
            },
            "scatter_triggers": {3: 1},
            "force_wincap": True,
            "force_freegame": True,
        }
        base_freegame = {
            "reel_weights": {
                self.basegame_type: {"BR0": 1},
                self.freegame_type: {"FR0": 1},
            },
            "scatter_triggers": {3: 1},
            "force_wincap": False,
            "force_freegame": True,
        }
        base_zero = {
            "reel_weights": {self.basegame_type: {"BR0": 1}},
            "force_wincap": False,
            "force_freegame": False,
        }
        base_basegame = {
            "reel_weights": {self.basegame_type: {"BR0": 1}},
            "force_wincap": False,
            "force_freegame": False,
        }
        bonus_wincap = {
            "reel_weights": {
                self.basegame_type: {"BR0": 1},
                self.freegame_type: {"FR0": 1},
            },
            "force_wincap": True,
            "force_freegame": True,
        }
        bonus_freegame = {
            "reel_weights": {
                self.basegame_type: {"BR0": 1},
                self.freegame_type: {"FR0": 1},
            },
            "force_wincap": False,
            "force_freegame": True,
        }

        self.bet_modes = [
            BetMode(
                name="base",
                cost=1.0,
                rtp=self.rtp,
                max_win=self.wincap,
                auto_close_disabled=False,
                is_feature=True,
                is_buybonus=False,
                distributions=[
                    Distribution("wincap",    quota=0.001, win_criteria=self.wincap, conditions=base_wincap),
                    Distribution("freegame",  quota=0.10,  conditions=base_freegame),
                    Distribution("0",         quota=0.40,  win_criteria=0.0, conditions=base_zero),
                    Distribution("basegame",  quota=0.499, conditions=base_basegame),
                ],
            ),
            BetMode(
                name="bonus",
                cost=100.0,
                rtp=self.rtp,
                max_win=self.wincap,
                auto_close_disabled=False,
                is_feature=False,
                is_buybonus=True,
                distributions=[
                    Distribution("wincap",   quota=0.001, win_criteria=self.wincap, conditions=bonus_wincap),
                    Distribution("freegame", quota=0.999, conditions=bonus_freegame),
                ],
            ),
        ]
