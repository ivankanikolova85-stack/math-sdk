"""Dog House – state overrides: book reset, repeat checks, bonus-mode entry."""

from game_executables import GameExecutables
from src.calculations.statistics import get_random_outcome


class GameStateOverride(GameExecutables):

    def reset_book(self) -> None:
        """Reset per-simulation state including sticky wild tracking."""
        super().reset_book()
        # List of {"reel": int, "row": int, "mult": int} for persistent wilds
        self.sticky_wilds = []
        self.triggered_freegame = False
        self.dog_booster_triggered = False

    def assign_special_sym_function(self) -> None:
        """No special symbol construction logic needed at draw time."""
        self.special_symbol_functions = {}

    def check_repeat(self) -> None:
        """
        Ensure simulation satisfies its distribution criteria:
          - wincap sims must hit exactly the wincap.
          - freegame sims must have triggered a freegame.
          - zero-win sims must pay nothing.
          - basegame sims with non-None win_criteria must match exactly.
        """
        super().check_repeat()
        if self.repeat is False:
            cond = self.get_current_distribution_conditions()
            win_criteria = self.get_current_betmode_distributions().get_win_criteria()

            if cond["force_freegame"] and not self.triggered_freegame:
                self.repeat = True
                return

            if win_criteria is not None and self.final_win != win_criteria:
                self.repeat = True
                return

            if win_criteria is None and self.final_win == 0 and self.criteria not in ("0", "freegame", "wincap"):
                self.repeat = True
                return
