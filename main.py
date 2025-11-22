import pygame
import sys
import random
import os
import json
import math
import time
from enum import Enum

# Import tkinter for the file dialog
import tkinter as tk
from tkinter import filedialog, messagebox

# --- Constants ---
# Screen dimensions
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
SIDEBAR_WIDTH = 250
BOARD_AREA_WIDTH = SCREEN_WIDTH - SIDEBAR_WIDTH

# Board settings
BOARD_SIZE = 10
SQUARE_SIZE = 60
BOARD_WIDTH = BOARD_SIZE * SQUARE_SIZE
BOARD_HEIGHT = BOARD_SIZE * SQUARE_SIZE
BOARD_X_POS = (BOARD_AREA_WIDTH - BOARD_WIDTH) // 2
BOARD_Y_POS = (SCREEN_HEIGHT - BOARD_HEIGHT) // 2

# Player Token Size
PLAYER_TOKEN_SIZE = 50

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_GREY = (40, 40, 40)
LIGHT_GREY = (200, 200, 200)
BROWN = (139, 69, 19)
LIGHT_BLUE = (173, 216, 230)
GREEN = (0, 180, 0)
LADDER_COLOR = (0, 150, 0)
SNAKE_COLOR = (150, 0, 0)
DICE_BG_COLOR = (250, 250, 250)
BUTTON_COLOR = (100, 100, 200)
BUTTON_HOVER_COLOR = (130, 130, 230)
BUTTON_DISABLED_COLOR = (180, 180, 180)
PURPLE = (102, 51, 153)
DARK_PURPLE = (61, 31, 92)
GOLD = (255, 215, 0)
RED = (200, 0, 0)

# Game States
class GameState(Enum):
    MENU = 'MENU'
    PLAYER_COUNT_SELECT = 'PLAYER_COUNT_SELECT'  # New state for selecting number of players
    PLAYER_SETUP = 'PLAYER_SETUP'
    PLAYING = 'PLAYING'
    GAME_OVER = 'GAME_OVER'
    TUTORIAL = 'TUTORIAL'
    SETTINGS = 'SETTINGS'

# Game Modes
class GameMode(Enum):
    CLASSIC = 'Classic'
    TIMED = 'Timed'
    CHAMPIONSHIP = 'Championship'
    POWER_UP = 'Power-Up'

# --- Game Data ---
SNAKES = {16: 6, 47: 26, 49: 11, 56: 53, 62: 19, 64: 60, 87: 24, 93: 73, 95: 75, 98: 78}
LADDERS = {1: 38, 4: 14, 9: 31, 21: 42, 28: 84, 26: 44, 51: 26, 71: 91, 80: 100}

# Power-ups for Power-Up mode
POWER_UPS = {
    5: "Extra Roll",
    15: "Shield",
    25: "Swap Position",
    35: "Skip Turn",
    45: "Double Move",
    55: "Teleport",
    65: "Reverse Direction",
    75: "Immunity",
    85: "Steal Roll",
    95: "Final Sprint"
}

# --- Pygame Setup ---
pygame.init()
pygame.mixer.init()  # Initialize sound mixer
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Snake and Ladder - Enhanced Edition")
clock = pygame.time.Clock()

# Initialize Tkinter root window (hidden) for file dialogs
try:
    tk_root = tk.Tk()
    tk_root.withdraw()  # Hide the main tkinter window
except tk.TclError:
    print("Warning: Could not initialize Tkinter. File dialogs may not work.")
    tk_root = None

# Load fonts
try:
    # Try to load custom fonts
    title_font = pygame.font.Font("assets/text/BrownieStencil.ttf", 64)
    subtitle_font = pygame.font.Font("assets/fonts/BebasNeue-Regular.ttf", 36)
    font = pygame.font.Font("assets/font/BrownieStencil-808MJ.ttf", 28)
    sidebar_font = pygame.font.Font("assets/fonts/Roboto-Regular.ttf", 24)
except:
    # Fall back to default fonts if custom fonts aren't available
    title_font = pygame.font.Font(None, 64)
    subtitle_font = pygame.font.Font(None, 36)
    font = pygame.font.Font(None, 28)
    sidebar_font = pygame.font.Font(None, 24)

# Load sounds
try:
    roll_sound = pygame.mixer.Sound("assets/sounds/dice_roll.wav")
    move_sound = pygame.mixer.Sound("assets/sounds/move.wav")
    snake_sound = pygame.mixer.Sound("assets/sounds/snake.wav")
    ladder_sound = pygame.mixer.Sound("assets/sounds/ladder.wav")
    win_sound = pygame.mixer.Sound("assets/sounds/win.wav")
    button_click = pygame.mixer.Sound("assets/sounds/button_click.wav")
except:
    print("Warning: Could not load sound files. Sound will be disabled.")
    roll_sound = None
    move_sound = None
    snake_sound = None
    ladder_sound = None
    win_sound = None
    button_click = None

# Load background images
try:
    menu_bg = pygame.image.load("assets/images/menu_bg.jpg").convert()
    board_bg = pygame.image.load("assets/images/board_bg.jpg").convert()
except:
    print("Warning: Could not load background images. Using solid colors.")
    menu_bg = None
    board_bg = None

# --- Helper Classes ---
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, disabled_color=None, font_size=28):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.disabled_color = disabled_color or BUTTON_DISABLED_COLOR
        self.is_hovered = False
        self.is_enabled = True
        self.font = pygame.font.Font(None, font_size)
        self.click_cooldown = 0

    def draw(self, surface):
        # Update click cooldown
        if self.click_cooldown > 0:
            self.click_cooldown -= 1
            
        color = self.disabled_color if not self.is_enabled else (self.hover_color if self.is_hovered else self.color)
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=8)
        
        text_color = WHITE if self.is_enabled else (150, 150, 150)
        text_surf = self.font.render(self.text, True, text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos) and self.is_enabled
        if event.type == pygame.MOUSEBUTTONDOWN and self.is_enabled and self.click_cooldown == 0:
            if self.rect.collidepoint(event.pos):
                self.click_cooldown = 10  # Prevent multiple clicks in quick succession
                return True
        return False

class TextBox:
    def __init__(self, x, y, width, height, label_text, default_text=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = default_text
        self.label_text = label_text
        self.active = False
        self.cursor_visible = True
        self.cursor_timer = 0

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                self.active = False
            else:
                self.text += event.unicode

    def update(self):
        self.cursor_timer += 1
        if self.cursor_timer >= 40:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0

    def draw(self, surface):
        label_surf = font.render(self.label_text, True, WHITE)
        surface.blit(label_surf, (self.rect.x, self.rect.y - 30))
        color = LIGHT_GREY if self.active else WHITE
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=5)
        text_surface = font.render(self.text, True, BLACK)
        surface.blit(text_surface, (self.rect.x + 10, self.rect.y + 10))
        if self.active and self.cursor_visible:
            cursor_x = self.rect.x + 10 + text_surface.get_width()
            pygame.draw.line(surface, BLACK, (cursor_x, self.rect.y + 10), (cursor_x, self.rect.y + self.rect.height - 10), 2)

class PlayerImageLoader:
    def __init__(self, x, y, size, label_text):
        self.rect = pygame.Rect(x, y, size, size)
        self.label_text = label_text
        self.image_surface = None
        self.browse_button = Button(x, y + size + 10, size, 40, "Browse...", BUTTON_COLOR, BUTTON_HOVER_COLOR)

    def handle_event(self, event):
        if self.browse_button.handle_event(event):
            if not tk_root:
                print("Tkinter is not available. Cannot open file dialog.")
                return False
            
            # Open the file dialog
            file_path = filedialog.askopenfilename(
                parent=tk_root,
                title=f"Select an image for {self.label_text}",
                filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.gif"), ("All Files", "*.*")]
            )
            
            if file_path:
                try:
                    # Use convert_alpha() for images with transparency
                    loaded_image = pygame.image.load(file_path).convert_alpha()
                    self.image_surface = loaded_image
                    return True  # Signal that an image was loaded
                except pygame.error as e:
                    print(f"Error loading image: {e}")
            return False
        return False

    def draw(self, surface):
        # Draw image or placeholder
        if self.image_surface:
            scaled_image = pygame.transform.scale(self.image_surface, (self.rect.width, self.rect.height))
            surface.blit(scaled_image, self.rect)
        else:
            pygame.draw.rect(surface, LIGHT_GREY, self.rect, border_radius=5)
            pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=5)
            placeholder_text = font.render("No Image", True, DARK_GREY)
            text_rect = placeholder_text.get_rect(center=self.rect.center)
            surface.blit(placeholder_text, text_rect)
        
        # Draw browse button
        self.browse_button.draw(surface)

    def is_image_loaded(self):
        return self.image_surface is not None

