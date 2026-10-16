import serial
import pygame
import time
import random
import re
from collections import deque

# Initialize audio & UI
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
pygame.init()
pygame.font.init()

# Setup window
WIDTH, HEIGHT = 600, 400
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Air Piano - Real Notes")
font = pygame.font.SysFont("Segoe UI", 36, bold=True)
small_font = pygame.font.SysFont("Segoe UI", 24)
tiny_font = pygame.font.SysFont("Segoe UI", 18)

# Serial port
ser = serial.Serial('COM8', 9600, timeout=1)

# Note to filename mapping
note_file_map = {
    "C": "c1.wav", "C#": "c1s.wav", "D": "d1.wav", "D#": "d1s.wav",
    "E": "e1.wav", "F": "f1.wav", "F#": "f1s.wav", "G": "g1.wav",
    "G#": "g1s.wav", "A": "a1.wav", "A#": "a1s.wav", "B": "b1.wav"
}

# Load WAV sounds
note_sounds = {}
for note, filename in note_file_map.items():
    try:
        note_sounds[note] = pygame.mixer.Sound(
    f"C:/Users/HP/vsprojects/arduino projects/airpiano maksad/airpiano/wav-piano-sound-master/wav-piano-sound-master/wav/{filename}"
)
        note_sounds[note].set_volume(0.8)
    except Exception as e:
        print(f"Could not load {filename}: {e}")

# Notes layout
white_keys = ["C", "D", "E", "F", "G", "A", "B"]
black_keys = ["C#", "D#", None, "F#", "G#", "A#", None]

# Notes layout
white_keys = ["C", "D", "E", "F", "G", "A", "B"]
black_keys = ["C#", "D#", None, "F#", "G#", "A#", None]

note_queue = deque()  # Queue for notes to be played
current_note = ""
current_distance = 0
currently_playing_note = ""
note_play_time = 0
note_duration = 0.3  # seconds
note_start_time = 0
last_detected_note = ""
last_note_time = 0

button_rect = pygame.Rect(WIDTH - 120, 20, 100, 40)

# Background gradient config
bg_gradient = [(15, 15, 30), (25, 20, 40), (20, 25, 35), (10, 10, 25)]
fade_duration = 6
color_index = 0
last_time = time.time()

# Flash effect
flash_color = (0, 0, 0)
flash_intensity = 0

def lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

def draw_rounded_rect(surface, rect, color, radius=8, border=0, border_color=(0, 0, 0), glow=False):
    shape_surf = pygame.Surface(rect.size, pygame.SRCALPHA)

    if glow:
        glow_color = (color[0], color[1], min(255, color[2] + 100))
        glow_surf = pygame.Surface((rect.width + 12, rect.height + 12), pygame.SRCALPHA)
        pygame.draw.ellipse(glow_surf, (*glow_color, 100), glow_surf.get_rect())
        surface.blit(glow_surf, (rect.x - 6, rect.y - 6))

    pygame.draw.rect(shape_surf, color, shape_surf.get_rect(), border_radius=radius)
    if border > 0:
        pygame.draw.rect(shape_surf, border_color, shape_surf.get_rect(), border, border_radius=radius)
    surface.blit(shape_surf, rect.topleft)

