"""Dog House – game executables: sticky wilds, DogBooster, line evaluation."""

import random
from copy import deepcopy
from game_calculations import GameCalculations
from src.calculations.lines import Lines


class GameExecutables(GameCalculations):

    # ── Freespin spin grant helpers ────────────────────────────────────────────

    def get_random_fs_amount(self) -> int:
        """Return a random spin count in [8, 15] for a fresh trigger."""
        return random.choice(self.config.fs_spin_range)

    # ── Sticky wild management ─────────────────────────────────────────────────

    def apply_sticky_wilds_to_board(self) -> None:
        """Overwrite board positions that hold a persistent sticky wild."""
        for entry in self.sticky_wilds:
            reel, row, mult = entry["reel"], entry["row"], entry["mult"]
            sym = self.create_symbol("W")
            sym.assign_attribute({"multiplier": mult})
            self.board[reel][row] = sym

    def collect_new_sticky_wilds(self) -> list:
        """
        Scan the board for Wilds that are not already tracked as sticky.
        Return a list of newly locked positions and register them.
        """
        existing = {(e["reel"], e["row"]) for e in self.sticky_wilds}
        new_wilds = []
        for reel in range(self.config.num_reels):
            for row in range(self.config.num_rows[reel]):
                sym = self.board[reel][row]
                if sym.name == "W" and (reel, row) not in existing:
                    entry = {"reel": reel, "row": row, "mult": sym.multiplier if sym.multiplier else 1}
                    self.sticky_wilds.append(entry)
                    new_wilds.append(deepcopy(entry))
                    existing.add((reel, row))
        return new_wilds

    # ── DogBooster mechanic ────────────────────────────────────────────────────

    def apply_dog_booster(self) -> bool:
        """
        If a DogBooster symbol (DB) is present on the board, add +2 to the
        multiplier of every registered sticky wild.
        Returns True if DogBooster was applied.
        """
        db_positions = []
        for reel in range(self.config.num_reels):
            for row in range(self.config.num_rows[reel]):
                if self.board[reel][row].name == "DB":
                    db_positions.append({"reel": reel, "row": row})

        if not db_positions:
            return False

        for entry in self.sticky_wilds:
            entry["mult"] = min(entry["mult"] + 2, 5)  # cap at 5x

        # Reflect updated multipliers on the board immediately
        self.apply_sticky_wilds_to_board()
        return True

    # ── Lines evaluation wrapper ───────────────────────────────────────────────

    def evaluate_lines_board(self) -> None:
        """Evaluate paylines, record wins, emit events."""
        self.win_data = Lines.get_lines(
            self.board,
            self.config,
            global_multiplier=self.global_multiplier,
        )
        Lines.record_lines_wins(self)
        self.win_manager.update_spinwin(self.win_data["totalWin"])
        Lines.emit_linewin_events(self)

    # ── Freespin trigger override ──────────────────────────────────────────────

    def update_freespin_amount(self, scatter_key: str = "scatter") -> None:
        """
        Override: grant random 8-15 spins on first trigger;
        retrigger always adds +10.
        """
        from src.events.events import fs_trigger_event

        if self.gametype == self.config.basegame_type:
            # Initial trigger from base game
            self.tot_fs = self.get_random_fs_amount()
            fs_trigger_event(self, basegame_trigger=True, freegame_trigger=False)
        else:
            # Retrigger inside freegame
            self.tot_fs += self.config.fs_retrigger_amount
            fs_trigger_event(self, basegame_trigger=False, freegame_trigger=True)
