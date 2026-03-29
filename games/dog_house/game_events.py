"""Dog House – custom event emitters for DogBooster and sticky wilds."""


def dog_booster_event(gamestate) -> None:
    """Emit event when DogBooster activates and boosts sticky wild multipliers."""
    event = {
        "type": "dogBooster",
        "stickyWilds": [
            {"reel": e["reel"], "row": e["row"], "mult": e["mult"]}
            for e in gamestate.sticky_wilds
        ],
    }
    gamestate.book.add_event(event)


def new_sticky_wild_event(gamestate, new_wilds: list) -> None:
    """Emit event for wild positions newly locked as sticky this spin."""
    event = {
        "type": "newStickyWilds",
        "wilds": new_wilds,
    }
    gamestate.book.add_event(event)


def sticky_wild_state_event(gamestate) -> None:
    """Emit the full current state of all sticky wilds."""
    event = {
        "type": "stickyWildState",
        "wilds": [
            {"reel": e["reel"], "row": e["row"], "mult": e["mult"]}
            for e in gamestate.sticky_wilds
        ],
    }
    gamestate.book.add_event(event)
