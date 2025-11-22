import pygame
from src.ui.draw import pill

class StatusBar:
    def __init__(self, rect, color1, color2, font):
        self.rect = pygame.Rect(rect)
        self.c1 = color1
        self.c2 = color2
        self.font = font
        self.text = ""

    def set_text(self, s):
        self.text = s

    def draw(self, surface, color_text):
        pill(surface, self.rect, self.c1, self.c2)
        img = self.font.render(self.text, True, color_text)
        r = img.get_rect(center=self.rect.center)
        surface.blit(img, r)