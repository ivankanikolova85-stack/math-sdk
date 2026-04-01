"""Dog House – main game state: base spin and freespin loops."""

from game_override import GameStateOverride
from src.events.events import reveal_event, fs_trigger_event


class GameState(GameStateOverride):
    """Handle all game-logic and event updates for each simulation round."""

    def run_spin(self, sim, simulation_seed=None):
        self.reset_seed(sim)
        self.repeat = True

        while self.repeat:
            self.reset_book()

            if self.betmode == "bonus":
                self._run_bonus()
            else:
                self._run_base()

            self.evaluate_finalwin()
            self.check_repeat()

        self.imprint_wins()

    # ── Base mode ──────────────────────────────────────────────────────────────

    def _run_base(self):
        """Standard base-game spin: reveal → evaluate → maybe trigger freegame."""
        self.draw_board(emit_event=False)
        self.sanitize_board_symbols()
        reveal_event(self)

        self.evaluate_lines_board()
        self.win_manager.update_gametype_wins(self.gametype)

        if self.check_fs_condition() and self.check_freespin_entry():
            self.triggered_freegame = True
            self.run_freespin_from_base()

    # ── Bonus buy mode ─────────────────────────────────────────────────────────

    def _run_bonus(self):
        """Bonus buy: skip base reveal, go straight to freegame."""
        self.triggered_freegame = True
        # Switch to freegame context
        self.reset_fs_spin()
        # Initialise special_syms_on_board so fs_trigger_event can access it
        self.refresh_special_syms()
        # Grant random 8-15 spins
        self.tot_fs = self.get_random_fs_amount()
        fs_trigger_event(self, basegame_trigger=True, freegame_trigger=False)
        self.run_freespin()

    # ── Freegame loop ──────────────────────────────────────────────────────────

    def run_freespin(self):
        """
        Freegame with sticky wilds + DogBooster mechanic.
          1. Draw new freegame board.
          2. Sanitize placement rules.
          3. Re-apply existing sticky wilds onto board.
          4. Check DogBooster — +2 to every sticky wild multiplier.
          5. Collect newly landed wilds → lock as sticky.
          6. Evaluate paylines.
          7. Retrigger check (3 scatters → +10 spins).
          8. Wincap check.
        """
        if self.gametype != self.config.freegame_type:
            self.reset_fs_spin()

        while self.fs < self.tot_fs and not self.wincap_triggered:
            self.update_freespin()

            self.create_board_reelstrips()
            self.sanitize_board_symbols()

            # Re-impose sticky wilds
            self.apply_sticky_wilds_to_board()

            # DogBooster: +2 to all sticky wild multipliers
            if self.apply_dog_booster():
                self.dog_booster_triggered = True

            reveal_event(self)

            # Lock new wilds
            self.collect_new_sticky_wilds()

            # Paylines
            self.evaluate_lines_board()
            self.win_manager.update_gametype_wins(self.gametype)

            # Wincap
            if self.evaluate_wincap():
                break

            # Retrigger: 3 scatters → +10 spins
            if self.check_fs_condition():
                self.tot_fs += self.config.fs_retrigger_amount
                fs_trigger_event(self, basegame_trigger=False, freegame_trigger=True)

        self.end_freespin()
