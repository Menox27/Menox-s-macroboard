import board
import analogio
import time

from kmk.kmk_keyboard import KMKKeyboard
from kmk.keys import KC
from kmk.scanners import DiodeOrientation
from kmk.modules.encoder import EncoderHandler
from kmk.modules.layers import Layers
from kmk.modules.combos import Combos, Chord
from kmk.modules.rapidkeys import RapidKeys
from kmk.extensions.display import Display, SSD1306
from kmk.extensions.rgb import RGB

keyboard = KMKKeyboard()

# 1. Hardware Setup (3x3 Matrix)
keyboard.col_pins = (board.GP26, board.GP27, board.GP28)
keyboard.row_pins = (board.GP29, board.GP3, board.GP4)
keyboard.diode_orientation = DiodeOrientation.COL2ROW

# Variablen für OLED-Helligkeit
oled_contrast = 100 

# Poti für Autoclicker-Speed (an GP2)
pot = analogio.AnalogIn(board.GP2)

# RGB Setup
rgb = RGB(pixel_pin=board.GP0, num_pixels=9, val_default=50, hue_default=140)

# 2. Module & Extensions
layers_module = Layers()
encoder_handler = EncoderHandler()
combos_module = Combos()
rapid_keys = RapidKeys()
keyboard.modules = [layers_module, encoder_handler, combos_module, rapid_keys]

# 3. Spezial-Tasten & Custom Keys
DESKTOP_RECHTS = KC.LCTL(KC.LGUI(KC.RIGHT))
DESKTOP_LINKS = KC.LCTL(KC.LGUI(KC.LEFT))
AUTOCLICK = KC.MS_BTN1.repeat(interval=50)
TASK_MANAGER = KC.LCTRL(KC.LSHIFT(KC.ESC))
ALT_TAB = KC.LALT(KC.TAB)
ENTER = KC.ENT

# 4. OLED Display Logik
i2c_bus = board.I2C()
display_driver = SSD1306(i2c=i2c_bus, device_address=0x3C)

class MyDisplay(Display):
    def on_runtime_report(self, keyboard):
        global oled_contrast
        self.driver.fill(0)
        layer = keyboard.active_layers[0]
        
        # OLED Helligkeit anwenden
        self.driver.contrast(oled_contrast)
        
        if layer == 0:
            interval = AUTOCLICK.interval
            self.driver.text('MACRO MODE', 0, 0, 1)
            self.driver.text(f'Speed: {interval}ms', 0, 20, 1)
            rgb.set_hsv(140, 100, rgb.val) # Eisblau
        else:
            self.driver.text('SETTINGS', 0, 0, 1)
            self.driver.text(f'RGB-Bright: {int(rgb.val/255*100)}%', 0, 15, 1)
            self.driver.text(f'OLED-Contrast: {oled_contrast}', 0, 30, 1)
            rgb.set_hsv(0, 255, rgb.val) # Rot
        self.driver.show()

display_extension = MyDisplay(display_driver)
keyboard.extensions = [rgb, display_extension]

# 5. Custom Code für OLED Steuerung
def oled_br_up(keyboard, *args):
    global oled_contrast
    oled_contrast = min(oled_contrast + 25, 255)

def oled_br_down(keyboard, *args):
    global oled_contrast
    oled_contrast = max(oled_contrast - 25, 0)

KC_OLED_UP = KC.NO.clone()
KC_OLED_UP.on_press.append(oled_br_up)
KC_OLED_DOWN = KC.NO.clone()
KC_OLED_DOWN.on_press.append(oled_br_down)

# 6. Combos & Encoder
combos_module.combos = [Chord((ALT_TAB, ENTER), KC.TG(1))]

encoder_handler.pins = ((board.GP2, board.GP1, None, False),)
encoder_handler.map = [
    ((KC.VOLU, KC.VOLD),),        # Layer 0: System Volume
    ((KC.RGB_VAI, KC.RGB_VAD),),  # Layer 1: RGB Helligkeit
]

# 7. Die Keymap
keyboard.keymap = [
    [   # LAYER 0 (Macro Layer)
        KC.MUTE,       DESKTOP_LINKS,  DESKTOP_RECHTS, 
        KC.LCTRL(KC.C), KC.LCTRL(KC.V), TASK_MANAGER,   
        ALT_TAB,       AUTOCLICK,      ENTER           
    ],
    [   # LAYER 1 (Settings Layer)
        KC.TRNS,      KC.TRNS,        KC.TRNS,
        KC.TRNS,      KC.TRNS,        KC_OLED_UP,   # Taste 6: OLED Heller
        KC.TRNS,      KC.TRNS,        KC_OLED_DOWN  # Taste 9: OLED Dunkler
    ]
]

def update_poti_speed(keyboard):
    AUTOCLICK.interval = int(10 + (pot.value / 65535) * 500)

keyboard.before_matrix_scan.append(update_poti_speed)

if __name__ == '__main__':
    keyboard.go()