# NOTE: The MenuPlayerSlot class is no longer used but kept for potential future use.
class MenuPlayerSlot:
    def __init__(self, x, y, size, player_num):
        self.rect = pygame.Rect(x, y, size, size)
        self.player_num = player_num
        self.active = False
        self.image_surface = None
        self.player_name = f"Player {player_num}"
        self.create_default_avatar()

    def create_default_avatar(self):
        # Create a default avatar with a unique color for each player
        colors = [(255, 100, 100), (100, 100, 255), (100, 255, 100), (255, 255, 100)]
        self.image_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.circle(self.image_surface, colors[self.player_num-1], 
                          (self.rect.width//2, self.rect.height//2), self.rect.width//2)
        pygame.draw.circle(self.image_surface, BLACK, 
                          (self.rect.width//2, self.rect.height//2), self.rect.width//2, 2)
    
    def update_player_data(self, name, avatar):
        """Update the player data with name and avatar"""
        self.player_name = name
        if avatar:
            self.image_surface = avatar

    def draw(self, surface):
        # Draw the player image
        if self.image_surface:
            surface.blit(self.image_surface, self.rect)
        
        # Draw the player label
        label = font.render(self.player_name, True, WHITE)
        label_rect = label.get_rect(center=(self.rect.centerx, self.rect.bottom + 20))
        surface.blit(label, label_rect)

class ToggleButton:
    def __init__(self, x, y, width, height, text, initial_state=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.is_on = initial_state

    def draw(self, surface):
        # Draw the button background
        color = GREEN if self.is_on else BUTTON_COLOR
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=5)
        
        # Draw the text
        text_surf = font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.is_on = not self.is_on
                return True
        return False

class Dropdown:
    def __init__(self, x, y, width, height, options, default_text="Select..."):
        self.rect = pygame.Rect(x, y, width, height)
        self.options = options
        self.default_text = default_text
        self.selected_option = None
        self.is_expanded = False
        self.option_rects = [pygame.Rect(x, y + (i + 1) * height, width, height) for i in range(len(options))]

    def draw(self, surface):
        pygame.draw.rect(surface, WHITE, self.rect, border_radius=5)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=5)
        text_to_display = self.selected_option if self.selected_option else self.default_text
        text_surf = font.render(text_to_display, True, BLACK)
        text_rect = text_surf.get_rect(midleft=(self.rect.x + 10, self.rect.centery))
        surface.blit(text_surf, text_rect)
        arrow_points = [(self.rect.right - 20, self.rect.centery - 5), (self.rect.right - 10, self.rect.centery + 5), (self.rect.right - 30, self.rect.centery + 5)]
        pygame.draw.polygon(surface, BLACK, arrow_points)
        if self.is_expanded:
            for i, option_rect in enumerate(self.option_rects):
                pygame.draw.rect(surface, WHITE, option_rect, border_radius=5)
                pygame.draw.rect(surface, BLACK, option_rect, 1, border_radius=5)
                option_text = font.render(self.options[i], True, BLACK)
                option_text_rect = option_text.get_rect(midleft=(option_rect.x + 10, option_rect.centery))
                surface.blit(option_text, option_text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_expanded:
                for i, option_rect in enumerate(self.option_rects):
                    if option_rect.collidepoint(event.pos):
                        self.selected_option = self.options[i]
                        self.is_expanded = False
                        return True
                if not self.rect.collidepoint(event.pos):
                    self.is_expanded = False
            else:
                if self.rect.collidepoint(event.pos):
                    self.is_expanded = True
        return False

class Player:
    def __init__(self, name, avatar_surface, pos=0):
        self.name = name
        self.avatar_surface = avatar_surface
        self.pos = pos
        self.power_ups = []
        self.shield = False
        self.extra_rolls = 0
        self.skip_next_turn = False
        self.wins = 0
        self.games_played = 0
        
    def add_power_up(self, power_up):
        self.power_ups.append(power_up)
        
    def use_power_up(self, power_up_index):
        if 0 <= power_up_index < len(self.power_ups):
            return self.power_ups.pop(power_up_index)
        return None

class Dice:
    def __init__(self, x, y, size, sounds_enabled):
        self.rect = pygame.Rect(x, y, size, size)
        self.value = 0
        self.rolling = False
        self.roll_animation_timer = 0
        self.roll_animation_duration = 60  # frames
        self.sounds_enabled = sounds_enabled # Store sounds_enabled state
        self.dot_positions = {
            1: [(size//2, size//2)],
            2: [(size//4, size//4), (3*size//4, 3*size//4)],
            3: [(size//4, size//4), (size//2, size//2), (3*size//4, 3*size//4)],
            4: [(size//4, size//4), (3*size//4, size//4), (size//4, 3*size//4), (3*size//4, 3*size//4)],
            5: [(size//4, size//4), (3*size//4, size//4), (size//2, size//2), (size//4, 3*size//4), (3*size//4, 3*size//4)],
            6: [(size//4, size//4), (3*size//4, size//4), (size//4, size//2), (3*size//4, size//2), (size//4, 3*size//4), (3*size//4, 3*size//4)]
        }
    
    def roll(self):
        if not self.rolling:
            self.rolling = True
            self.roll_animation_timer = 0
            if roll_sound and self.sounds_enabled: # Use self.sounds_enabled
                roll_sound.play()
            return True
        return False
    
    def update(self):
        if self.rolling:
            self.roll_animation_timer += 1
            # Show random values during animation
            self.value = random.randint(1, 6)
            
            if self.roll_animation_timer >= self.roll_animation_duration:
                self.rolling = False
                # Set the final value
                self.value = random.randint(1, 6)
                return True  # Signal that the roll is complete
        return False
    
    def draw(self, surface):
        # Draw dice background
        pygame.draw.rect(surface, DICE_BG_COLOR, self.rect, border_radius=10)
        pygame.draw.rect(surface, BLACK, self.rect, 3, border_radius=10)
        
        if self.value > 0 and self.value in self.dot_positions:
            for pos in self.dot_positions[self.value]:
                pygame.draw.circle(surface, BLACK, 
                                 (self.rect.x + pos[0], self.rect.y + pos[1]), 
                                 self.rect.width // 10)

class Animation:
    def __init__(self, start_pos, end_pos, duration, surface=None, color=None):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.current_pos = list(start_pos)
        self.duration = duration
        self.timer = 0
        self.surface = surface
        self.color = color
        self.complete = False
        
    def update(self):
        self.timer += 1
        if self.timer >= self.duration:
            self.current_pos = list(self.end_pos)
            self.complete = True
        else:
            progress = self.timer / self.duration
            # Use easing function for smoother animation
            eased_progress = self.ease_in_out_quad(progress)
            self.current_pos[0] = self.start_pos[0] + (self.end_pos[0] - self.start_pos[0]) * eased_progress
            self.current_pos[1] = self.start_pos[1] + (self.end_pos[1] - self.start_pos[1]) * eased_progress
        return self.complete
    
    def draw(self, surface):
        if self.surface:
            surface.blit(self.surface, self.current_pos)
        elif self.color:
            pygame.draw.circle(surface, self.color, 
                             (int(self.current_pos[0]), int(self.current_pos[1])), 
                             PLAYER_TOKEN_SIZE // 2)
    
    def ease_in_out_quad(self, t):
        return t * t * (3.0 - 2.0 * t)

class Particle:
    def __init__(self, x, y, color, velocity, lifetime):
        self.x = x
        self.y = y
        self.color = color
        self.vx, self.vy = velocity
        self.lifetime = lifetime
        self.age = 0
        self.size = random.randint(2, 5)
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1  # Gravity
        self.age += 1
        return self.age >= self.lifetime
    
    def draw(self, surface):
        alpha = max(0, 255 * (1 - self.age / self.lifetime))
        size = max(1, self.size * (1 - self.age / self.lifetime))
        # Note: pygame.draw.circle does not support alpha in the color tuple directly.
        # A more advanced implementation would use a surface with per-pixel alpha.
        pygame.draw.circle(surface, self.color[:3], 
                         (int(self.x), int(self.y)), int(size))

class ParticleSystem:
    def __init__(self):
        self.particles = []
        
    def emit(self, x, y, color, count=20):
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1, 3)
            velocity = (math.cos(angle) * speed, math.sin(angle) * speed - 2)
            lifetime = random.randint(20, 40)
            self.particles.append(Particle(x, y, color, velocity, lifetime))
    
    def update(self):
        self.particles = [p for p in self.particles if not p.update()]
    
    def draw(self, surface):
        for particle in self.particles:
            particle.draw(surface)

# Helper function to get board coordinates
def get_board_coords(square_num):
    if not 1 <= square_num <= 100: 
        return None
    row = (square_num - 1) // BOARD_SIZE
    col = (square_num - 1) % BOARD_SIZE
    x = BOARD_X_POS + (col if row % 2 == 0 else BOARD_SIZE - 1 - col) * SQUARE_SIZE
    y = BOARD_Y_POS + (BOARD_SIZE - 1 - row) * SQUARE_SIZE
    return (x, y)

class Game:
    def __init__(self):
        self.state = GameState.MENU
        self.mode = GameMode.CLASSIC
        self.num_players = 0
        self.selected_num_players = 2 # Store the selected number of players
        self.players = []
        self.current_player_index = 0
        self.winner_index = -1
        self.message = ""
        self.sounds_enabled = True
        self.animations = []
        self.particle_system = ParticleSystem()
        self.dice = None
        self.timed_mode_timer = 0  # For timed mode
        self.championship_rounds = 0  # For championship mode
        self.championship_current_round = 0
        self.championship_scores = []  # Track scores for championship mode
        self.show_power_up_notification = False
        self.power_up_notification_text = ""
        self.power_up_notification_timer = 0
        
        # Create UI elements
        self.create_ui_elements()
        
        # Create default avatars
        self.create_default_avatars()
        
    def create_default_avatars(self):
        self.default_avatars = []
        colors = [(255, 100, 100), (100, 100, 255), (100, 255, 100), (255, 255, 100)]
        for color in colors:
            avatar = pygame.Surface((64, 64), pygame.SRCALPHA)
            pygame.draw.circle(avatar, color, (32, 32), 30)
            pygame.draw.circle(avatar, BLACK, (32, 32), 30, 2)
            self.default_avatars.append(avatar)
    
    def create_ui_elements(self):
        menu_center_x = SCREEN_WIDTH // 2
        
        # Menu elements
        self.menu_title = title_font.render("Snakes & Ladders", True, WHITE)
        self.menu_subtitle = subtitle_font.render("Enhanced Edition", True, WHITE)
        
        # Create menu buttons
        self.menu_sounds_button = ToggleButton(menu_center_x - 250, 180, 120, 40, "Sounds", self.sounds_enabled)
        mode_options = [mode.value for mode in GameMode]
        self.menu_mode_dropdown = Dropdown(menu_center_x - 70, 180, 140, 40, mode_options, self.mode.value)
        self.menu_mode_dropdown.selected_option = self.mode.value
        self.menu_load_button = Button(menu_center_x + 110, 180, 120, 40, "Load Game", BUTTON_COLOR, BUTTON_HOVER_COLOR)
        
        # Player slots have been removed, so buttons are moved up.
        self.menu_start_button = Button(menu_center_x - 150, 260, 300, 50, "Start Game", GREEN, BUTTON_COLOR,)
        self.menu_quick_start_button = Button(menu_center_x - 150, 320, 300, 50, "Quick Start", BUTTON_COLOR, BUTTON_HOVER_COLOR)
        self.menu_tutorial_button = Button(menu_center_x - 150, 380, 300, 60, "How to Play", BUTTON_COLOR, BUTTON_HOVER_COLOR, (0, 220, 0))
        self.menu_settings_button = Button(menu_center_x - 150, 460, 300, 60, "Settings", BUTTON_COLOR, BUTTON_HOVER_COLOR)
        
        # --- New UI Elements for Player Count Selection ---
        self.player_count_title = title_font.render("Select Number of Players", True, WHITE)
        self.player_count_back_button = Button(menu_center_x - 100, 450, 200, 50, "Back", BUTTON_COLOR, BUTTON_HOVER_COLOR)
        self.player_count_two_button = Button(menu_center_x - 250, 250, 150, 60, "2 Players", BUTTON_COLOR, BUTTON_HOVER_COLOR)
        self.player_count_three_button = Button(menu_center_x - 75, 250, 150, 60, "3 Players", BUTTON_COLOR, BUTTON_HOVER_COLOR)
        self.player_count_four_button = Button(menu_center_x + 100, 250, 150, 60, "4 Players", BUTTON_COLOR, BUTTON_HOVER_COLOR)

        # Player setup elements
        self.setup_title = title_font.render("Enter Player Details", True, WHITE)
        self.setup_back_button = Button(menu_center_x - 100, 550, 200, 50, "Back", BUTTON_COLOR, BUTTON_HOVER_COLOR)
        self.setup_start_button = Button(menu_center_x - 100, 620, 200, 50, "Start Game", GREEN, (0, 220, 0))
        self.setup_start_button.is_enabled = False
        self.setup_elements = []
        
        # Game elements
        sidebar_center_x = BOARD_AREA_WIDTH + SIDEBAR_WIDTH // 2
        self.game_roll_button = Button(sidebar_center_x - 90, 400, 180, 60, "Roll Dice", BUTTON_COLOR, BUTTON_HOVER_COLOR)
        self.game_menu_button = Button(sidebar_center_x - 90, 600, 180, 60, "Main Menu", BUTTON_COLOR, BUTTON_HOVER_COLOR)
        self.game_save_button = Button(sidebar_center_x - 90, 520, 180, 60, "Save Game", BUTTON_COLOR, BUTTON_HOVER_COLOR)
        self.game_power_up_button = Button(sidebar_center_x - 90, 470, 180, 40, "Use Power-Up", BUTTON_COLOR, BUTTON_HOVER_COLOR)
        self.game_power_up_button.is_enabled = False
        
        # Game over elements
        self.game_over_title = title_font.render("Game Over", True, BLACK)
        self.game_over_menu_button = Button(menu_center_x - 100, 450, 200, 50, "Main Menu", BUTTON_COLOR, BUTTON_HOVER_COLOR)
        self.game_over_play_again_button = Button(menu_center_x - 100, 380, 200, 50, "Play Again", GREEN, (0, 220, 0))
        
        # Tutorial elements
        self.tutorial_title = title_font.render("How to Play", True, WHITE)
        self.tutorial_back_button = Button(menu_center_x - 100, 600, 200, 50, "Back", BUTTON_COLOR, BUTTON_HOVER_COLOR)
        self.tutorial_pages = [
            "Welcome to Snakes & Ladders Enhanced!\n\nThe goal is to be the first player to reach square 100.",
            "Roll the dice to move your token forward.\n\nIf you land on a ladder, you climb up to the top of the ladder.",
            "If you land on a snake, you slide down to the tail of the snake.\n\nBe careful!",
            "In Power-Up mode, special squares give you abilities.\n\nUse them wisely to gain an advantage!",
            "In Timed mode, each player has a limited time to make their move.\n\nThink quickly!",
            "In Championship mode, play multiple rounds.\n\nThe player with the most wins is the champion!"
        ]
        self.tutorial_current_page = 0
        self.tutorial_prev_button = Button(menu_center_x - 200, 500, 150, 50, "Previous", BUTTON_COLOR, BUTTON_HOVER_COLOR)
        self.tutorial_next_button = Button(menu_center_x + 50, 500, 150, 50, "Next", BUTTON_COLOR, BUTTON_HOVER_COLOR)
        
        # Settings elements
        self.settings_title = title_font.render("Settings", True, WHITE)
        self.settings_back_button = Button(menu_center_x - 100, 550, 200, 50, "Back", BUTTON_COLOR, BUTTON_HOVER_COLOR)
        self.settings_sounds_toggle = ToggleButton(menu_center_x - 100, 200, 200, 50, "Sound Effects", self.sounds_enabled)
        self.settings_difficulty_dropdown = Dropdown(menu_center_x - 100, 280, 200, 50, ["Easy", "Normal", "Hard"], "Normal")
        self.settings_difficulty_dropdown.selected_option = "Normal"
        self.settings_theme_dropdown = Dropdown(menu_center_x - 100, 360, 200, 50, ["Classic", "Modern", "Neon"], "Classic")
        self.settings_theme_dropdown.selected_option = "Classic"
    
    def create_player_setup_elements(self, num):
        self.setup_elements = []
        setup_center_x = SCREEN_WIDTH // 2
        start_y = 180
        for i in range(num):
            y_pos = start_y + i * 120
            textbox = TextBox(setup_center_x - 250, y_pos, 200, 40, f"Player {i+1} Name:")
            image_loader = PlayerImageLoader(setup_center_x + 60, y_pos - 50, 90, f"Player {i+1}")
            self.setup_elements.append((textbox, image_loader))
    
    def setup_game(self, player_data):
        self.num_players = len(player_data)
        self.players = [Player(data['name'], data['avatar']) for data in player_data]
        self.current_player_index = 0
        self.winner_index = -1
        self.message = f"{self.players[self.current_player_index].name}'s turn"
        
        # Initialize dice
        sidebar_center_x = BOARD_AREA_WIDTH + SIDEBAR_WIDTH // 2
        self.dice = Dice(sidebar_center_x - 90, 200, 180, self.sounds_enabled) # Pass sounds_enabled
        
        # Reset game mode specific variables
        if self.mode == GameMode.TIMED:
            self.timed_mode_timer = 30  # 30 seconds per turn
        elif self.mode == GameMode.CHAMPIONSHIP:
            self.championship_current_round = 1
            self.championship_rounds = 3
            self.championship_scores = [0] * self.num_players
        
        # Start the game
        self.state = GameState.PLAYING
    
    def save_game(self):
        """Save the current game state to a file"""
        # Create a directory for saves if it doesn't exist
        if not os.path.exists("saves"):
            os.makedirs("saves")
        
        # Prepare game data for saving
        save_data = {
            'mode': self.mode.value,
            'num_players': self.num_players,
            'players': [],
            'current_player_index': self.current_player_index,
            'winner_index': self.winner_index,
            'sounds_enabled': self.sounds_enabled
        }
        
        # Add mode-specific data
        if self.mode == GameMode.TIMED:
            save_data['timed_mode_timer'] = self.timed_mode_timer
        elif self.mode == GameMode.CHAMPIONSHIP:
            save_data['championship_current_round'] = self.championship_current_round
            save_data['championship_rounds'] = self.championship_rounds
            save_data['championship_scores'] = self.championship_scores
        
        # Save player data (excluding avatar surfaces which can't be pickled)
        for i, player in enumerate(self.players):
            player_data = {
                'pos': player.pos,
                'name': player.name,
                'power_ups': player.power_ups,
                'shield': player.shield,
                'extra_rolls': player.extra_rolls,
                'skip_next_turn': player.skip_next_turn,
                'wins': player.wins,
                'games_played': player.games_played
            }
            save_data['players'].append(player_data)
            
            # Save player avatars as separate files
            avatar_path = f"saves/avatar_{player.name}.png"
            pygame.image.save(player.avatar_surface, avatar_path)
            player_data['avatar_path'] = avatar_path
        
        # Get a filename from the user
        if tk_root:
            file_path = filedialog.asksaveasfilename(
                parent=tk_root,
                title="Save Game",
                defaultextension=".json",
                filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
                initialdir="saves"
            )
            
            if file_path:
                with open(file_path, 'w') as f:
                    json.dump(save_data, f)
                return True
        return False
    
    def load_game(self):
        """Load a game state from a file"""
        if not tk_root:
            return False
        
        file_path = filedialog.askopenfilename(
            parent=tk_root,
            title="Load Game",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
            initialdir="saves"
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    save_data = json.load(f)
                
                # Restore game state
                self.mode = GameMode(save_data['mode'])
                self.num_players = save_data['num_players']
                self.current_player_index = save_data['current_player_index']
                self.winner_index = save_data['winner_index']
                self.sounds_enabled = save_data.get('sounds_enabled', True)
                
                # Restore mode-specific data
                if self.mode == GameMode.TIMED:
                    self.timed_mode_timer = save_data.get('timed_mode_timer', 30)
                elif self.mode == GameMode.CHAMPIONSHIP:
                    self.championship_current_round = save_data.get('championship_current_round', 1)
                    self.championship_rounds = save_data.get('championship_rounds', 3)
                    self.championship_scores = save_data.get('championship_scores', [0] * self.num_players)
                
                # Restore player data
                self.players = []
                for player_data in save_data['players']:
                    # Load player avatar
                    avatar_path = player_data.get('avatar_path')
                    if avatar_path and os.path.exists(avatar_path):
                        avatar = pygame.image.load(avatar_path).convert_alpha()
                    else:
                        # Create a default avatar if the file doesn't exist
                        avatar = self.default_avatars[len(self.players) % len(self.default_avatars)]
                    
                    player = Player(
                        player_data['name'],
                        avatar,
                        player_data['pos']
                    )
                    player.power_ups = player_data.get('power_ups', [])
                    player.shield = player_data.get('shield', False)
                    player.extra_rolls = player_data.get('extra_rolls', 0)
                    player.skip_next_turn = player_data.get('skip_next_turn', False)
                    player.wins = player_data.get('wins', 0)
                    player.games_played = player_data.get('games_played', 0)
                    
                    self.players.append(player)
                
                # Initialize dice
                sidebar_center_x = BOARD_AREA_WIDTH + SIDEBAR_WIDTH // 2
                self.dice = Dice(sidebar_center_x - 90, 200, 180, self.sounds_enabled) # Pass sounds_enabled
                
                # Update UI elements
                self.menu_mode_dropdown.selected_option = self.mode.value
                self.menu_sounds_button.is_on = self.sounds_enabled
                
                # Start the game
                self.state = GameState.PLAYING
                
                return True
            except Exception as e:
                print(f"Error loading game: {e}")
                if tk_root:
                    messagebox.showerror("Load Error", f"Failed to load game: {e}")
                return False
        return False
    
    def handle_roll(self):
        """Handle dice roll and player movement"""
        if self.dice and not self.dice.rolling:
            current_player = self.players[self.current_player_index]
            
            # Check if player should skip turn
            if current_player.skip_next_turn:
                current_player.skip_next_turn = False
                self.message = f"{current_player.name} skips this turn!"
                self.next_turn()
                return
            
            # Roll the dice
            if self.dice.roll():
                # Determine the final position after the roll animation completes
                # This will be handled in the update method
                pass
    
    def next_turn(self):
        """Move to the next player's turn"""
        self.current_player_index = (self.current_player_index + 1) % self.num_players
        self.message = f"{self.players[self.current_player_index].name}'s turn"
        
        # Reset timer for timed mode
        if self.mode == GameMode.TIMED:
            self.timed_mode_timer = 30  # 30 seconds per turn
        
        # Update power-up button state
        self.game_power_up_button.is_enabled = len(self.players[self.current_player_index].power_ups) > 0
    
    def move_player(self, player_index, steps):
        """Move a player by the specified number of steps"""
        player = self.players[player_index]
        old_pos = player.pos
        new_pos = min(player.pos + steps, 100)
        
        # Create animation for player movement
        if old_pos > 0:
            start_coords = get_board_coords(old_pos)
            end_coords = get_board_coords(new_pos)
            
            if start_coords and end_coords:
                # Calculate offset for player token
                offset_x = (player_index % 2) * 20 - 10
                offset_y = (player_index // 2) * 20 - 10
                
                start_pos = (start_coords[0] + SQUARE_SIZE // 2 + offset_x, 
                            start_coords[1] + SQUARE_SIZE // 2 + offset_y)
                end_pos = (end_coords[0] + SQUARE_SIZE // 2 + offset_x, 
                          end_coords[1] + SQUARE_SIZE // 2 + offset_y)
                
                # Create animation
                avatar = pygame.transform.scale(player.avatar_surface, (PLAYER_TOKEN_SIZE, PLAYER_TOKEN_SIZE))
                self.animations.append(Animation(start_pos, end_pos, 30, avatar))
                
                # Play move sound
                if move_sound and self.sounds_enabled:
                    move_sound.play()
        
        # Update player position
        player.pos = new_pos
        
        # Check for snakes and ladders
        if player.pos in SNAKES:
            # Create particle effect at snake head
            head_coords = get_board_coords(player.pos)
            if head_coords:
                self.particle_system.emit(
                    head_coords[0] + SQUARE_SIZE // 2,
                    head_coords[1] + SQUARE_SIZE // 2,
                    SNAKE_COLOR,
                    30
                )
            
            # Apply snake effect if player doesn't have shield
            if not player.shield:
                player.pos = SNAKES[player.pos]
                self.message += " Oh no, a snake!"
                
                # Play snake sound
                if snake_sound and self.sounds_enabled:
                    snake_sound.play()
            else:
                self.message += " Shield protected you from a snake!"
                player.shield = False
        
        elif player.pos in LADDERS:
            # Create particle effect at ladder bottom
            bottom_coords = get_board_coords(player.pos)
            if bottom_coords:
                self.particle_system.emit(
                    bottom_coords[0] + SQUARE_SIZE // 2,
                    bottom_coords[1] + SQUARE_SIZE // 2,
                    LADDER_COLOR,
                    30
                )
            
            player.pos = LADDERS[player.pos]
            self.message += " Yay, a ladder!"
            
            # Play ladder sound
            if ladder_sound and self.sounds_enabled:
                ladder_sound.play()
        
        # Check for power-ups in Power-Up mode
        if self.mode == GameMode.POWER_UP and player.pos in POWER_UPS:
            power_up = POWER_UPS[player.pos]
            player.add_power_up(power_up)
            self.show_power_up_notification = True
            self.power_up_notification_text = f"{player.name} got a {power_up}!"
            self.power_up_notification_timer = 120  # Show for 2 seconds at 60 FPS
            
            # Create particle effect for power-up
            pos_coords = get_board_coords(player.pos)
            if pos_coords:
                self.particle_system.emit(
                    pos_coords[0] + SQUARE_SIZE // 2,
                    pos_coords[1] + SQUARE_SIZE // 2,
                    GOLD,
                    40
                )
        
        # Check for winner
        if player.pos == 100:
            self.winner_index = player_index
            player.wins += 1
            player.games_played += 1
            
            # Update other players' games played
            for p in self.players:
                if p != player:
                    p.games_played += 1
            
            # Handle different game modes
            if self.mode == GameMode.CHAMPIONSHIP:
                # Update championship scores
                self.championship_scores[player_index] += 1
                
                # Check if championship is complete
                if self.championship_current_round >= self.championship_rounds:
                    # Find the overall winner
                    max_score = max(self.championship_scores)
                    winners = [i for i, score in enumerate(self.championship_scores) if score == max_score]
                    
                    if len(winners) == 1:
                        self.winner_index = winners[0]
                    else:
                        # Tie - choose randomly
                        self.winner_index = random.choice(winners)
                    
                    self.state = GameState.GAME_OVER
                else:
                    # Start next round
                    self.championship_current_round += 1
                    self.reset_round()
            else:
                self.state = GameState.GAME_OVER
            
            # Play win sound
            if win_sound and self.sounds_enabled:
                win_sound.play()
                
            # Create celebration particles
            winner_coords = get_board_coords(100)
            if winner_coords:
                for _ in range(5):
                    self.particle_system.emit(
                        winner_coords[0] + SQUARE_SIZE // 2,
                        winner_coords[1] + SQUARE_SIZE // 2,
                        (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255)),
                        50
                    )
        else:
            # Continue to next turn if player has no extra rolls
            if player.extra_rolls > 0:
                player.extra_rolls -= 1
                self.message = f"{player.name} gets an extra roll!"
            else:
                self.next_turn()
    
    def reset_round(self):
        """Reset the board for a new round in championship mode"""
        for player in self.players:
            player.pos = 0
            player.power_ups = []
            player.shield = False
            player.extra_rolls = 0
            player.skip_next_turn = False
        
        self.current_player_index = 0
        self.winner_index = -1
        self.message = f"Round {self.championship_current_round}: {self.players[self.current_player_index].name}'s turn"
    
    def use_power_up(self, power_up_index):
        """Use a power-up for the current player"""
        current_player = self.players[self.current_player_index]
        power_up = current_player.use_power_up(power_up_index)
        
        if not power_up:
            return False
        
        # Apply power-up effect
        if power_up == "Extra Roll":
            current_player.extra_rolls += 1
            self.message = f"{current_player.name} gets an extra roll!"
        elif power_up == "Shield":
            current_player.shield = True
            self.message = f"{current_player.name} is protected from the next snake!"
        elif power_up == "Swap Position":
            # Choose a random player to swap with
            other_players = [i for i in range(len(self.players)) if i != self.current_player_index]
            if other_players:
                target_index = random.choice(other_players)
                target_player = self.players[target_index]
                
                # Swap positions
                current_player.pos, target_player.pos = target_player.pos, current_player.pos
                self.message = f"{current_player.name} swapped positions with {target_player.name}!"
                
                # Create animations for both players
                for i, player in enumerate([current_player, target_player]):
                    if player.pos > 0:
                        coords = get_board_coords(player.pos)
                        if coords:
                            offset_x = (i % 2) * 20 - 10
                            offset_y = (i // 2) * 20 - 10
                            center_x = coords[0] + SQUARE_SIZE // 2 + offset_x
                            center_y = coords[1] + SQUARE_SIZE // 2 + offset_y
                            
                            # Create particle effect
                            self.particle_system.emit(center_x, center_y, PURPLE, 30)
        elif power_up == "Skip Turn":
            # Choose a random player to skip
            other_players = [i for i in range(len(self.players)) if i != self.current_player_index]
            if other_players:
                target_index = random.choice(other_players)
                target_player = self.players[target_index]
                target_player.skip_next_turn = True
                self.message = f"{target_player.name} will skip their next turn!"
        elif power_up == "Double Move":
            # This will be applied after the next roll
            self.message = f"{current_player.name}'s next move will be doubled!"
            # We'll handle this in the move_player function
            current_player.double_next_move = True
        elif power_up == "Teleport":
            # Teleport to a random position ahead
            current_pos = current_player.pos
            max_pos = min(current_pos + 20, 100)
            new_pos = random.randint(current_pos + 1, max_pos)
            self.move_player(self.current_player_index, new_pos - current_pos)
            self.message = f"{current_player.name} teleported to square {new_pos}!"
        elif power_up == "Reverse Direction":
            # Reverse the direction of the next player
            next_player_index = (self.current_player_index + 1) % self.num_players
            next_player = self.players[next_player_index]
            next_player.reverse_direction = True
            self.message = f"{next_player.name} will move backward on their next turn!"
        elif power_up == "Immunity":
            # Immunity from all negative effects for 3 turns
            current_player.immunity_turns = 3
            self.message = f"{current_player.name} is immune for 3 turns!"
        elif power_up == "Steal Roll":
            # Steal the next player's roll
            next_player_index = (self.current_player_index + 1) % self.num_players
            next_player = self.players[next_player_index]
            next_player.steal_next_roll = True
            self.message = f"{current_player.name} will steal {next_player.name}'s next roll!"
        elif power_up == "Final Sprint":
            # Move forward 10 squares
            self.move_player(self.current_player_index, 10)
            self.message = f"{current_player.name} sprints forward 10 squares!"
        
        return True
    
    def update(self):
        """Update game state"""
        # Update animations
        completed_animations = []
        for animation in self.animations:
            if animation.update():
                completed_animations.append(animation)
        
        for animation in completed_animations:
            self.animations.remove(animation)
        
        # Update particle system
        self.particle_system.update()
        
        # Update dice
        if self.dice and self.dice.rolling:
            if self.dice.update():
                # Dice roll is complete
                current_player = self.players[self.current_player_index]
                dice_value = self.dice.value
                self.message = f"{current_player.name} rolled a {dice_value}!"
                
                # Apply double move power-up if active
                if hasattr(current_player, 'double_next_move') and current_player.double_next_move:
                    dice_value *= 2
                    self.message += " Double move applied!"
                    current_player.double_next_move = False
                
                # Apply reverse direction power-up if active
                if hasattr(current_player, 'reverse_direction') and current_player.reverse_direction:
                    dice_value = -dice_value
                    self.message += " Moving backward!"
                    current_player.reverse_direction = False
                
                # Move player
                if dice_value > 0:
                    new_pos = current_player.pos + dice_value
                    if new_pos > 100:
                        self.message += " Can't go over 100."
                    else:
                        self.move_player(self.current_player_index, dice_value)
                elif dice_value < 0:
                    # Moving backward
                    new_pos = max(current_player.pos + dice_value, 1)
                    self.move_player(self.current_player_index, dice_value)
        
        # Update power-up notification timer
        if self.show_power_up_notification:
            self.power_up_notification_timer -= 1
            if self.power_up_notification_timer <= 0:
                self.show_power_up_notification = False
        
        # Update timed mode timer
        if self.state == GameState.PLAYING and self.mode == GameMode.TIMED:
            self.timed_mode_timer -= 1/60  # Decrease by frame time (assuming 60 FPS)
            if self.timed_mode_timer <= 0:
                # Time's up, move to next player
                self.message = f"Time's up! {self.players[self.current_player_index].name} loses their turn."
                self.next_turn()
    
    def handle_event(self, event):
        """Handle pygame events"""
        if event.type == pygame.QUIT:
            return False
        
        if self.state == GameState.MENU:
            # Handle menu buttons
            if self.menu_sounds_button.handle_event(event):
                self.sounds_enabled = self.menu_sounds_button.is_on
                if button_click and self.sounds_enabled:
                    button_click.play()
            
            if self.menu_mode_dropdown.handle_event(event):
                self.mode = GameMode(self.menu_mode_dropdown.selected_option)
                if button_click and self.sounds_enabled:
                    button_click.play()
            
            if self.menu_load_button.handle_event(event):
                if self.load_game():
                    if button_click and self.sounds_enabled:
                        button_click.play()
            
            if self.menu_tutorial_button.handle_event(event):
                self.state = GameState.TUTORIAL
                self.tutorial_current_page = 0
                if button_click and self.sounds_enabled:
                    button_click.play()
            
            if self.menu_settings_button.handle_event(event):
                self.state = GameState.SETTINGS
                if button_click and self.sounds_enabled:
                    button_click.play()
            
            if self.menu_start_button.handle_event(event):
                # Go to player count selection screen
                self.state = GameState.PLAYER_COUNT_SELECT
                if button_click and self.sounds_enabled:
                    button_click.play()
            
            if self.menu_quick_start_button.handle_event(event):
                # Quick start with 4 players
                num_players = 4
                player_data = []
                for i in range(num_players):
                    player_data.append({
                        'name': f'Player {i+1}', 
                        'avatar': self.default_avatars[i]
                    })
                self.setup_game(player_data)
                if button_click and self.sounds_enabled:
                    button_click.play()

        # --- Handle Player Count Selection ---
        elif self.state == GameState.PLAYER_COUNT_SELECT:
            if self.player_count_back_button.handle_event(event):
                self.state = GameState.MENU
                if button_click and self.sounds_enabled:
                    button_click.play()

            if self.player_count_two_button.handle_event(event):
                self.selected_num_players = 2
                self.create_player_setup_elements(self.selected_num_players)
                self.state = GameState.PLAYER_SETUP
                if button_click and self.sounds_enabled:
                    button_click.play()

            if self.player_count_three_button.handle_event(event):
                self.selected_num_players = 3
                self.create_player_setup_elements(self.selected_num_players)
                self.state = GameState.PLAYER_SETUP
                if button_click and self.sounds_enabled:
                    button_click.play()

            if self.player_count_four_button.handle_event(event):
                self.selected_num_players = 4
                self.create_player_setup_elements(self.selected_num_players)
                self.state = GameState.PLAYER_SETUP
                if button_click and self.sounds_enabled:
                    button_click.play()
        
        elif self.state == GameState.PLAYER_SETUP:
            # Handle the back button
            if self.setup_back_button.handle_event(event):
                # Go back to player count selection instead of main menu
                self.state = GameState.PLAYER_COUNT_SELECT
                if button_click and self.sounds_enabled:
                    button_click.play()

            for textbox, image_loader in self.setup_elements:
                textbox.handle_event(event)
                if image_loader.handle_event(event):
                    if button_click and self.sounds_enabled:
                        button_click.play()
            
            all_names_filled = all(tb.text.strip() != "" for tb, _ in self.setup_elements)
            all_images_loaded = all(img.is_image_loaded() for _, img in self.setup_elements)
            self.setup_start_button.is_enabled = all_names_filled and all_images_loaded

            if self.setup_start_button.handle_event(event) and self.setup_start_button.is_enabled:
                player_data = []
                for textbox, image_loader in self.setup_elements:
                    player_data.append({
                        'name': textbox.text, 
                        'avatar': image_loader.image_surface
                    })
                self.setup_game(player_data)
                if button_click and self.sounds_enabled:
                    button_click.play()
        
        elif self.state == GameState.PLAYING:
            if self.game_roll_button.handle_event(event):
                self.handle_roll()
                if button_click and self.sounds_enabled:
                    button_click.play()
            
            if self.game_save_button.handle_event(event):
                if self.save_game():
                    if button_click and self.sounds_enabled:
                        button_click.play()
            
            if self.game_menu_button.handle_event(event):
                self.state = GameState.MENU
                if button_click and self.sounds_enabled:
                    button_click.play()
            
            if self.game_power_up_button.handle_event(event) and self.game_power_up_button.is_enabled:
                # Use the first power-up (in a more advanced version, we could let the player choose)
                if self.use_power_up(0):
                    if button_click and self.sounds_enabled:
                        button_click.play()
        
        elif self.state == GameState.GAME_OVER:
            if self.game_over_menu_button.handle_event(event):
                self.state = GameState.MENU
                if button_click and self.sounds_enabled:
                    button_click.play()
            
            if self.game_over_play_again_button.handle_event(event):
                # Reset the game with the same players
                if self.mode == GameMode.CHAMPIONSHIP:
                    self.reset_round()
                    self.state = GameState.PLAYING
                else:
                    # Reset positions
                    for player in self.players:
                        player.pos = 0
                        player.power_ups = []
                        player.shield = False
                        player.extra_rolls = 0
                        player.skip_next_turn = False
                    
                    self.current_player_index = 0
                    self.winner_index = -1
                    self.message = f"{self.players[self.current_player_index].name}'s turn"
                    self.state = GameState.PLAYING
                
                if button_click and self.sounds_enabled:
                    button_click.play()
        
        elif self.state == GameState.TUTORIAL:
            if self.tutorial_back_button.handle_event(event):
                self.state = GameState.MENU
                if button_click and self.sounds_enabled:
                    button_click.play()
            
            if self.tutorial_prev_button.handle_event(event) and self.tutorial_current_page > 0:
                self.tutorial_current_page -= 1
                if button_click and self.sounds_enabled:
                    button_click.play()
            
            if self.tutorial_next_button.handle_event(event) and self.tutorial_current_page < len(self.tutorial_pages) - 1:
                self.tutorial_current_page += 1
                if button_click and self.sounds_enabled:
                    button_click.play()
        
        elif self.state == GameState.SETTINGS:
            if self.settings_back_button.handle_event(event):
                self.state = GameState.MENU
                if button_click and self.sounds_enabled:
                    button_click.play()
            
            if self.settings_sounds_toggle.handle_event(event):
                self.sounds_enabled = self.settings_sounds_toggle.is_on
                if button_click and self.sounds_enabled:
                    button_click.play()
            
            if self.settings_difficulty_dropdown.handle_event(event):
                # Apply difficulty settings
                if button_click and self.sounds_enabled:
                    button_click.play()
            
            if self.settings_theme_dropdown.handle_event(event):
                # Apply theme settings
                if button_click and self.sounds_enabled:
                    button_click.play()
        
        return True
    
    def draw_board(self, surface):
        """Draw the game board"""
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                x = BOARD_X_POS + j * SQUARE_SIZE
                y = BOARD_Y_POS + i * SQUARE_SIZE
                color = WHITE if (i + j) % 2 == 0 else LIGHT_GREY
                pygame.draw.rect(surface, color, (x, y, SQUARE_SIZE, SQUARE_SIZE))
                pygame.draw.rect(surface, BLACK, (x, y, SQUARE_SIZE, SQUARE_SIZE), 1)
        
        # Draw numbers
        for num in range(1, 101):
            coords = get_board_coords(num)
            if coords:
                text = sidebar_font.render(str(num), True, BLACK)
                text_rect = text.get_rect(center=(coords[0] + SQUARE_SIZE // 2, coords[1] + SQUARE_SIZE // 2))
                surface.blit(text, text_rect)
        
        # Draw ladders
        for start, end in LADDERS.items():
            start_coords, end_coords = get_board_coords(start), get_board_coords(end)
            if start_coords and end_coords:
                # Draw ladder as a series of lines
                start_x = start_coords[0] + SQUARE_SIZE // 2
                start_y = start_coords[1] + SQUARE_SIZE // 2
                end_x = end_coords[0] + SQUARE_SIZE // 2
                end_y = end_coords[1] + SQUARE_SIZE // 2
                
                # Calculate ladder angle
                angle = math.atan2(end_y - start_y, end_x - start_x)
                perpendicular = angle + math.pi / 2
                
                # Draw ladder rails
                offset = 10
                pygame.draw.line(surface, LADDER_COLOR, 
                                (start_x + math.cos(perpendicular) * offset, 
                                 start_y + math.sin(perpendicular) * offset),
                                (end_x + math.cos(perpendicular) * offset, 
                                 end_y + math.sin(perpendicular) * offset), 3)
                pygame.draw.line(surface, LADDER_COLOR, 
                                (start_x - math.cos(perpendicular) * offset, 
                                 start_y - math.sin(perpendicular) * offset),
                                (end_x - math.cos(perpendicular) * offset, 
                                 end_y - math.sin(perpendicular) * offset), 3)
                
                # Draw ladder rungs
                num_rungs = 5
                for i in range(1, num_rungs):
                    t = i / num_rungs
                    rung_x = start_x + (end_x - start_x) * t
                    rung_y = start_y + (end_y - start_y) * t
                    pygame.draw.line(surface, LADDER_COLOR,
                                    (rung_x + math.cos(perpendicular) * offset,
                                     rung_y + math.sin(perpendicular) * offset),
                                    (rung_x - math.cos(perpendicular) * offset,
                                     rung_y - math.sin(perpendicular) * offset), 2)
        
        # Draw snakes with enhanced appearance
        for start, end in SNAKES.items():
            start_coords, end_coords = get_board_coords(start), get_board_coords(end)
            if start_coords and end_coords:
                # Draw snake as a curved line
                start_x = start_coords[0] + SQUARE_SIZE // 2
                start_y = start_coords[1] + SQUARE_SIZE // 2
                end_x = end_coords[0] + SQUARE_SIZE // 2
                end_y = end_coords[1] + SQUARE_SIZE // 2
                
                # Create a deterministic curve for the snake based on its position
                # This ensures the snake looks the same every time it's drawn
                hash_value = (start * 7 + end * 13) % 1000 / 1000.0
                control_offset_x = 40 * (hash_value - 0.5)
                control_offset_y = 40 * ((hash_value * 2) % 1.0 - 0.5)
                control_x = (start_x + end_x) / 2 + control_offset_x
                control_y = (start_y + end_y) / 2 + control_offset_y
                
                # Draw the snake body with gradient effect
                # First draw a thicker base layer
                pygame.draw.lines(surface, (100, 0, 0), False, 
                                 [(start_x, start_y), (control_x, control_y), (end_x, end_y)], 12)
                
                # Then draw the main body
                pygame.draw.lines(surface, SNAKE_COLOR, False, 
                                 [(start_x, start_y), (control_x, control_y), (end_x, end_y)], 8)
                
                # Draw a pattern on the snake body
                num_segments = 10
                for i in range(num_segments):
                    t = i / num_segments
                    # Calculate position along the curve
                    x = (1-t)**2 * start_x + 2*(1-t)*t * control_x + t**2 * end_x
                    y = (1-t)**2 * start_y + 2*(1-t)*t * control_y + t**2 * end_y
                    
                    # Draw pattern segments
                    if i % 2 == 0:
                        pygame.draw.circle(surface, (180, 0, 0), (int(x), int(y)), 5)
                
                # Draw snake head with more detail
                pygame.draw.circle(surface, SNAKE_COLOR, (int(start_x), int(start_y)), 12)
                pygame.draw.circle(surface, (100, 0, 0), (int(start_x), int(start_y)), 12, 2)
                
                # Draw snake eyes with pupils
                eye_offset = 5
                pygame.draw.circle(surface, WHITE, (int(start_x - eye_offset), int(start_y - eye_offset)), 4)
                pygame.draw.circle(surface, WHITE, (int(start_x + eye_offset), int(start_y - eye_offset)), 4)
                pygame.draw.circle(surface, BLACK, (int(start_x - eye_offset), int(start_y - eye_offset)), 2)
                pygame.draw.circle(surface, BLACK, (int(start_x + eye_offset), int(start_y - eye_offset)), 2)
                
                # Draw snake tongue
                tongue_length = 15
                pygame.draw.lines(surface, RED, False, 
                                 [(int(start_x), int(start_y + 5)), 
                                  (int(start_x - 5), int(start_y + tongue_length)),
                                  (int(start_x), int(start_y + tongue_length + 5)),
                                  (int(start_x + 5), int(start_y + tongue_length)),
                                  (int(start_x), int(start_y + 5))], 2)
        
        # Draw power-up squares in Power-Up mode
        if self.mode == GameMode.POWER_UP:
            for pos, power_up in POWER_UPS.items():
                coords = get_board_coords(pos)
                if coords:
                    # Draw a special square for power-ups
                    pygame.draw.rect(surface, GOLD, 
                                    (coords[0] + 5, coords[1] + 5, 
                                     SQUARE_SIZE - 10, SQUARE_SIZE - 10), 2)
                    
                    # Draw a star in the center
                    center_x = coords[0] + SQUARE_SIZE // 2
                    center_y = coords[1] + SQUARE_SIZE // 2
                    size = 10
                    
                    # Draw star
                    points = []
                    for i in range(10):
                        angle = math.pi * i / 5
                        if i % 2 == 0:
                            radius = size
                        else:
                            radius = size // 2
                        x = center_x + radius * math.cos(angle - math.pi / 2)
                        y = center_y + radius * math.sin(angle - math.pi / 2)
                        points.append((x, y))
                    
                    pygame.draw.polygon(surface, GOLD, points)
    
    def draw_players(self, surface):
        """Draw player tokens on the board"""
        for i, player in enumerate(self.players):
            if player.pos > 0:
                coords = get_board_coords(player.pos)
                if coords:
                    offset_x = (i % 2) * 20 - 10
                    offset_y = (i // 2) * 20 - 10
                    center_x = coords[0] + SQUARE_SIZE // 2 + offset_x
                    center_y = coords[1] + SQUARE_SIZE // 2 + offset_y
                    
                    # Scale the avatar to the token size
                    avatar = player.avatar_surface
                    scaled_avatar = pygame.transform.scale(avatar, (PLAYER_TOKEN_SIZE, PLAYER_TOKEN_SIZE))
                    
                    # Get the rect for the scaled avatar and center it
                    avatar_rect = scaled_avatar.get_rect(center=(center_x, center_y))
                    
                    # Blit the scaled avatar
                    surface.blit(scaled_avatar, avatar_rect)
                    
                    # Draw the border circle with the correct radius
                    pygame.draw.circle(surface, BLACK, (center_x, center_y), PLAYER_TOKEN_SIZE // 2, 2)
    
    def draw_sidebar(self, surface):
        """Draw the game sidebar"""
        pygame.draw.rect(surface, DARK_GREY, (BOARD_AREA_WIDTH, 0, SIDEBAR_WIDTH, SCREEN_HEIGHT))
        title = title_font.render("Game Info", True, WHITE)
        title_rect = title.get_rect(center=(BOARD_AREA_WIDTH + SIDEBAR_WIDTH // 2, 40))
        surface.blit(title, title_rect)
        
        current_player = self.players[self.current_player_index]
        turn_text = sidebar_font.render("Current Turn:", True, WHITE)
        surface.blit(turn_text, (BOARD_AREA_WIDTH + 20, 100))
        
        avatar = current_player.avatar_surface
        scaled_avatar = pygame.transform.scale(avatar, (40, 40))
        surface.blit(scaled_avatar, (BOARD_AREA_WIDTH + 20, 130))
        
        name_text = font.render(current_player.name, True, WHITE)
        surface.blit(name_text, (BOARD_AREA_WIDTH + 70, 135))
        
        # Draw dice
        if self.dice:
            self.dice.draw(surface)
        
        # Draw message
        message_text = sidebar_font.render(self.message, True, WHITE)
        message_rect = message_text.get_rect(center=(BOARD_AREA_WIDTH + SIDEBAR_WIDTH // 2, 350))
        surface.blit(message_text, message_rect)
        
        # Draw timer for timed mode
        if self.mode == GameMode.TIMED:
            timer_text = font.render(f"Time: {int(self.timed_mode_timer)}s", True, WHITE)
            timer_rect = timer_text.get_rect(center=(BOARD_AREA_WIDTH + SIDEBAR_WIDTH // 2, 380))
            surface.blit(timer_text, timer_rect)
        
        # Draw championship info
        if self.mode == GameMode.CHAMPIONSHIP:
            round_text = font.render(f"Round: {self.championship_current_round}/{self.championship_rounds}", True, WHITE)
            round_rect = round_text.get_rect(center=(BOARD_AREA_WIDTH + SIDEBAR_WIDTH // 2, 380))
            surface.blit(round_text, round_rect)
        
        # Draw player list
        list_title = sidebar_font.render("Players:", True, WHITE)
        surface.blit(list_title, (BOARD_AREA_WIDTH + 20, 500))
        for i, player in enumerate(self.players):
            y_pos = 530 + i * 35
            list_avatar = pygame.transform.scale(player.avatar_surface, (25, 25))
            surface.blit(list_avatar, (BOARD_AREA_WIDTH + 20, y_pos - 12))
            pos_text = sidebar_font.render(f"{player.name}: {player.pos}", True, WHITE)
            surface.blit(pos_text, (BOARD_AREA_WIDTH + 50, y_pos - 10))
            
            # Draw power-ups in Power-Up mode
            if self.mode == GameMode.POWER_UP and len(player.power_ups) > 0:
                power_up_text = font.render(f"Power-ups: {len(player.power_ups)}", True, GOLD)
                surface.blit(power_up_text, (BOARD_AREA_WIDTH + 50, y_pos + 10))
    
    def draw(self, surface):
        """Draw the game"""
        # Draw background based on game state
        if self.state == GameState.MENU:
            if menu_bg:
                surface.blit(menu_bg, (0, 0))
            else:
                surface.fill(PURPLE)
        elif self.state in [GameState.PLAYING, GameState.GAME_OVER]:
            if board_bg:
                surface.blit(board_bg, (0, 0))
            else:
                surface.fill(LIGHT_BLUE)
        else:
            surface.fill(PURPLE)
        
        if self.state == GameState.MENU:
            # Draw menu
            title_rect = self.menu_title.get_rect(center=(SCREEN_WIDTH // 2, 80))
            surface.blit(self.menu_title, title_rect)
            
            subtitle_rect = self.menu_subtitle.get_rect(center=(SCREEN_WIDTH // 2, 130))
            surface.blit(self.menu_subtitle, subtitle_rect)
            
            # Draw menu options
            self.menu_sounds_button.draw(surface)
            self.menu_mode_dropdown.draw(surface)
            self.menu_load_button.draw(surface)
            self.menu_tutorial_button.draw(surface)
            self.menu_settings_button.draw(surface)
            
            # Player slots have been removed from here
            
            # Draw buttons
            self.menu_start_button.draw(surface)
            self.menu_quick_start_button.draw(surface)
            
            # Draw footer text
            footer_text = font.render("You can save and continue your game from the game menu", True, WHITE)
            footer_rect = footer_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
            surface.blit(footer_text, footer_rect)

        # --- Draw Player Count Selection Screen ---
        elif self.state == GameState.PLAYER_COUNT_SELECT:
            title_rect = self.player_count_title.get_rect(center=(SCREEN_WIDTH // 2, 150))
            surface.blit(self.player_count_title, title_rect)

            self.player_count_back_button.draw(surface)
            self.player_count_two_button.draw(surface)
            self.player_count_three_button.draw(surface)
            self.player_count_four_button.draw(surface)

        elif self.state == GameState.PLAYER_SETUP:
            # Draw player setup
            title_rect = self.setup_title.get_rect(center=(SCREEN_WIDTH // 2, 80))
            surface.blit(self.setup_title, title_rect)
            
            for textbox, image_loader in self.setup_elements:
                textbox.draw(surface)
                image_loader.draw(surface)
            
            self.setup_back_button.draw(surface)
            self.setup_start_button.draw(surface)
        
        elif self.state == GameState.PLAYING:
            # Draw game board area
            pygame.draw.rect(surface, LIGHT_BLUE, (0, 0, BOARD_AREA_WIDTH, SCREEN_HEIGHT))
            
            # Draw board
            self.draw_board(surface)
            
            # Draw players
            self.draw_players(surface)
            
            # Draw sidebar
            self.draw_sidebar(surface)
            
            # Draw game buttons
            self.game_roll_button.draw(surface)
            self.game_save_button.draw(surface)
            self.game_menu_button.draw(surface)
            self.game_power_up_button.draw(surface)
            
            # Draw animations
            for animation in self.animations:
                animation.draw(surface)
            
            # Draw particles
            self.particle_system.draw(surface)
            
            # Draw power-up notification
            if self.show_power_up_notification:
                notification_surf = pygame.Surface((400, 60), pygame.SRCALPHA)
                notification_surf.fill((255, 215, 0, 200))  # Gold with transparency
                notification_rect = notification_surf.get_rect(center=(SCREEN_WIDTH // 2, 150))
                surface.blit(notification_surf, notification_rect)
                
                notification_text = font.render(self.power_up_notification_text, True, BLACK)
                notification_text_rect = notification_text.get_rect(center=(SCREEN_WIDTH // 2, 150))
                surface.blit(notification_text, notification_text_rect)
        
        elif self.state == GameState.GAME_OVER:
            # Draw game board area
            pygame.draw.rect(surface, LIGHT_BLUE, (0, 0, BOARD_AREA_WIDTH, SCREEN_HEIGHT))
            
            # Draw board
            self.draw_board(surface)
            
            # Draw players
            self.draw_players(surface)
            
            # Draw sidebar
            self.draw_sidebar(surface)
            
            # Draw game over overlay
            overlay_surf = pygame.Surface((400, 300), pygame.SRCALPHA)
            overlay_surf.fill((255, 255, 255, 240))
            overlay_rect = overlay_surf.get_rect(center=(BOARD_AREA_WIDTH // 2, SCREEN_HEIGHT // 2))
            surface.blit(overlay_surf, overlay_rect)
            
            # Draw winner text
            winner = self.players[self.winner_index]
            win_text = title_font.render(f"{winner.name} Wins!", True, BLACK)
            win_text_rect = win_text.get_rect(center=(BOARD_AREA_WIDTH // 2, SCREEN_HEIGHT // 2 - 80))
            surface.blit(win_text, win_text_rect)
            
            # Draw winner avatar
            winner_avatar = pygame.transform.scale(winner.avatar_surface, (80, 80))
            winner_avatar_rect = winner_avatar.get_rect(center=(BOARD_AREA_WIDTH // 2, SCREEN_HEIGHT // 2))
            surface.blit(winner_avatar, winner_avatar_rect)
            
            # Draw game mode specific information
            if self.mode == GameMode.CHAMPIONSHIP:
                # Show championship scores
                score_text = subtitle_font.render("Championship Scores:", True, BLACK)
                score_text_rect = score_text.get_rect(center=(BOARD_AREA_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
                surface.blit(score_text, score_text_rect)
                
                for i, (player, score) in enumerate(zip(self.players, self.championship_scores)):
                    player_score_text = font.render(f"{player.name}: {score} wins", True, BLACK)
                    player_score_rect = player_score_text.get_rect(center=(BOARD_AREA_WIDTH // 2, SCREEN_HEIGHT // 2 + 100 + i * 30))
                    surface.blit(player_score_text, player_score_rect)
            
            # Draw buttons
            self.game_over_play_again_button.draw(surface)
            self.game_over_menu_button.draw(surface)
        
        elif self.state == GameState.TUTORIAL:
            # Draw tutorial
            title_rect = self.tutorial_title.get_rect(center=(SCREEN_WIDTH // 2, 80))
            surface.blit(self.tutorial_title, title_rect)
            
            # Draw tutorial content
            content_surf = pygame.Surface((700, 300), pygame.SRCALPHA)
            content_surf.fill((255, 255, 255, 200))
            content_rect = content_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            surface.blit(content_surf, content_rect)
            
            # Split text into lines and render
            lines = self.tutorial_pages[self.tutorial_current_page].split('\n')
            for i, line in enumerate(lines):
                text = font.render(line, True, BLACK)
                text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60 + i * 40))
                surface.blit(text, text_rect)
            
            # Draw navigation buttons
            self.tutorial_prev_button.draw(surface)
            self.tutorial_next_button.draw(surface)
            self.tutorial_back_button.draw(surface)
            
            # Draw page indicator
            page_text = font.render(f"Page {self.tutorial_current_page + 1} of {len(self.tutorial_pages)}", True, WHITE)
            page_rect = page_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
            surface.blit(page_text, page_rect)
        
        elif self.state == GameState.SETTINGS:
            # Draw settings
            title_rect = self.settings_title.get_rect(center=(SCREEN_WIDTH // 2, 80))
            surface.blit(self.settings_title, title_rect)
            
            # Draw settings options
            self.settings_sounds_toggle.draw(surface)
            self.settings_difficulty_dropdown.draw(surface)
            self.settings_theme_dropdown.draw(surface)
            
            # Draw back button
            self.settings_back_button.draw(surface)

# Create the game instance
game = Game()

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if not game.handle_event(event):
            running = False
    
    game.update()
    game.draw(screen)
    pygame.display.flip()
    clock.tick(60)

# Clean up the tkinter root window when the game exits
if tk_root:
    tk_root.destroy()

pygame.quit()
sys.exit()