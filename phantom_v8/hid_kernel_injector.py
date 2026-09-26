import struct
import time
import math
from typing import List, Tuple
from .models import HardwareHIDPacket, HIDActionType


class HIDKernelInjector:
    """
    Synthesizes raw USB HID (Human Interface Device) descriptor packets.
    Bypasses DOM event dispatchers and Chrome DevTools Protocol (CDP) to prevent bot detection.
    """

    def __init__(self):
        self._packet_counter = 0

    def generate_mouse_hid_packet(
        self,
        x: int,
        y: int,
        button_mask: int = 0,
        delta_x: int = 0,
        delta_y: int = 0
    ) -> HardwareHIDPacket:
        """
        Packs a standard 5-byte USB HID mouse report:
        [buttons: 1 byte, rel_x: 2 bytes, rel_y: 2 bytes]
        """
        self._packet_counter += 1
        # Pack standard USB HID mouse report (simulated)
        raw_report = struct.pack("<Bhh", button_mask & 0x07, delta_x, delta_y)

        return HardwareHIDPacket(
            packet_id=self._packet_counter,
            action_type=HIDActionType.MOUSE_MOVE if button_mask == 0 else HIDActionType.MOUSE_DOWN,
            x=x,
            y=y,
            button_mask=button_mask,
            delta_x=delta_x,
            delta_y=delta_y,
            hardware_report_bytes=raw_report
        )

    def generate_natural_trajectory(
        self,
        start: Tuple[int, int],
        end: Tuple[int, int],
        steps: int = 12
    ) -> List[HardwareHIDPacket]:
        """
        Generates realistic physiological micro-motion curve with physiological tremor.
        """
        packets: List[HardwareHIDPacket] = []
        curr_x, curr_y = start

        for i in range(1, steps + 1):
            t = i / steps
            # Smooth acceleration and deceleration (sigmoid curve)
            s_curve = (1.0 - math.cos(t * math.pi)) / 2.0
            target_x = int(start[0] + (end[0] - start[0]) * s_curve)
            target_y = int(start[1] + (end[1] - start[1]) * s_curve)

            # Micro-tremor oscillation
            tremor_x = int(math.sin(i * 1.5) * 1.2)
            tremor_y = int(math.cos(i * 1.5) * 1.2)

            next_x = target_x + tremor_x
            next_y = target_y + tremor_y

            dx = next_x - curr_x
            dy = next_y - curr_y

            packet = self.generate_mouse_hid_packet(
                x=next_x,
                y=next_y,
                button_mask=0,
                delta_x=dx,
                delta_y=dy
            )
            packets.append(packet)
            curr_x, curr_y = next_x, next_y

        return packets

    def generate_keyboard_hid_packet(self, key_code: int, is_down: bool) -> HardwareHIDPacket:
        """Packs standard USB HID keyboard report."""
        self._packet_counter += 1
        # [modifier: 1 byte, reserved: 1 byte, keycode: 1 byte]
        report = struct.pack("<BBB", 0, 0, key_code if is_down else 0)

        return HardwareHIDPacket(
            packet_id=self._packet_counter,
            action_type=HIDActionType.KEY_DOWN if is_down else HIDActionType.KEY_UP,
            x=0,
            y=0,
            key_code=key_code,
            hardware_report_bytes=report
        )
