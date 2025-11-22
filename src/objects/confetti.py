import pygame
import random

class Confetti:
    def __init__(self, x, y, color, size, speed):
        self.x = x
        self.y = y
        self.color = color
        self.size = size
        self.speed = speed
        self.angle = random.uniform(0, 2 * 3.14159)
        self.rotation_speed = random.uniform(-0.2, 0.2)
        self.gravity = 0.2
        self.velocity_y = random.uniform(-5, -2)
        self.velocity_x = random.uniform(-2, 2)
        self.alpha = 255
        self.shape = random.choice(["square", "circle"])

    def update(self, dt):
        self.velocity_y += self.gravity
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        self.angle += self.rotation_speed * dt
        self.alpha -= 2 * dt # Fade out over time

    def draw(self, surface):
        if self.alpha <= 0:
            return

        temp_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        temp_surface.fill((0,0,0,0)) # Transparent background

        color_with_alpha = self.color + (int(self.alpha),)

        if self.shape == "square":
            pygame.draw.rect(temp_surface, color_with_alpha, (self.size/2, self.size/2, self.size, self.size))
        else: # circle
            pygame.draw.circle(temp_surface, color_with_alpha, (self.size, self.size), self.size/2)

        rotated_surface = pygame.transform.rotate(temp_surface, self.angle * 180 / 3.14159)
        rotated_rect = rotated_surface.get_rect(center=(self.x, self.y))
        surface.blit(rotated_surface, rotated_rect)
