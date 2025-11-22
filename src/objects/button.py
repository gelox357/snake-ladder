import pygame

class Button:
    def __init__(self, rect, color, text_surf, value=None):
        self.rect = pygame.Rect(rect)
        self.color = color
        self.text_surf = text_surf
        self.enabled = True
        self.value = value # Added value attribute

    def handle(self, event):
        if not self.enabled:
            return False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, border_radius=12)
        pygame.draw.rect(surface, (0,0,0), self.rect, width=2, border_radius=12)
        r = self.text_surf.get_rect(center=self.rect.center)
        surface.blit(self.text_surf, r)
