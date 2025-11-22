WINDOW_WIDTH = 960
WINDOW_HEIGHT = 980
FPS = 60

BOARD_SIZE = 700
TILE_SIZE = 70
BOARD_X = 130
BOARD_Y = 90

COLOR_BG_TOP = (109, 91, 212)
COLOR_BG_BOTTOM = (105, 193, 231)
COLOR_CARD = (245, 245, 245)
COLOR_TILE_ORANGE = (242, 92, 43)
COLOR_TILE_WHITE = (255, 255, 255)
COLOR_GRID = (17, 17, 17)
COLOR_SNAKE = (57, 163, 74)
COLOR_SNAKE_DARK = (43, 127, 58)
COLOR_LADDER_RAIL = (138, 107, 82)
COLOR_LADDER_RUNG = (179, 148, 119)
COLOR_BUTTON_TEXT = (255, 255, 255)
COLOR_BUTTON_ROLL = (59, 130, 246)
COLOR_BUTTON_PAUSE = (255, 207, 51)
COLOR_BUTTON_RESUME = (109, 211, 255)
COLOR_BUTTON_SAVE = (52, 199, 89)
COLOR_BUTTON_RESTART = (240, 147, 251)
COLOR_BUTTON_MENU = (153, 153, 153)
COLOR_STATUS_BG1 = (255, 239, 199)
COLOR_STATUS_BG2 = (252, 182, 159)
COLOR_TEXT = (51, 51, 51)
COLOR_ACCENT = (102, 126, 234) # For highlighting selected options

FONT_REGULAR = "assets/fonts/Nunito-Regular.ttf"
FONT_BOLD = "assets/fonts/Nunito-Bold.ttf"

PLAYER_COLORS = [
    (66, 135, 245), # Blue
    (255, 165, 0),  # Orange
    (16, 185, 129), # Green
    (244, 114, 182) # Pink
]

SNAKES = {
    16: 6, 47: 26, 49: 11, 56: 53, 62: 19, 64: 60, 87: 24, 93: 73, 95: 75, 98: 78
}

LADDERS = {
    1: 38, 4: 14, 9: 31, 21: 42, 28: 84, 36: 44, 51: 67, 71: 91, 80: 100
}

SPECIAL_TILES = {
    "powerUps": { 8:{"type":"forward5"}, 27:{"type":"forward5"}, 63:{"type":"forward5"} },
    "powerDowns": { 17:{"type":"backward6"}, 54:{"type":"backward6"}, 99:{"type":"backward6"} }
}

POWER_UP_TEXTS = {
    'forward5': 'Five Steps Forward'
}

POWER_DOWN_TEXTS = {
    'backward6': 'Six Steps Backward'
}

TIMED_MODE_DURATION = 120 # seconds (2 minutes)

ASSET_MANIFEST = {
    "images": {
        "dice_1": "assets/images/dice_1.png",
        "dice_2": "assets/images/dice_2.png",
        "dice_3": "assets/images/dice_3.png",
        "dice_4": "assets/images/dice_4.png",
        "dice_5": "assets/images/dice_5.png",
        "dice_6": "assets/images/dice_6.png",
        "dice_custom": "assets/images/dice_custom.png",
        "token": "assets/images/token.png",
        "avatar": "assets/images/avatar.png",
        "zombie_head": "assets/images/zombie_head.png",
        "board_bg": "assets/images/snakeboard.png",
        "player1": "assets/images/player1.png", # Dummy player images
        "player2": "assets/images/player2.png",
        "player3": "assets/images/player3.png",
        "player4": "assets/images/player4.png",
    },
    "sounds": {
        "roll": "assets/sounds/roll.wav",
        "land": "assets/sounds/land.wav",
        "step": "assets/sounds/step.wav",
        "ladder": "assets/sounds/ladder.wav",
        "snake": "assets/sounds/snake.wav",
        "zombie": "assets/sounds/zombie.wav",
        "win": "assets/sounds/win.wav",
    }
}
