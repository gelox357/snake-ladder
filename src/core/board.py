import os
import pygame
from src.config import settings

class Board:
    def __init__(self, assets=None):
        self.origin = (settings.BOARD_X, settings.BOARD_Y)
        self.size = settings.BOARD_SIZE
        self.tile = settings.TILE_SIZE
        self.rect = pygame.Rect(self.origin[0], self.origin[1], self.size, self.size)
        self.snakes = settings.SNAKES.copy()
        self.ladders = settings.LADDERS.copy()
        self.special_tiles = settings.SPECIAL_TILES.copy()
        self.assets = assets

    def square_pos(self, square):
        if square < 1:
            square = 1
        if square > 100:
            square = 100
        s = square - 1
        row = s // 10
        col = s % 10
        if row % 2 == 1:
            col = 9 - col
        x = self.origin[0] + col * self.tile + self.tile // 2
        y = self.origin[1] + (9 - row) * self.tile + self.tile // 2
        return x, y

    def apply_collision(self, square):
        if square in self.snakes:
            return self.snakes[square], "snake"
        if square in self.ladders:
            return self.ladders[square], "ladder"
        if square in self.special_tiles["powerUps"]:
            return square, "power_up"
        if square in self.special_tiles["powerDowns"]:
            return square, "power_down"
        return square, None

    def render(self, surface, font):
        path = None
        if self.assets:
            path = self.assets.manifest["images"].get("board_bg")
        if path and os.path.exists(path):
            img = self.assets.image("board_bg", (self.size, self.size))
            surface.blit(img, self.origin)
            # overlay numbers for clarity even with background image
            for r in range(10):
                for c in range(10):
                    n = r * 10 + c + 1
                    if r % 2 == 1:
                        n = r * 10 + (9 - c) + 1
                    x = self.origin[0] + c * self.tile
                    y = self.origin[1] + (9 - r) * self.tile
                    s = font.render(str(n), True, (30,30,30))
                    surface.blit(s, (x + 6, y + 6))
        
        # Draw special tiles
        for square, data in self.special_tiles["powerUps"].items():
            x, y = self.square_pos(square)
            # Draw a colored background for power-up tile
            pygame.draw.rect(surface, (76, 175, 80, 50), (x - self.tile/2 + 2, y - self.tile/2 + 2, self.tile - 4, self.tile - 4), border_radius=5)
            # Draw arrow icon
            text_surface = font.render('↑', True, (255,255,255))
            text_rect = text_surface.get_rect(center=(x, y - self.tile * 0.15))
            surface.blit(text_surface, text_rect)
            # Draw text for power-up
            power_up_text = settings.POWER_UP_TEXTS[data["type"]]
            text_lines = self.wrap_text(power_up_text, font, self.tile - 10)
            for i, line in enumerate(text_lines):
                line_surface = font.render(line, True, (255,255,255))
                line_rect = line_surface.get_rect(center=(x, y + self.tile * 0.15 + i * font.get_height()))
                surface.blit(line_surface, line_rect)

        for square, data in self.special_tiles["powerDowns"].items():
            x, y = self.square_pos(square)
            # Draw a colored background for power-down tile
            pygame.draw.rect(surface, (244, 67, 54, 50), (x - self.tile/2 + 2, y - self.tile/2 + 2, self.tile - 4, self.tile - 4), border_radius=5)
            # Draw arrow icon
            text_surface = font.render('↓', True, (255,255,255))
            text_rect = text_surface.get_rect(center=(x, y - self.tile * 0.15))
            surface.blit(text_surface, text_rect)
            # Draw text for power-down
            power_down_text = settings.POWER_DOWN_TEXTS[data["type"]]
            text_lines = self.wrap_text(power_down_text, font, self.tile - 10)
            for i, line in enumerate(text_lines):
                line_surface = font.render(line, True, (255,255,255))
                line_rect = line_surface.get_rect(center=(x, y + self.tile * 0.15 + i * font.get_height()))
                surface.blit(line_surface, line_rect)

        pygame.draw.rect(surface, (0, 0, 0), self.rect, width=3, border_radius=14)

    def wrap_text(self, text, font, max_width):
        words = text.split(' ')
        lines = []
        current_line = ''
        for word in words:
            test_line = current_line + word + ' '
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                lines.append(current_line.strip())
                current_line = word + ' '
        lines.append(current_line.strip())
        return lines
