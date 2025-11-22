import math
import pygame
from src.config import settings

class Snake:
    def __init__(self, head_square, tail_square):
        self.head_square = head_square
        self.tail_square = tail_square
        self.time = 0.0
        self.eat_time = 0.0
        self.amplitude = 10.0
        self.frequency = 2.0

    def update(self, dt):
        self.time += dt
        if self.eat_time > 0:
            self.eat_time = max(0.0, self.eat_time - dt)

    def trigger_eat(self):
        self.eat_time = 0.6

    def _path_points(self, board):
        s_coord = board.square_pos(self.head_square)
        e_coord = board.square_pos(self.tail_square)

        # Calculate control points for a more natural snake curve
        dx = e_coord[0] - s_coord[0]
        dy = e_coord[1] - s_coord[1]
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Create multiple control points for a more winding snake
        # Add perpendicular offset for a more curved snake
        perp_x = -dy / distance if distance > 0 else 0
        perp_y = dx / distance if distance > 0 else 0
        curve_amount = min(distance * 0.3, board.tile * 2)
        
        control_x1 = s_coord[0] + dx * 0.25 + perp_x * curve_amount
        control_y1 = s_coord[1] + dy * 0.25 + perp_y * curve_amount
        control_x2 = s_coord[0] + dx * 0.75 - perp_x * curve_amount
        control_y2 = s_coord[1] + dy * 0.75 - perp_y * curve_amount
        
        pts = []
        segment_count = 20 # More segments for smoother curve
        for i in range(segment_count + 1):
            t = i / segment_count
            # Quadratic Bezier curve calculation
            x = (1 - t)**3 * s_coord[0] + 3 * (1 - t)**2 * t * control_x1 + 3 * (1 - t) * t**2 * control_x2 + t**3 * e_coord[0]
            y = (1 - t)**3 * s_coord[1] + 3 * (1 - t)**2 * t * control_y1 + 3 * (1 - t) * t**2 * control_y2 + t**3 * e_coord[1]
            pts.append((x, y))
        return pts

    def draw(self, surface, board):
        pts = self._path_points(board)
        
        # Draw shadow
        # Pygame doesn't have built-in shadow, so we draw a slightly offset darker version
        shadow_offset_x = 2
        shadow_offset_y = 2
        for i in range(len(pts) - 1):
            p1 = (pts[i][0] + shadow_offset_x, pts[i][1] + shadow_offset_y)
            p2 = (pts[i+1][0] + shadow_offset_x, pts[i+1][1] + shadow_offset_y)
            pygame.draw.line(surface, (0, 0, 0, 70), p1, p2, int(board.tile * 0.4) + 4) # Darker, thicker line for shadow

        # Draw snake body as segmented segments
        segment_width = int(board.tile * 0.4)
        for i in range(len(pts) - 1):
            p1 = pts[i]
            p2 = pts[i+1]
            
            # Calculate segment angle
            angle = math.atan2(p2[1] - p1[1], p2[0] - p1[0])
            perp_segment_x = -math.sin(angle) * segment_width / 2
            perp_segment_y = math.cos(angle) * segment_width / 2
            
            # Draw segment
            segment_points = [
                (p1[0] + perp_segment_x, p1[1] + perp_segment_y),
                (p2[0] + perp_segment_x, p2[1] + perp_segment_y),
                (p2[0] - perp_segment_x, p2[1] - perp_segment_y),
                (p1[0] - perp_segment_x, p1[1] - perp_segment_y)
            ]
            pygame.draw.polygon(surface, settings.COLOR_SNAKE, segment_points)
            
            # Draw segment border
            pygame.draw.polygon(surface, settings.COLOR_SNAKE_DARK, segment_points, int(board.tile * 0.05))
            
            # Draw scale pattern on segment
            if i % 2 == 0:
                scale_size = int(board.tile * 0.06)
                mid_x = (p1[0] + p2[0]) / 2
                mid_y = (p1[1] + p2[1]) / 2
                
                for j in [-1, 0, 1]:
                    scale_x = mid_x + j * perp_segment_x * 0.6
                    scale_y = mid_y + j * perp_segment_y * 0.6
                    pygame.draw.circle(surface, settings.COLOR_SNAKE_DARK, (int(scale_x), int(scale_y)), scale_size)
        
        # Draw snake head - triangular/oval shape
        head_length = int(board.tile * 0.6)
        head_width = int(board.tile * 0.45)
        
        # Calculate head angle (pointing in direction of first segment)
        if len(pts) > 1:
            first_segment_angle = math.atan2(pts[1][1] - pts[0][1], pts[1][0] - pts[0][0])
        else:
            first_segment_angle = 0 # Default if only one point

        head_center = pts[0]
        
        # Draw triangular snake head
        head_points = [
            (head_center[0] + head_length/2 * math.cos(first_segment_angle), head_center[1] + head_length/2 * math.sin(first_segment_angle)),
            (head_center[0] - head_length/3 * math.cos(first_segment_angle) - head_width/2 * math.sin(first_segment_angle), head_center[1] - head_length/3 * math.sin(first_segment_angle) + head_width/2 * math.cos(first_segment_angle)),
            (head_center[0] - head_length/4 * math.cos(first_segment_angle), head_center[1] - head_length/4 * math.sin(first_segment_angle)),
            (head_center[0] - head_length/3 * math.cos(first_segment_angle) + head_width/2 * math.sin(first_segment_angle), head_center[1] - head_length/3 * math.sin(first_segment_angle) - head_width/2 * math.cos(first_segment_angle))
        ]
        pygame.draw.polygon(surface, settings.COLOR_SNAKE, head_points)
        pygame.draw.polygon(surface, settings.COLOR_SNAKE_DARK, head_points, int(board.tile * 0.05))
        
        # Draw eyes
        eye_size = int(board.tile * 0.08)
        eye_offset_dist = head_length / 6
        eye_offset_perp = head_width / 4
        
        eye_x_base = head_center[0] + eye_offset_dist * math.cos(first_segment_angle)
        eye_y_base = head_center[1] + eye_offset_dist * math.sin(first_segment_angle)
        
        left_eye_x = eye_x_base - eye_offset_perp * math.sin(first_segment_angle)
        left_eye_y = eye_y_base + eye_offset_perp * math.cos(first_segment_angle)
        
        right_eye_x = eye_x_base + eye_offset_perp * math.sin(first_segment_angle)
        right_eye_y = eye_y_base - eye_offset_perp * math.cos(first_segment_angle)
        
        pygame.draw.circle(surface, (255,255,255), (int(left_eye_x), int(left_eye_y)), eye_size)
        pygame.draw.circle(surface, (0,0,0), (int(left_eye_x), int(left_eye_y)), int(eye_size * 0.6))
        pygame.draw.circle(surface, (255,255,255), (int(right_eye_x), int(right_eye_y)), eye_size)
        pygame.draw.circle(surface, (0,0,0), (int(right_eye_x), int(right_eye_y)), int(eye_size * 0.6))
        
        # Draw nostrils
        nostril_size = int(board.tile * 0.03)
        nostril_offset_dist = head_length / 2 - 2
        nostril_offset_perp = head_width / 8
        
        nostril_x_base = head_center[0] + nostril_offset_dist * math.cos(first_segment_angle)
        nostril_y_base = head_center[1] + nostril_offset_dist * math.sin(first_segment_angle)
        
        left_nostril_x = nostril_x_base - nostril_offset_perp * math.sin(first_segment_angle)
        left_nostril_y = nostril_y_base + nostril_offset_perp * math.cos(first_segment_angle)
        
        right_nostril_x = nostril_x_base + nostril_offset_perp * math.sin(first_segment_angle)
        right_nostril_y = nostril_y_base - nostril_offset_perp * math.cos(first_segment_angle)
        
        pygame.draw.circle(surface, (0,0,0), (int(left_nostril_x), int(left_nostril_y)), nostril_size)
        pygame.draw.circle(surface, (0,0,0), (int(right_nostril_x), int(right_nostril_y)), nostril_size)
        
        # Draw tongue
        tongue_length = int(board.tile * 0.2)
        tongue_width = int(board.tile * 0.05)
        
        tongue_start_x = head_center[0] + head_length/2 * math.cos(first_segment_angle)
        tongue_start_y = head_center[1] + head_length/2 * math.sin(first_segment_angle)
        
        tongue_end_x1 = tongue_start_x + tongue_length * math.cos(first_segment_angle - 0.3)
        tongue_end_y1 = tongue_start_y + tongue_length * math.sin(first_segment_angle - 0.3)
        
        tongue_end_x2 = tongue_start_x + tongue_length * math.cos(first_segment_angle + 0.3)
        tongue_end_y2 = tongue_start_y + tongue_length * math.sin(first_segment_angle + 0.3)
        
        pygame.draw.line(surface, (211, 47, 47), (int(tongue_start_x), int(tongue_start_y)), (int(tongue_end_x1), int(tongue_end_y1)), int(tongue_width))
        pygame.draw.line(surface, (211, 47, 47), (int(tongue_start_x), int(tongue_start_y)), (int(tongue_end_x2), int(tongue_end_y2)), int(tongue_width))
        
        # Draw snake tail
        tail_size = int(board.tile * 0.25)
        pygame.draw.circle(surface, settings.COLOR_SNAKE, (int(e_coord[0]), int(e_coord[1])), tail_size)
        pygame.draw.circle(surface, settings.COLOR_SNAKE_DARK, (int(e_coord[0]), int(e_coord[1])), tail_size, int(board.tile * 0.05))
