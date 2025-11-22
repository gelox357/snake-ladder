import pygame
from src.config import settings

class Ladder:
    def __init__(self, bottom_square, top_square):
        self.bottom_square = bottom_square
        self.top_square = top_square

    def draw(self, surface, board):
        s_coord = board.square_pos(self.bottom_square)
        e_coord = board.square_pos(self.top_square)

        # Calculate ladder dimensions
        dx = e_coord[0] - s_coord[0]
        dy = e_coord[1] - s_coord[1]
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Ladder width
        ladder_width = int(board.tile * 0.4)
        
        # Calculate perpendicular direction for ladder width
        perp_x = -dy / distance * ladder_width / 2 if distance > 0 else 0
        perp_y = dx / distance * ladder_width / 2 if distance > 0 else 0
        
        # Draw shadow
        shadow_offset_x = 2
        shadow_offset_y = 2
        
        # Left side shadow
        pygame.draw.line(surface, (0, 0, 0, 70), 
                         (s_coord[0] + perp_x + shadow_offset_x, s_coord[1] + perp_y + shadow_offset_y), 
                         (e_coord[0] + perp_x + shadow_offset_x, e_coord[1] + perp_y + shadow_offset_y), 
                         int(board.tile * 0.2) + 4)
        # Right side shadow
        pygame.draw.line(surface, (0, 0, 0, 70), 
                         (s_coord[0] - perp_x + shadow_offset_x, s_coord[1] - perp_y + shadow_offset_y), 
                         (e_coord[0] - perp_x + shadow_offset_x, e_coord[1] - perp_y + shadow_offset_y), 
                         int(board.tile * 0.2) + 4)

        # Draw ladder sides
        pygame.draw.line(surface, settings.COLOR_LADDER_RAIL, 
                         (s_coord[0] + perp_x, s_coord[1] + perp_y), 
                         (e_coord[0] + perp_x, e_coord[1] + perp_y), 
                         int(board.tile * 0.2))
        pygame.draw.line(surface, settings.COLOR_LADDER_RAIL, 
                         (s_coord[0] - perp_x, s_coord[1] - perp_y), 
                         (e_coord[0] - perp_x, e_coord[1] - perp_y), 
                         int(board.tile * 0.2))
        
        # Draw ladder rungs
        rung_count = max(3, int(distance / (board.tile * 0.6)))
        rung_width = int(board.tile * 0.15)
        
        for i in range(1, rung_count + 1):
            t = i / (rung_count + 1)
            rung_x = s_coord[0] + dx * t
            rung_y = s_coord[1] + dy * t
            
            # Calculate rung endpoints with slight inward angle
            inward_angle_factor = 0.1 # Small factor to make rungs slightly angled inward
            current_perp_x = perp_x * (1 - inward_angle_factor * (i - rung_count/2) / (rung_count/2))
            current_perp_y = perp_y * (1 - inward_angle_factor * (i - rung_count/2) / (rung_count/2))
            
            pygame.draw.line(surface, settings.COLOR_LADDER_RUNG, 
                             (rung_x - current_perp_x, rung_y - current_perp_y), 
                             (rung_x + current_perp_x, rung_y + current_perp_y), 
                             rung_width)
        
        # Add wood texture effect
        texture_line_width = int(board.tile * 0.05)
        for i in range(3):
            offset = (i - 1) * int(board.tile * 0.08)
            
            # Left side grain
            pygame.draw.line(surface, (62, 39, 35, 70), 
                             (s_coord[0] + perp_x + offset, s_coord[1] + perp_y), 
                             (e_coord[0] + perp_x + offset, e_coord[1] + perp_y), 
                             texture_line_width)
            
            # Right side grain
            pygame.draw.line(surface, (62, 39, 35, 70), 
                             (s_coord[0] - perp_x + offset, s_coord[1] - perp_y), 
                             (e_coord[0] - perp_x + offset, e_coord[1] - perp_y), 
                             texture_line_width)
