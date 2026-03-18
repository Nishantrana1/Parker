# Parker — Voice-Reactive Sphere Assistant

Parker is a Python-based intelligent voice-reactive assistant that listens to your microphone and visually responds to your speech in real-time. It features a beautiful, glowing, pulsatile UI built with Pygame and optionally sends serial commands to an external microcontroller (like an Arduino) to trigger physical movements.

## 🌟 Features

- **Real-Time Audio Analysis**: Uses `sounddevice` and `numpy` to capture and process live microphone input.
- **Voice Activity Detection**: Detects speech using Root-Mean-Square (RMS) audio energy calculation against a configurable threshold.
- **Dynamic Visuals**: A sleek, reactive UI powered by `pygame`. When idle, the sphere breathes calmly. When voice is detected, it turns bright cyan, expands, and radiates ripples.
- **Hardware Integration**: Can send movement commands (start/stop) over a serial port to control a physical robotic sphere or servo motors.
- **Modular Design**: Clean architecture separating audio processing, hardware control, and UI rendering.

## 📂 Project Structure

- `main.py` — The entry point of the application. Opens the continuous audio stream and runs the main Pygame event loop.
- `config.py` — Central configuration file containing all tunable parameters (audio thresholds, hardware serial ports, etc.).
- `audio_detector.py` — Pure mathematical logic for voice-activity detection (RMS volume calculation and threshold comparison).
- `movement_controller.py` — Handles simulated movement state and manages serial connections to external hardware via PySerial.
- `sphere_renderer.py` — Contains the `SphereRenderer` class that draws the glowing, animating sphere UI using Pygame.

## ⚙️ Configuration

All settings can be tweaked in `config.py`:
- **Audio Settings**:
  - `VOLUME_THRESHOLD`: Adjust this to calibrate microphone sensitivity. Increase it if background noise triggers Parker, decrease if it struggles to hear you.
  - `SAMPLE_RATE` / `BLOCK_SIZE`: Controls the audio processing fidelity and reaction speed.
- **Serial / Arduino Settings**:
  - `USE_SERIAL`: Set to `True` if you have an Arduino connected to sync hardware movement with voice activity.
  - `SERIAL_PORT`: The COM port (Windows e.g., `"COM3"`) or TTY device (Linux/macOS e.g., `"/dev/ttyUSB0"`).
  - `SERIAL_BAUD_RATE`: Baud rate for serial communication (default is `9600`).

## 🚀 Getting Started

### Prerequisites

Ensure you have Python 3 installed. Install the necessary dependencies (ideally in a virtual environment):

```bash
pip install -r requirements.txt
```

*(The primary dependencies are: `numpy`, `sounddevice`, `pygame`, and optionally `pyserial`).*

### Running Parker

To launch the assistant, simply run:

```bash
python main.py
```

- Speak into your default system microphone and watch the interface react immediately.
- Press **Escape** or close the Pygame window to gracefully shut down the application.

## 🛠️ Hardware Setup (Optional)

If `USE_SERIAL` is enabled in `config.py`, Parker will send single-byte commands when sound states change:
- `'1'` (`0x31` byte) — Voice detected (Start movement).
- `'0'` (`0x30` byte) — Silence detected (Stop movement).

Simply connect your microcontroller, listen on the mapped serial port at 9600 baud rate, and parse the incoming bytes to dictate your hardware's logic.



Virtual Environment
Activate the environment:

powershell
d:\Nisha\programing\project\Parker\venv\Scripts\Activate.ps1
Run the program:

bash
python main.py