def draw_distance_bar(surface, distance, x, y, width, height):
    # Bar background
    bar_bg_rect = pygame.Rect(x, y, width, height)
    draw_rounded_rect(surface, bar_bg_rect, (30, 30, 50), radius=12, border=2, border_color=(60, 60, 80))
    
    # Calculate fill percentage (5-50cm range)
    if distance >= 5 and distance <= 50:
        fill_percent = (distance - 5) / 45  # 0 to 1
        # Color gradient from red (close) to blue (far)
        red_intensity = int(255 * (1 - fill_percent))
        blue_intensity = int(255 * fill_percent)
        bar_color = (red_intensity, 50, blue_intensity)
        glow = True
    else:
        fill_percent = 0
        bar_color = (60, 60, 60)
        glow = False
    
    # Fill bar
    if fill_percent > 0:
        fill_width = int((width - 8) * fill_percent)
        fill_rect = pygame.Rect(x + 4, y + 4, fill_width, height - 8)
        draw_rounded_rect(surface, fill_rect, bar_color, radius=8, glow=glow)
    
    # Distance text
    distance_text = tiny_font.render(f"{distance} cm", True, (255, 255, 255))
    text_rect = distance_text.get_rect(center=(x + width // 2, y + height + 15))
    surface.blit(distance_text, text_rect)
    
    # Range indicators
    range_text = tiny_font.render("5cm", True, (150, 150, 150))
    surface.blit(range_text, (x - 5, y + height + 30))
    range_text = tiny_font.render("50cm", True, (150, 150, 150))
    surface.blit(range_text, (x + width - 25, y + height + 30))

def random_color():
    return tuple(random.randint(0, 255) for _ in range(3))

def parse_serial_data(line):
    # Parse "Distance: X cm - Note: Y" format
    match = re.match(r"Distance:\s*(\d+)\s*cm\s*-\s*Note:\s*(\w+|none)", line)
    if match:
        distance = int(match.group(1))
        note = match.group(2) if match.group(2) != "none" else ""
        return distance, note
    return None, None

# Main loop
running = True
print("Piano Ready!")

try:
    while running:
        now = time.time()
        elapsed = now - last_time
        t = (elapsed % fade_duration) / fade_duration
        c1 = bg_gradient[color_index % len(bg_gradient)]
        c2 = bg_gradient[(color_index + 1) % len(bg_gradient)]
        bg_color = lerp_color(c1, c2, t)

        if elapsed > fade_duration:
            color_index += 1
            last_time = now

        # Serial read
        line = ser.readline().decode(errors='ignore').strip()
        if line:
            distance, note = parse_serial_data(line)
            if distance is not None:
                current_distance = distance
                
                # Queue note if it's different from the last detected note (debounce)
                if note and note in note_sounds and note != last_detected_note:
                    note_queue.append(note)
                    last_detected_note = note
                elif not note:
                    last_detected_note = ""
        
        # Check if current note finished playing and play next one
        time_elapsed = time.time() - note_play_time
        if time_elapsed > note_duration and note_queue:
            # Previous note finished, play next one
            next_note = note_queue.popleft()
            currently_playing_note = next_note
            note_play_time = time.time()
            note_sounds[next_note].play()
            flash_color = random_color()
            flash_intensity = 1.0

        # Apply flash effect
        if flash_intensity > 0:
            mix = min(flash_intensity, 1)
            bg_color = tuple(
                int(bg_color[i] * (1 - mix) + flash_color[i] * mix)
                for i in range(3)
            )
            flash_intensity -= 0.05

        window.fill(bg_color)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            if e.type == pygame.MOUSEBUTTONDOWN and button_rect.collidepoint(e.pos):
                running = False

        # Draw distance bar
        bar_width = 300
        bar_height = 20
        bar_x = (WIDTH - bar_width) // 2
        bar_y = 30
        draw_distance_bar(window, current_distance, bar_x, bar_y, bar_width, bar_height)

        # Draw note label
        if currently_playing_note:
            note_surface = font.render(f"🎵 {currently_playing_note}", True, (255, 255, 255))
            note_rect = note_surface.get_rect(center=(WIDTH // 2, 120))
            window.blit(note_surface, note_rect)

        # Draw white keys
        key_width = WIDTH // 7
        white_rects = []
        for i, note in enumerate(white_keys):
            is_pressed = (currently_playing_note == note and time.time() - note_play_time < note_duration)
            y_offset = 5 if is_pressed else 0
            rect = pygame.Rect(i * key_width + 5, HEIGHT - 140 + y_offset, key_width - 10, 130 - y_offset)
            color = (255, 255, 255) if not is_pressed else (180, 200, 255)
            draw_rounded_rect(window, rect, color, radius=8, border=2, border_color=(220, 220, 220), glow=is_pressed)
            white_rects.append(rect)

        # Draw black keys
        black_width = key_width // 2
        black_height = 90
        for i, note in enumerate(black_keys):
            if note:
                is_pressed = (currently_playing_note == note and time.time() - note_play_time < note_duration)
                y_offset = 4 if is_pressed else 0
                x = i * key_width + key_width - black_width // 2
                rect = pygame.Rect(x, HEIGHT - 140 + y_offset, black_width, black_height - y_offset)
                color = (40, 40, 40) if not is_pressed else (60, 120, 255)
                draw_rounded_rect(window, rect, color, radius=6, glow=is_pressed)

        # Draw Quit button
        draw_rounded_rect(window, button_rect, (255, 105, 97), radius=10)
        quit_text = small_font.render("QUIT", True, (255, 255, 255))
        window.blit(quit_text, quit_text.get_rect(center=button_rect.center))

        pygame.display.flip()
        time.sleep(0.05)

except KeyboardInterrupt:
    print("Piano Closed")

finally:
    ser.close()
    pygame.quit()
