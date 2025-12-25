import board
import analogio
import time

from kmk.kmk_keyboard import KMKKeyboard
from kmk.keys import KC
from kmk.modules.rapidkeys import RapidKeys

# Initialisierung des Keyboards
keyboard = KMKKeyboard()

# RapidKeys Modul für den Autoclicker
rapid_keys = RapidKeys()
keyboard.modules.append(rapid_keys)

# Potentiometer an GPIO4 (Pin D4 am XIAO)
# Er liest Werte von 0 (0V) bis 65535 (3.3V)
pot = analogio.AnalogIn(board.GP4)

# Pins für deine 7 Tasten (Direct Pin)
keyboard.direct_pins = [
    board.GP28,                         # Taste 1 (Oben)
    board.GP29, board.GP6, board.GP1,     # Taste 2, 3, 4 (Mitte)
    board.GP7,  board.GP0, board.GP2      # Taste 5, 6, 7 (Unten)
]

# Desktop-Wechsel Definitionen
DESKTOP_RECHTS = KC.LCTL(KC.LGUI(KC.RIGHT))
DESKTOP_LINKS = KC.LCTL(KC.LGUI(KC.LEFT))

# Der Autoclicker (Initialwert 50ms, wird gleich dynamisch überschrieben)
AUTOCLICK = KC.MS_BTN1.repeat(interval=50)
TASK_MANAGER = KC.LCTRL(KC.LSHIFT(KC.ESC))

keyboard.keymap = [
    [
        KC.MUTE,                          # Taste 1
        DESKTOP_LINKS, DESKTOP_RECHTS, TASK_MANAGER, # Taste 2, 3, 4
        KC.LCTRL(KC.C), KC.LCTRL(KC.V), AUTOCLICK # Taste 5, 6, 7
    ]
]

# Diese Funktion wird bei jedem Tastenscan ausgeführt
def update_poti_speed(keyboard):
    # Wir lesen den Poti-Wert (0 bis 65535)
    # Wir mappen das auf ein Intervall von 10ms (sehr schnell) bis 500ms (langsam)
    # Wenn das Poti ganz links ist: 10ms, ganz rechts: 510ms
    new_interval = int(10 + (pot.value / 65535) * 500)
    
    # Wir überschreiben das Intervall der Autoclicker-Taste (Taste 7)
    AUTOCLICK.interval = new_interval

# KMK anweisen, die Poti-Funktion ständig zu prüfen
keyboard.before_matrix_scan.append(update_poti_speed)

if __name__ == '__main__':
    keyboard.go()