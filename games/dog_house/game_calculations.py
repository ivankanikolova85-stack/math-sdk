"""Dog House – custom board calculations."""

from src.executables.executables import Executables


class GameCalculations(Executables):
    """Extend base Executables with Dog House specific board logic."""

    # Reels on which Wild (W) is forbidden in basegame (0-indexed)
    WILD_FORBIDDEN_REELS = [0]
    # Reels on which Scatter (S) is allowed (0-indexed: reels 1, 3, 5 → 0, 2, 4)
    SCATTER_ALLOWED_REELS = [0, 2, 4]

    def sanitize_board_symbols(self) -> None:
        """
        Enforce symbol placement rules after a board is drawn:
          - Remove Wild (W) from reel 1 (index 0) in basegame.
          - Remove Scatter (S) from reels that are not 1/3/5 (indices 1/3).
          - Cap total scatters at 3 by removing extras from last reels.

        Invalid positions are replaced with a random low-pay symbol.
        """
        low_pays = ["L1", "L2", "L3", "L4"]
        import random

        for reel in range(self.config.num_reels):
            for row in range(self.config.num_rows[reel]):
                sym = self.board[reel][row]
                # Wild forbidden on reel 0
                if sym.name == "W" and reel in self.WILD_FORBIDDEN_REELS:
                    self.board[reel][row] = self.create_symbol(random.choice(low_pays))
                # Scatter only allowed on reels 0, 2, 4
                if sym.name == "S" and reel not in self.SCATTER_ALLOWED_REELS:
                    self.board[reel][row] = self.create_symbol(random.choice(low_pays))

        # Cap scatters at 3
        scatter_positions = []
        for reel in range(self.config.num_reels):
            for row in range(self.config.num_rows[reel]):
                if self.board[reel][row].name == "S":
                    scatter_positions.append((reel, row))

        while len(scatter_positions) > 3:
            reel, row = scatter_positions.pop()
            self.board[reel][row] = self.create_symbol(random.choice(low_pays))

        # Refresh special symbol tracking after modifications
        self.get_special_symbols_on_board()
