"""Local Reversi gym environment.

The course handout originally asked to copy this folder into
`site-packages/gym/envs/` and register the env there. For this workspace we
register it programmatically so `reversi_main.py` can run without modifying
installed packages.
"""

from __future__ import annotations

from gymnasium.envs.registration import register, registry

from .reversi import ReversiEnv


def register_env() -> None:
    """Register `Reversi8x8-v0` with the current gym install.

    Safe to call multiple times.
    """

    env_id = "Reversi8x8-v0"
    if env_id in registry:
        return

    register(
        id=env_id,
        entry_point=ReversiEnv,
        kwargs={
            "player_color": "black",
            "opponent": "random",
            "observation_type": "numpy3c",
            "illegal_place_mode": "lose",
            "board_size": 8,
        },
    )
