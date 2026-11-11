from typing import Optional
import numpy as np
import asyncio


class StreamState:
    def __init__(self):
        self.client_connected: bool = False
        self.game_active: bool = False
        self.latest_frame: Optional[np.ndarray] = None
        self.stream_mode: str = "raw"  # raw | processed
        self.lock = asyncio.Lock()


stream_state = StreamState()