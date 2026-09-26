from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional
import time


class HIDActionType(str, Enum):
    MOUSE_MOVE = "mouse_move"
    MOUSE_DOWN = "mouse_down"
    MOUSE_UP = "mouse_up"
    KEY_DOWN = "key_down"
    KEY_UP = "key_up"
    WHEEL_SCROLL = "wheel_scroll"


@dataclass
class HardwareHIDPacket:
    packet_id: int
    action_type: HIDActionType
    x: int
    y: int
    button_mask: int = 0
    key_code: Optional[int] = None
    delta_x: int = 0
    delta_y: int = 0
    timestamp_ns: int = field(default_factory=time.time_ns)
    hardware_report_bytes: bytes = b""


@dataclass
class FingerprintProfile:
    user_agent: str
    webgl_vendor: str
    webgl_renderer: str
    hardware_concurrency: int
    device_memory_gb: int
    screen_resolution: tuple[int, int]
    canvas_noise_seed: int
    audio_noise_seed: float
    navigator_platform: str = "MacIntel"


@dataclass
class BotDetectionAudit:
    score: float  # 0.0 (bot) to 1.0 (clean human)
    cdp_leaks_detected: bool
    webdriver_flag_present: bool
    canvas_hash_natural: bool
    timing_entropy_passed: bool
    rejection_reasons: List[str] = field(default_factory=list)
