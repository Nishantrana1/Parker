"""
movement_controller.py — Sphere movement control (simulated + optional serial).

Exposes:
    • start_movement()
    • stop_movement()

When config.USE_SERIAL is True the module also sends single-byte commands
('1' = move, '0' = stop) over the configured serial port.
"""

import config

# ── Optional serial connection ────────────────────────────────────────
_serial_connection = None

if config.USE_SERIAL:
    try:
        import serial
        _serial_connection = serial.Serial(
            port=config.SERIAL_PORT,
            baudrate=config.SERIAL_BAUD_RATE,
            timeout=1,
        )
        print(f"✅ Serial connected on {config.SERIAL_PORT} "
              f"@ {config.SERIAL_BAUD_RATE} baud")
    except Exception as exc:
        print(f"⚠️  Could not open serial port {config.SERIAL_PORT}: {exc}")
        _serial_connection = None


# ── Movement state (avoids spamming the same message) ────────────────
_is_moving = False


def start_movement() -> None:
    """Begin sphere movement (called when voice is detected)."""
    global _is_moving
    if _is_moving:
        return                          # already moving — nothing to do

    _is_moving = True
    print("🔊 Voice detected!  Moving sphere...")

    if _serial_connection and _serial_connection.is_open:
        _serial_connection.write(b"1")  # tell Arduino to start servo


def stop_movement() -> None:
    """Stop sphere movement (called when silence is detected)."""
    global _is_moving
    if not _is_moving:
        return                          # already stopped — nothing to do

    _is_moving = False
    print("🔇 Silence.  Stopping sphere.")

    if _serial_connection and _serial_connection.is_open:
        _serial_connection.write(b"0")  # tell Arduino to stop servo
