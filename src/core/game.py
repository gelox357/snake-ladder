import os
import pygame
import base64 # Import base64 for image data handling
from src.config import settings
from src.services.assets import AssetLoader
from src.services.persistence import save, load
from src.scenes.menu_scene import MenuScene
from src.scenes.board_scene import BoardScene
from src.scenes.profile_scene import ProfileScene

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.width = settings.WINDOW_WIDTH
        self.height = settings.WINDOW_HEIGHT
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Snakes & Ladders")
        pygame.event.set_grab(True) # Ensure mouse events are captured
        pygame.mouse.set_visible(True) # Ensure mouse is visible
        self.clock = pygame.time.Clock()
        self.assets = AssetLoader(settings.ASSET_MANIFEST)
        self.scenes = []
        self.paused = False
        self.push(MenuScene(self))

    def push(self, scene):
        self.scenes.append(scene)

    def pop(self):
        self.scenes.pop()

    def start_board(self, names, player_images, sound_on, mode):
        self.scenes = [BoardScene(self, names, player_images, sound_on, mode)]

    def goto_menu(self):
        self.scenes = [MenuScene(self)]

    def goto_profiles(self):
        self.scenes = [ProfileScene(self)]

    def save_state(self, data):
        save(os.path.join("saves", "game.json"), data)

    def load_saved(self):
        data = load(os.path.join("saves", "game.json"))
        if not data:
            return
        players_data = data["players"]
        names = [p["name"] for p in players_data]
        player_images = []
        for p_data in players_data:
            if "image_data" in p_data and p_data["image_data"]:
                img_bytes = base64.b64decode(p_data["image_data"])
                img_surface = pygame.image.fromstring(img_bytes, p_data["image_size"], 'RGBA')
                player_images.append(img_surface)
            else:
                player_images.append(None) # Ensure None is appended if no image data

        scene = BoardScene(self, names, player_images, True, data.get("mode","Classic"))
        for i, pd in enumerate(players_data):
            scene.players[i].square = pd["square"]
        scene.turn = data["turn"]
        scene.mode = data.get("mode", "classic")
        scene.timed_remaining = data.get("timed_remaining", settings.TIMED_MODE_DURATION)
        scene.endless_scores = data.get("endless_scores", [0]*len(names))
        scene.start_mode_logic() # Restart mode logic after loading
        self.scenes = [scene]

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(settings.FPS) / 1000.0
            pygame.event.pump() # Explicitly process events
            for event in pygame.event.get():
                print(f"Game event: {event.type}") # Debug print for all events
                if event.type == pygame.QUIT:
                    running = False
                else:
                    self.scenes[-1].handle(event)
            self.scenes[-1].update(dt)
            self.scenes[-1].render(self.screen)
            pygame.display.flip()
        pygame.quit()
