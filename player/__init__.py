"""
PilotFS Player Module - Full Features
"""

from .enigma_player import (
    PilotFSPlayer,
    get_player_status,
    is_media_file,
    can_play_file,
    IS_ENIGMA2,
    ENIGMA_AVAILABLE,
    PLAYER_AVAILABLE
)

# Backward compatibility
MyLocalPlayer = PilotFSPlayer

__all__ = [
    'PilotFSPlayer',
    'MyLocalPlayer',
    'get_player_status',
    'is_media_file',
    'can_play_file',
    'IS_ENIGMA2',
    'ENIGMA_AVAILABLE',
    'PLAYER_AVAILABLE'
]
