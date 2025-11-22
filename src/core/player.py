import pygame # Import pygame to handle default image creation
from src.config import settings

class Player:
    def __init__(self, name, color, image=None):
        self.name = name
        self.color = color
        self.square = 1
        self.image = image
        if self.image is None:
            # Create a default circular image if no image is provided
            self.image = pygame.Surface((settings.TILE_SIZE // 2, settings.TILE_SIZE // 2), pygame.SRCALPHA)
            pygame.draw.circle(self.image, self.color, (settings.TILE_SIZE // 4, settings.TILE_SIZE // 4), settings.TILE_SIZE // 4)
        self.moves = 0
        self.climbed = 0
        self.snake_hits = 0
        self.move_queue = []
        self.anim_from = 1
        self.anim_to = 1
        self.anim_t = 1.0
        self.anim_speed = 4.0

        # Power-up/down flags
        self.doubleNext = False
        self.halfNext = False
        self.skipSnake = False
        self.loseTurn = False # Added for 'loseTurn' power-down

        # For snake animation
        self.animated_x = None
        self.animated_y = None

    def enqueue_steps(self, steps):
        for _ in range(steps):
            self.move_queue.append(1)

    def step(self):
        if not self.move_queue:
            return False
        prev = self.square
        self.square += self.move_queue.pop(0)
        if self.square > 100:
            over = self.square - 100
            self.square = 100 - over
        self.moves += 1
        self.anim_from = prev
        self.anim_to = self.square
        self.anim_t = 0.0
        return True

    def advance_anim(self, dt):
        if self.anim_t < 1.0:
            self.anim_t = min(1.0, self.anim_t + dt * self.anim_speed)
