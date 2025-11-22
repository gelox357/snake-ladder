import pygame
from src.core.scene import Scene
from src.config import settings
from src.ui.draw import vertical_gradient, rounded_rect, text
from src.objects.button import Button

class MenuScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.title_font = game.assets.font(settings.FONT_BOLD, 48)
        self.ui_font = game.assets.font(settings.FONT_REGULAR, 22)
        self.small_font = game.assets.font(settings.FONT_REGULAR, 16)

        self.players_count = 4
        self.sound_on = True
        self.mode = "classic"
        self.names = [f"Player {i+1}" for i in range(4)]
        self.player_images = [None for _ in range(4)] # Store player image surfaces

        # UI elements
        self.player_count_options = [
            Button((320, 260, 100, 40), settings.COLOR_BUTTON_MENU, self.small_font.render("2 Players", True, settings.COLOR_BUTTON_TEXT), value=2),
            Button((430, 260, 100, 40), settings.COLOR_BUTTON_MENU, self.small_font.render("3 Players", True, settings.COLOR_BUTTON_TEXT), value=3),
            Button((540, 260, 100, 40), settings.COLOR_BUTTON_MENU, self.small_font.render("4 Players", True, settings.COLOR_BUTTON_TEXT), value=4)
        ]
        self.sound_toggle = Button((320, 310, 120, 40), settings.COLOR_BUTTON_MENU, self.small_font.render("Sound: ON", True, settings.COLOR_BUTTON_TEXT))
        self.mode_options = [
            Button((320, 360, 100, 40), settings.COLOR_BUTTON_MENU, self.small_font.render("Classic", True, settings.COLOR_BUTTON_TEXT), value="classic"),
            Button((430, 360, 100, 40), settings.COLOR_BUTTON_MENU, self.small_font.render("Timed", True, settings.COLOR_BUTTON_TEXT), value="timed"),
            Button((540, 360, 100, 40), settings.COLOR_BUTTON_MENU, self.small_font.render("Endless", True, settings.COLOR_BUTTON_TEXT), value="endless")
        ]

        self.player_name_inputs = []
        self.create_player_setup_ui()

        self.start_btn = Button((320, 760, 160, 48), settings.COLOR_BUTTON_ROLL, self.ui_font.render("Start Game", True, settings.COLOR_BUTTON_TEXT))
        self.quick_btn = Button((500, 760, 160, 48), settings.COLOR_BUTTON_RESTART, self.ui_font.render("Quick Start", True, settings.COLOR_BUTTON_TEXT))
        self.load_btn = Button((620, 200, 140, 40), settings.COLOR_BUTTON_SAVE, self.ui_font.render("Load Saved", True, settings.COLOR_BUTTON_TEXT))
        self.profile_btn = Button((470, 200, 140, 40), settings.COLOR_BUTTON_MENU, self.ui_font.render("Profiles", True, settings.COLOR_BUTTON_TEXT))

    def create_player_setup_ui(self):
        self.player_name_inputs = []
        for i in range(self.players_count):
            y = 420 + i * 60
            name_input_rect = pygame.Rect(320, y, 250, 40)
            self.player_name_inputs.append({
                "rect": name_input_rect,
                "text": self.names[i],
                "active": False,
                "image_rect": pygame.Rect(260, y, 40, 40), # Rect for image upload area
                "image_surface": None # Store loaded image surface
            })

    def handle(self, event):
        for btn in self.player_count_options:
            if btn.handle(event):
                self.players_count = btn.value
                self.names = self.names[:self.players_count] + [f"Player {i+1}" for i in range(len(self.names), self.players_count)]
                self.player_images = self.player_images[:self.players_count] + [None for _ in range(len(self.player_images), self.players_count)]
                self.create_player_setup_ui()

        if self.sound_toggle.handle(event):
            self.sound_on = not self.sound_on
            self.sound_toggle.text = self.small_font.render(f"Sound: {'ON' if self.sound_on else 'OFF'}", True, settings.COLOR_BUTTON_TEXT)

        for btn in self.mode_options:
            if btn.handle(event):
                self.mode = btn.value

        for i, input_field in enumerate(self.player_name_inputs):
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_field["rect"].collidepoint(event.pos):
                    input_field["active"] = True
                elif input_field["image_rect"].collidepoint(event.pos):
                    print(f"Image upload clicked for Player {i+1}")
                else:
                    input_field["active"] = False
            if event.type == pygame.KEYDOWN and input_field["active"]:
                if event.key == pygame.K_BACKSPACE:
                    input_field["text"] = input_field["text"][:-1]
                else:
                    input_field["text"] += event.unicode
                self.names[i] = input_field["text"]

        if self.start_btn.handle(event):
            print("Start Game button clicked!") # Debug print
            final_player_images = []
            for i in range(self.players_count):
                if self.player_name_inputs[i]["image_surface"]:
                    final_player_images.append(self.player_name_inputs[i]["image_surface"])
                else:
                    final_player_images.append(None)
            self.game.start_board(self.names[:self.players_count], final_player_images, self.sound_on, self.mode)
        if self.quick_btn.handle(event):
            default_images = [None for _ in range(self.players_count)]
            self.game.start_board([f"Player {i+1}" for i in range(self.players_count)], default_images, True, "classic")
        if self.load_btn.handle(event):
            self.game.load_saved()
        if self.profile_btn.handle(event):
            self.game.goto_profiles()

    def update(self, dt):
        pass

    def render(self, surface):
        vertical_gradient(surface, (0,0,self.game.width,self.game.height), settings.COLOR_BG_TOP, settings.COLOR_BG_BOTTOM)
        text(surface, self.title_font, "Snakes & Ladders", (255,255,255), (self.game.width//2, 120), center=True)
        info = self.ui_font.render("Classic Edition — Enhanced (Modes, sound, save, pause, mobile-friendly)", True, (230,230,230))
        r = info.get_rect(center=(self.game.width//2, 170))
        surface.blit(info, r)
        rounded_rect(surface, (220, 220, 520, 580), (255,255,255), 16) # Adjusted height for new UI elements

        # Player count selection
        text(surface, self.small_font, "Players:", (30,30,30), (260, 270), center=False)
        for btn in self.player_count_options:
            btn.draw(surface)
            if btn.value == self.players_count:
                pygame.draw.rect(surface, settings.COLOR_ACCENT, btn.rect, 3, border_radius=10) # Highlight selected

        # Sound toggle
        self.sound_toggle.draw(surface)
        if self.sound_on:
            pygame.draw.rect(surface, settings.COLOR_ACCENT, self.sound_toggle.rect, 3, border_radius=10)

        # Game mode selection
        text(surface, self.small_font, "Mode:", (30,30,30), (260, 370), center=False)
        for btn in self.mode_options:
            btn.draw(surface)
            if btn.value == self.mode:
                pygame.draw.rect(surface, settings.COLOR_ACCENT, btn.rect, 3, border_radius=10) # Highlight selected

        # Player setup inputs
        for i, input_field in enumerate(self.player_name_inputs):
            # Draw image upload area
            pygame.draw.circle(surface, (220,220,220), input_field["image_rect"].center, 20)
            if input_field["image_surface"]:
                surface.blit(input_field["image_surface"], input_field["image_rect"])
            else:
                text(surface, self.small_font, "📷", (100,100,100), input_field["image_rect"].center, center=True)

            # Draw name input field
            pygame.draw.rect(surface, (245,245,255), input_field["rect"], border_radius=12)
            if input_field["active"]:
                pygame.draw.rect(surface, settings.COLOR_ACCENT, input_field["rect"], 2, border_radius=12)
            
            name_surface = self.ui_font.render(input_field["text"], True, (30,30,30))
            surface.blit(name_surface, (input_field["rect"].x + 10, input_field["rect"].y + 8))

        self.load_btn.draw(surface)
        self.profile_btn.draw(surface)
        self.start_btn.draw(surface)
        self.quick_btn.draw(surface)

        tip_text = self.small_font.render("Tip: Save and resume games from in-game menu.", True, (150,150,150))
        tip_rect = tip_text.get_rect(center=(self.game.width//2, 820))
        surface.blit(tip_text, tip_rect)
