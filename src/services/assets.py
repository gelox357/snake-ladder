import os
import pygame

class AssetLoader:
    def __init__(self, manifest):
        self.manifest = manifest
        self.images = {}
        self.sounds = {}
        self.fonts = {}

    def _find_candidate(self, key):
        base_dir = os.path.join("assets", "images")
        if not os.path.isdir(base_dir):
            return None
        candidates = {
            "dice_custom": ["dice_custom", "dice", "die"],
            "zombie_head": ["zombie_head", "zombie", "snake_zombie", "snakehead", "snake"],
            "board_bg": ["board_bg", "board", "background", "bg", "snakeboard"]
        }.get(key, [key])
        exts = (".png", ".jpg", ".jpeg")
        files = os.listdir(base_dir)
        for name in files:
            lower = name.lower()
            for c in candidates:
                if lower.startswith(c) and os.path.splitext(lower)[1] in exts:
                    return os.path.join(base_dir, name)
        return None

    def image(self, key, size=None):
        if key in self.images:
            img = self.images[key]
        else:
            path = self.manifest["images"].get(key)
            if not path or not os.path.exists(path):
                found = self._find_candidate(key)
                if found:
                    path = found
                    self.manifest["images"][key] = path
                else:
                    # Fallback to snakeboard.png if no specific asset or candidate is found
                    if os.path.exists("assets/images/snakeboard.png"):
                        path = "assets/images/snakeboard.png"
                        self.manifest["images"][key] = path # Cache this fallback
            
            if path and os.path.exists(path):
                try:
                    img = pygame.image.load(path).convert_alpha()
                except Exception:
                    # If loading fails, create a generic gray circle
                    img = pygame.Surface((64, 64), pygame.SRCALPHA)
                    pygame.draw.circle(img, (200, 200, 200), (32, 32), 30)
            else:
                # If no path is found or fallback fails, create a generic gray circle
                img = pygame.Surface((64, 64), pygame.SRCALPHA)
                pygame.draw.circle(img, (200, 200, 200), (32, 32), 30)
            self.images[key] = img
        if size:
            return pygame.transform.smoothscale(img, size)
        return img

    def sound(self, key):
        if key in self.sounds:
            return self.sounds[key]
        path = self.manifest["sounds"].get(key)
        s = None
        if path and os.path.exists(path):
            try:
                s = pygame.mixer.Sound(path)
            except Exception:
                s = None
        self.sounds[key] = s
        return s

    def font(self, path, size):
        k = (path, size)
        if k in self.fonts:
            return self.fonts[k]
        if path and os.path.exists(path):
            f = pygame.font.Font(path, size)
        else:
            f = pygame.font.SysFont("arial", size)
        self.fonts[k] = f
        return f
