import pygame
from src.core.scene import Scene
from src.config import settings
from src.services.profiles import ProfileStore
from src.objects.button import Button
from src.ui.draw import vertical_gradient, rounded_rect

class ProfileScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.store = ProfileStore()
        self.font = game.assets.font(settings.FONT_REGULAR, 22)
        self.title_font = game.assets.font(settings.FONT_BOLD, 36)
        self.back_btn = Button((40, 40, 120, 44), settings.COLOR_BUTTON_MENU, self.font.render("Back", True, (255,255,255)))
        self.save_btn = Button((800, 40, 120, 44), settings.COLOR_BUTTON_SAVE, self.font.render("Save", True, (255,255,255)))
        self.name = "Player 1"
        self.color_idx = 0
        self.colors = [(66,135,245),(255,165,0),(16,185,129),(244,114,182)]

    def handle(self, event):
        if self.back_btn.handle(event):
            self.game.goto_menu()
        if self.save_btn.handle(event):
            p = self.store.get(self.name)
            p.color = self.colors[self.color_idx]
            self.store.save()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.color_idx = (self.color_idx - 1) % len(self.colors)
            if event.key == pygame.K_RIGHT:
                self.color_idx = (self.color_idx + 1) % len(self.colors)

    def update(self, dt):
        pass

    def render(self, surface):
        vertical_gradient(surface, (0,0,self.game.width,self.game.height), settings.COLOR_BG_TOP, settings.COLOR_BG_BOTTOM)
        rounded_rect(surface, (160,140,640,680), (255,255,255), 16)
        t = self.title_font.render("Profile", True, (40,40,60))
        surface.blit(t, (180, 160))
        self.back_btn.draw(surface)
        self.save_btn.draw(surface)
        name = self.font.render(self.name, True, (30,30,40))
        surface.blit(name, (180, 220))
        color = self.colors[self.color_idx]
        pygame.draw.circle(surface, color, (480, 400), 60)
        stats = self.font.render("Use ← → to change color", True, (60,60,70))
        surface.blit(stats, (330, 520))