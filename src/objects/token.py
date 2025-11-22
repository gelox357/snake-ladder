import pygame

class Token:
    def __init__(self, img, color):
        self.img = img
        self.color = color

    def draw(self, surface, pos):
        if self.img:
            r = self.img.get_rect(center=pos)
            surface.blit(self.img, r)
        else:
            pygame.draw.circle(surface, self.color, pos, 16)