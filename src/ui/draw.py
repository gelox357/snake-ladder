import pygame

def vertical_gradient(surface, rect, top_color, bottom_color):
    x, y, w, h = rect
    for i in range(h):
        t = i / max(1, h - 1)
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * t)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * t)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * t)
        pygame.draw.line(surface, (r, g, b), (x, y + i), (x + w, y + i))

def rounded_rect(surface, rect, color, radius):
    pygame.draw.rect(surface, color, rect, border_radius=radius)

def shadow(surface, rect, radius, alpha):
    s = pygame.Surface((rect[2], rect[3]), pygame.SRCALPHA)
    pygame.draw.rect(s, (0, 0, 0, alpha), (0, 0, rect[2], rect[3]), border_radius=radius)
    surface.blit(s, (rect[0], rect[1]))

def pill(surface, rect, color1, color2):
    vertical_gradient(surface, rect, color1, color2)
    pygame.draw.rect(surface, (0, 0, 0), rect, width=2, border_radius=22)

def text(surface, font, s, color, pos, center=False):
    img = font.render(s, True, color)
    if center:
        r = img.get_rect(center=pos)
        surface.blit(img, r)
    else:
        surface.blit(img, pos)