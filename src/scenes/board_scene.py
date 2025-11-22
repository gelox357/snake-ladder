import pygame
from src.core.scene import Scene
from src.config import settings
from src.core.board import Board
from src.core.player import Player
from src.objects.token import Token
from src.objects.dice import Dice
from src.objects.button import Button
from src.objects.status_bar import StatusBar
from src.objects.snake import Snake
from src.objects.ladder import Ladder
from src.objects.zombie import ZombieSnake
from src.objects.confetti import Confetti # Import Confetti
from src.ui.draw import vertical_gradient

class BoardScene(Scene):
    def __init__(self, game, names, player_images, sound_on, mode):
        super().__init__(game)
        self.board = Board(game.assets)
        self.players = []
        for i, n in enumerate(names):
            player_img_surface = None
            if player_images and i < len(player_images) and player_images[i]:
                player_img_surface = pygame.transform.scale(player_images[i], (settings.TILE_SIZE // 2, settings.TILE_SIZE // 2))
            else:
                # Fallback to a default token image if no custom image or if it failed to load
                default_token = game.assets.image("token", (settings.TILE_SIZE // 2, settings.TILE_SIZE // 2))
                player_img_surface = default_token
            self.players.append(Player(n, settings.PLAYER_COLORS[i % len(settings.PLAYER_COLORS)], player_img_surface))
        
        self.turn = 0
        self.dice = Dice(game.assets)
        self.font = game.assets.font(settings.FONT_REGULAR, 18)
        self.big_font = game.assets.font(settings.FONT_BOLD, 24)
        self.status = StatusBar((130, 820, 700, 45), settings.COLOR_STATUS_BG1, settings.COLOR_STATUS_BG2, self.big_font)
        
        self.roll_btn = Button((130, 880, 120, 44), settings.COLOR_BUTTON_ROLL, self.big_font.render("Roll", True, settings.COLOR_BUTTON_TEXT))
        self.pause_btn = Button((260, 880, 120, 44), settings.COLOR_BUTTON_PAUSE, self.big_font.render("Pause", True, settings.COLOR_BUTTON_TEXT))
        self.resume_btn = Button((260, 880, 120, 44), settings.COLOR_BUTTON_RESUME, self.big_font.render("Resume", True, settings.COLOR_BUTTON_TEXT))
        self.save_btn = Button((390, 880, 120, 44), settings.COLOR_BUTTON_SAVE, self.big_font.render("Save", True, settings.COLOR_BUTTON_TEXT))
        self.restart_btn = Button((520, 880, 120, 44), settings.COLOR_BUTTON_RESTART, self.big_font.render("Restart", True, settings.COLOR_BUTTON_TEXT))
        self.menu_btn = Button((650, 880, 120, 44), settings.COLOR_BUTTON_MENU, self.big_font.render("Menu", True, settings.COLOR_BUTTON_TEXT))
        
        self.dice_rect = pygame.Rect(30, 820, 80, 80)
        self.sound_on = sound_on
        self.mode = mode
        self.winner = None
        
        self.snakes = [Snake(h, t) for h, t in settings.SNAKES.items()]
        self.ladders = [Ladder(b, a) for b, a in settings.LADDERS.items()]
        self.zombie = ZombieSnake(self.board, self.game.assets) # Keep zombie for now, can remove if not needed
        self.last_dice_face = None
        self.zombie_frozen = True # Keep zombie frozen by default
        self.show_zombie = False # Don't show zombie by default
        
        # Timed mode variables
        self.timed_total_seconds = settings.TIMED_MODE_DURATION # Default 2 minutes
        self.timed_remaining = self.timed_total_seconds
        self.timed_interval = None
        self.timer_font = game.assets.font(settings.FONT_BOLD, 20)

        # Endless mode variables
        self.endless_scores = [0] * len(self.players)
        self.confetti_particles = [] # Initialize confetti particles list

        self.status.set_text(f"Player {self.turn+1} to roll")
        self.start_mode_logic()

    def start_mode_logic(self):
        if self.mode == 'timed':
            self.start_timed_countdown()
        elif self.mode == 'endless':
            self.endless_scores = [0] * len(self.players)
            self.update_scores_ui()

    def stop_mode_logic(self):
        if self.mode == 'timed':
            self.stop_timed_countdown()

    def start_timed_countdown(self):
        self.stop_timed_countdown()
        self.timed_remaining = self.timed_total_seconds
        self.timed_interval = pygame.time.set_timer(pygame.USEREVENT + 1, 1000) # 1 second interval

    def stop_timed_countdown(self):
        if self.timed_interval:
            pygame.time.set_timer(pygame.USEREVENT + 1, 0) # Stop the timer
            self.timed_interval = None

    def update_scores_ui(self):
        # This will be implemented when we have a proper UI for scores
        pass

    def handle(self, event):
        if self.roll_btn.handle(event):
            if not self.winner and not self.game.paused:
                self.dice.start()
        if self.pause_btn.handle(event):
            self.game.paused = True
        if self.resume_btn.handle(event):
            self.game.paused = False
        if self.save_btn.handle(event):
            self.game.save_state(self.serialize())
        if self.restart_btn.handle(event):
            self.stop_mode_logic()
            self.__init__(self.game, [p.name for p in self.players], self.sound_on, self.mode)
        if self.menu_btn.handle(event):
            self.stop_mode_logic()
            self.game.goto_menu()
        
        if self.mode == 'timed' and event.type == pygame.USEREVENT + 1:
            if not self.game.paused:
                self.timed_remaining -= 1
                if self.timed_remaining <= 0:
                    self.stop_timed_countdown()
                    self.handle_timed_mode_end()

    def handle_timed_mode_end(self):
        # Determine winner based on highest position
        best_idx = 0
        for i in range(1, len(self.players)):
            if self.players[i].square > self.players[best_idx].square:
                best_idx = i
        self.winner = self.players[best_idx]
        self.status.set_text(f"⏰ Time's up! {self.winner.name} wins with {self.winner.square}!")
        # Play win sound and confetti (to be implemented)
        self.game.paused = True # Prevent further rolls

    def update(self, dt):
        if self.game.paused:
            return
        
        done = self.dice.update(dt)
        if done:
            steps = self.dice.face
            self.last_dice_face = steps
            p = self.players[self.turn]
            
            # Apply power-ups/downs before moving
            # This logic needs to be more integrated with the board and player movement
            # For now, just a placeholder
            # if p.doubleNext: steps *= 2; p.doubleNext = False
            # elif p.halfNext: steps = max(1, steps // 2); p.halfNext = False

            p.enqueue_steps(steps)
            if not self.zombie_frozen:
                self.zombie.enqueue_steps(steps)
            
            if self.sound_on:
                s = self.game.assets.sound("roll")
                if s: s.play()

        p = self.players[self.turn]
        moved = p.step()
        if moved:
            p.advance_anim(dt)
            if self.sound_on:
                s = self.game.assets.sound("step")
                if s: s.play()
        else:
            before = p.square
            new, kind = self.board.apply_collision(p.square)
            
            # Handle snakes and ladders
            if kind == "snake":
                if p.skipSnake:
                    p.skipSnake = False
                    self.status.set_text(f"{p.name} avoided a snake!")
                else:
                    p.snake_hits += 1
                    p.square = new
                    for s in self.snakes:
                        if s.head_square == before and s.tail_square == new:
                            s.trigger_eat()
                    self.status.set_text(f"{p.name} hit a snake: {before} → {new}")
                    if self.sound_on:
                        s = self.game.assets.sound("snake")
                        if s: s.play()
            elif kind == "ladder":
                p.climbed += max(0, new - p.square)
                p.square = new
                self.status.set_text(f"{p.name} climbed a ladder: {before} → {new}")
                if self.sound_on:
                    s = self.game.assets.sound("ladder")
                    if s: s.play()
            elif kind == "power_up":
                power_up_type = self.board.special_tiles["powerUps"][p.square]["type"]
                self.status.set_text(f"{p.name} got a Power Up: {settings.POWER_UP_TEXTS[power_up_type]}!")
                if power_up_type == 'forward5':
                    p.square = min(100, p.square + 5)
                    self.status.set_text(f"{p.name} moved 5 spaces forward!")
            elif kind == "power_down":
                power_down_type = self.board.special_tiles["powerDowns"][p.square]["type"]
                self.status.set_text(f"{p.name} got a Power Down: {settings.POWER_DOWN_TEXTS[power_down_type]}!")
                if power_down_type == 'backward6':
                    p.square = max(1, p.square - 6)
                    self.status.set_text(f"{p.name} moved 6 spaces backward!")
                elif power_down_type == 'loseTurn':
                    p.loseTurn = True
                    self.status.set_text(f"{p.name} loses next turn!")

            if p.square == 100:
                self.winner = p
                self.status.set_text(f"🎉 {p.name} WINS! 🎉")
                if self.sound_on:
                    s = self.game.assets.sound("win")
                    if s: s.play()
                self.launch_confetti() # Launch confetti
                self.stop_mode_logic()
                self.game.paused = True
                
                if self.mode == 'endless':
                    self.endless_scores[self.turn] += 1
                    self.update_scores_ui()
                    for player_reset in self.players:
                        player_reset.square = 1
                    self.status.set_text(f"Round scored! {p.name} to play next.")
                    pygame.time.set_timer(pygame.USEREVENT + 2, 800) # Delay for 0.8 seconds
                    
            else:
                if p.loseTurn:
                    p.loseTurn = False
                    self.status.set_text(f"{p.name} lost a turn. Next: {self.players[(self.turn + 1) % len(self.players)].name}")
                else:
                    self.turn = (self.turn + 1) % len(self.players)
                    self.status.set_text(f"Next: {self.players[self.turn].name}")

    def render(self, surface):
        vertical_gradient(surface, (0,0,self.game.width,self.game.height), settings.COLOR_BG_TOP, settings.COLOR_BG_BOTTOM)
        self.board.render(surface, self.font)
        for l in self.ladders:
            l.draw(surface, self.board)
        for s in self.snakes:
            s.draw(surface, self.board) # Draw snakes
        
        if not self.zombie_frozen and self.show_zombie:
            self.zombie.update(self.game.clock.get_time()/1000.0)
            self.zombie.draw(surface)
        
        for p in self.players:
            p.advance_anim(self.game.clock.get_time()/1000.0)
            a = self.board.square_pos(p.anim_from)
            b = self.board.square_pos(p.anim_to)
            x = a[0] + (b[0] - a[0]) * p.anim_t
            y = a[1] + (b[1] - a[1]) * p.anim_t
            
            # Draw player image instead of generic token
            # Assuming player.image is a pygame.Surface
            if p.image:
                img_rect = p.image.get_rect(center=(x, y))
                surface.blit(p.image, img_rect)
            else:
                # Fallback to generic token if no image
                Token(self.game.assets.image("token", (32,32)), p.color).draw(surface, (x, y))
        
        self.dice.draw(surface, self.dice_rect)
        self.status.draw(surface, settings.COLOR_TEXT)
        
        self.roll_btn.draw(surface)
        if self.game.paused:
            self.resume_btn.draw(surface)
        else:
            self.pause_btn.draw(surface)
        self.save_btn.draw(surface)
        self.restart_btn.draw(surface)
        self.menu_btn.draw(surface)
        
        if self.last_dice_face is not None:
            overlay = self.big_font.render(f"Dice: {self.last_dice_face}", True, (255,255,255))
            r = overlay.get_rect(center=(self.game.width//2, 60))
            surface.blit(overlay, r)

        # Render timed mode timer
        if self.mode == 'timed':
            timer_text = self.timer_font.render(self.format_time(self.timed_remaining), True, settings.COLOR_TEXT)
            timer_rect = timer_text.get_rect(center=(self.game.width - 100, 60))
            surface.blit(timer_text, timer_rect)
        
        # Render endless mode scores
        if self.mode == 'endless':
            score_y_start = 100
            for i, score in enumerate(self.endless_scores):
                score_text = self.font.render(f"{self.players[i].name}: {score}", True, settings.COLOR_TEXT)
                score_rect = score_text.get_rect(topright=(self.game.width - 20, score_y_start + i * 25))
                surface.blit(score_text, score_rect)

        # Update and draw confetti
        for particle in list(self.confetti_particles):
            particle.update(self.game.clock.get_time()/1000.0)
            if particle.alpha <= 0 or particle.y > self.game.height:
                self.confetti_particles.remove(particle)
            else:
                particle.draw(surface)

    def format_time(self, seconds):
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02}:{seconds:02}"

    def launch_confetti(self):
        for _ in range(60):
            x = random.randint(0, self.game.width)
            y = random.randint(-50, 0)
            color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            size = random.randint(5, 13)
            speed = random.uniform(0.5, 1.5)
            self.confetti_particles.append(Confetti(x, y, color, size, speed))
