# audi0: Terminal Audio Visualizer

**audi0** is a highly customizable, cross-platform terminal-based audio visualizer written in Python. It listens to your system audio (or microphone) and draws beautiful, smooth ASCII waveforms directly in your command line.

## Features
- **Cross-Platform:** Works seamlessly on Windows (WASAPI System Loopback) and macOS/Linux (Microphone capture).
- **Interactive TUI Menu:** Easily adjust settings on the fly with `audi0 --menu`.
- **Advanced AGC (Auto Gain Control):** Automatically adjusts waveform sensitivity to match the volume of your media.
- **Custom Color Themes:** Configure bespoke hex-color gradients via `config.json`.
- **Plugin Architecture:** Write and load your own rendering logic using Python scripts.
- **High Performance:** Tear-free, optimized terminal drawing engine up to 144+ FPS.

## Installation

You can install `audi0` directly as a global command on any PC via pip:

```bash
git clone https://github.com/Negimazz/audi0.git
cd audi0
pip install .
```
*(Make sure you have Python 3.8+ installed)*

## Usage

Start the visualizer with your saved settings:
```bash
audi0
```

Open the interactive configuration menu:
```bash
audi0 --menu
```

### CLI Arguments
You can bypass the menu and directly launch with specific arguments:
```bash
audi0 --theme ocean --fps 120 --bars 100
audi0 --auto-sens --agc-speed 0.1
```
Use `audi0 --help` for a full list of commands.

## Customization & Configuration

All user settings are saved locally in `config.json`.

### Custom Color Themes
You can define your own dynamic gradients by adding CSS-style hex codes to `config.json`:
```json
"custom_themes": {
    "cyberpunk": ["#FF00FF", "#00FFFF", "#00FF00"],
    "sunset": ["#FF4500", "#FF8C00", "#FFD700"]
}
```
Load them via the menu or CLI (`audi0 --theme cyberpunk`).

### Plugins
Create your own `custom_renderer.py` in the `plugins/` folder containing a `render(...)` function. Load it via `audi0 --plugin custom_renderer`. Checkout `plugins/sample_plugin.py` for API reference!

## License
MIT License
