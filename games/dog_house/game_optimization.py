"""Set conditions/parameters for optimization program"""

from optimization_program.optimization_config import (
    ConstructScaling,
    ConstructParameters,
    ConstructConditions,
    verify_optimization_input,
)


class OptimizationSetup:
    """Game specific optimization setup.
    RTP splits must sum to exactly 0.96 per mode.

    Base mode:  wincap=0.01 + freegame=0.37 + 0=0.00 + basegame=0.58 = 0.96
    Bonus mode: wincap=0.01 + freegame=0.95 = 0.96
    """

    def __init__(self, game_config: object):
        self.game_config = game_config
        self.game_config.opt_params = {
            "base": {
                "conditions": {
                    "wincap": ConstructConditions(
                        rtp=0.01, av_win=5000, search_conditions=5000
                    ).return_dict(),
                    "freegame": ConstructConditions(
                        rtp=0.37, hr=200, search_conditions={"symbol": "scatter"}
                    ).return_dict(),
                    "0": ConstructConditions(
                        rtp=0.00, av_win=0, search_conditions=0
                    ).return_dict(),
                    "basegame": ConstructConditions(
                        rtp=0.58, hr=3.5
                    ).return_dict(),
                },
                "scaling": ConstructScaling(
                    [
                        {
                            "criteria": "basegame",
                            "scale_factor": 1,
                            "win_range": (1, 1),
                            "probability": 1.0,
                        },
                        {
                            "criteria": "freegame",
                            "scale_factor": 1,
                            "win_range": (1, 1),
                            "probability": 1.0,
                        },
                    ]
                ).return_dict(),
                "parameters": ConstructParameters(
                    num_show=5000,
                    num_per_fence=10000,
                    min_m2m=4,
                    max_m2m=8,
                    pmb_rtp=1.0,
                    sim_trials=5000,
                    test_spins=[50, 100, 200],
                    test_weights=[0.3, 0.4, 0.3],
                    score_type="rtp",
                ).return_dict(),
            },
            "bonus": {
                "conditions": {
                    "wincap": ConstructConditions(
                        rtp=0.01, av_win=5000, search_conditions=5000
                    ).return_dict(),
                    "freegame": ConstructConditions(
                        rtp=0.95, hr=1
                    ).return_dict(),
                },
                "scaling": ConstructScaling(
                    [
                        {
                            "criteria": "freegame",
                            "scale_factor": 1,
                            "win_range": (1, 1),
                            "probability": 1.0,
                        },
                    ]
                ).return_dict(),
                "parameters": ConstructParameters(
                    num_show=5000,
                    num_per_fence=10000,
                    min_m2m=4,
                    max_m2m=8,
                    pmb_rtp=1.0,
                    sim_trials=5000,
                    test_spins=[50, 100, 200],
                    test_weights=[0.3, 0.4, 0.3],
                    score_type="rtp",
                ).return_dict(),
            },
        }

        verify_optimization_input(self.game_config, self.game_config.opt_params)
