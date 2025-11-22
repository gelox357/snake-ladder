import random
import math
import os
import pygame

class Dice:
    def __init__(self, asset_loader):
        self.asset_loader = asset_loader
        self.face = 1
        self.time = 0.0
        self.rolling = False
        self.duration = 0.9
        self.angle = 0.0
        self.offset = 0.0

    def start(self):
        if self.rolling:
            return
        self.rolling = True
        self.time = 0.0
        self.angle = 0.0
        self.offset = 0.0
        s = self.asset_loader.sound("roll")
        if s:
            try:
                s.play()
            except Exception:
                pass

    def update(self, dt):
        if not self.rolling:
            return False
        self.time += dt
        self.face = random.randint(1, 6)
        self.angle += 720 * dt
        self.offset = 6 * math.sin(self.time * 18)
        if self.time >= self.duration:
            self.rolling = False
            self.face = random.randint(1, 6)
            return True
        return False

    def draw(self, surface, rect):
        base = pygame.Surface((rect[2], rect[3]), pygame.SRCALPHA)
        shade = pygame.Surface((rect[2], rect[3]), pygame.SRCALPHA)
        pygame.draw.rect(shade, (0,0,0,60), (6,8,rect[2]-12,rect[3]-12), border_radius=12)
        base.blit(shade, (0,0))
        custom_path = self.asset_loader.manifest["images"].get("dice_custom")
        use_custom = custom_path and os.path.exists(custom_path)
        src = self.asset_loader.image("dice_custom", (rect[2] - 16, rect[3] - 16)) if use_custom else self.asset_loader.image(f"dice_{self.face}", (rect[2] - 16, rect[3] - 16))
        img = pygame.transform.rotate(src, self.angle if self.rolling else 0)
        r = img.get_rect(center=(rect[0] + rect[2] // 2, rect[1] + rect[3] // 2 + int(self.offset)))
        pygame.draw.rect(surface, (240,240,255), rect, border_radius=12)
        pygame.draw.rect(surface, (0, 0, 0), rect, width=3, border_radius=12)
        surface.blit(img, r)
        if not self.rolling:
            if self.face == 6:
                glow = pygame.Surface((rect[2], rect[3]), pygame.SRCALPHA)
                pygame.draw.ellipse(glow, (16,185,129,90), (0,0,rect[2],rect[3]))
                surface.blit(glow, (rect[0], rect[1]))
            if self.face == 1:
                flash = pygame.Surface((rect[2], rect[3]), pygame.SRCALPHA)
                pygame.draw.rect(flash, (244,114,182,70), (0,0,rect[2],rect[3]), border_radius=12)
                surface.blit(flash, (rect[0], rect[1]))