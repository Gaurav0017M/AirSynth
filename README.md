# AirSynth — Contactless Air Piano

AirSynth is a contactless musical instrument that lets you play piano notes by moving your hand through the air. An ultrasonic distance sensor connected to an Arduino tracks hand position and streams it to a Python application, which maps the distance to a musical note and plays the corresponding piano sound through a real-time animated interface.

## Features

- **Real piano sound** — plays authentic WAV piano samples instead of synthesized tones
- **Animated visual interface** — built with Pygame, including glowing keys and a live distance bar
- **Real-time response** — low-latency serial communication between Arduino and Python
- **Full chromatic scale** — supports all 12 notes (C, C#, D, D#, E, F, F#, G, G#, A, A#, B)
- **Optional LCD display** — shows live sensor readings on a 16x2 I2C LCD

## How It Works

1. The Arduino continuously measures distance using an HC-SR04 ultrasonic sensor.
2. The measured distance is sent over serial to the Python application.
3. The Python app maps the distance range to a musical note and plays the matching WAV file.
4. The on-screen piano interface lights up and animates in sync with the note being played.

## Hardware Requirements

- Arduino Uno (or compatible board)
- HC-SR04 ultrasonic sensor
- Jumper wires
- Breadboard (optional)
- USB cable for Arduino connection
- I2C 16x2 LCD (optional, for live distance display)

### Wiring

**HC-SR04 → Arduino Uno**

| HC-SR04 Pin | Arduino Pin |
|-------------|-------------|
| VCC         | 5V          |
| GND         | GND         |
| Trig        | Pin 10      |
| Echo        | Pin 9       |

**I2C 16x2 LCD → Arduino Uno** (optional)

| LCD Pin | Arduino Pin |
|---------|-------------|
| VCC     | 5V          |
| GND     | GND         |
| SDA     | A4          |
| SCL     | A5          |

## Software Requirements

- Python 3.7+
- Arduino IDE
- Python packages: `pygame`, `pyserial`
- Arduino library: `I2C_LiquidCrystal` (only required if using the LCD)

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/AirSynth.git
   cd AirSynth
   ```

2. **Install Python dependencies**
   ```bash
   pip install pygame pyserial
   ```

3. **Upload the Arduino sketch**
   - Open `airpiano.ino` in the Arduino IDE
   - Connect your Arduino board
   - Select the correct board and port
   - Upload the sketch

4. **Configure the serial port**

   Open `airpianomain.py` and update the serial port to match your system:
   ```python
   ser = serial.Serial('COM8', 9600, timeout=1)  # Change COM8 to your port
   ```

5. **Set the audio file path**

   Update the WAV file path in `airpianomain.py` to point to the local `wav/` folder included in this repository:
   ```python
   note_sounds[note] = pygame.mixer.Sound(f"wav/{filename}")
   ```

6. **Run the application**
   ```bash
   python airpianomain.py
   ```

## Usage

1. Power on the Arduino and run `airpianomain.py`.
2. Hold your hand roughly 5–50 cm above the ultrasonic sensor.
3. Move your hand closer or farther away to play different notes:
   - Closer to the sensor → higher pitched notes
   - Farther from the sensor → lower pitched notes
4. Watch the interface as piano keys light up in time with the notes being played.

## Project Structure

```
AirSynth/
├── airpiano.ino        # Arduino sketch for the ultrasonic sensor
├── airpianomain.py      # Python application (audio playback + UI)
├── wav/                 # Piano note sound samples
│   ├── c1.wav
│   ├── c1s.wav
│   ├── d1.wav
│   ├── d1s.wav
│   ├── e1.wav
│   ├── f1.wav
│   ├── f1s.wav
│   ├── g1.wav
│   ├── g1s.wav
│   ├── a1.wav
│   ├── a1s.wav
│   ├── b1.wav
│   └── c2.wav
└── README.md
```

## Contributing

Contributions are welcome. Feel free to open an issue or submit a pull request for bug fixes, improvements, or new features.
