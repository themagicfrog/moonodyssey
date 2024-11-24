import pygame
import random
from player import Player
from game_objects import Potion, Wall
from constants import *

class Game:
    def __init__(self):
        pygame.init()
        self.fullscreen = False
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.FULLSCREEN_WIDTH = pygame.display.Info().current_w
        self.FULLSCREEN_HEIGHT = pygame.display.Info().current_h
        pygame.display.set_caption("Moon Explorer")
        self.clock = pygame.time.Clock()
        self.state = "STORY"
        self.mode = None
        self.game_start_time = 0
        self.current_time = 0
        self.high_scores = {'NORMAL': float('inf'), 'BLIND': float('inf')}
        self.story_page = 0
        self.fade_alpha = 255
        self.fade_speed = 2
        
        # Load images and font
        self.background = pygame.image.load("assets/background.png").convert()
        self.background = pygame.transform.scale(self.background, (WINDOW_WIDTH, WINDOW_HEIGHT))
        self.heart_img = pygame.image.load("assets/heart.png").convert_alpha()
        self.heart_img = pygame.transform.scale(self.heart_img, (30, 30))
        self.star_img = pygame.image.load("assets/potion2.png").convert_alpha()
        self.star_img = pygame.transform.scale(self.star_img, (40, 40))
        
        # Load pixel font with smaller sizes
        try:
            self.pixel_font = pygame.font.Font("assets/pixel_font.ttf", 54)
            self.pixel_font_small = pygame.font.Font("assets/pixel_font.ttf", 24)
            self.pixel_font_tiny = pygame.font.Font("assets/pixel_font.ttf", 20)
        except:
            print("Pixel font not found! Please add pixel_font.ttf to assets folder")
            self.pixel_font = pygame.font.Font(None, 54)
            self.pixel_font_small = pygame.font.Font(None, 24)
            self.pixel_font_tiny = pygame.font.Font(None, 20)
        
        # Load additional images
        self.moon_img = pygame.image.load("assets/background.png").convert()
        self.moon_img = pygame.transform.scale(self.moon_img, (200, 200))
        
        self.reset_game()
        self.heart_flash_timer = 0
        self.heart_visible = True

    def reset_game(self):
        """Reset the game state"""
        # Store previous state
        old_walls = self.walls if hasattr(self, 'walls') else []
        
        # Clear all lists first
        self.potions = []
        self.walls = []
        self.game_over = False
        self.won = False
        self.lives = 1
        self.stars_collected = 0
        
        # Create new walls in different positions from old ones
        while len(self.walls) < 10:
            x = random.randint(0, WINDOW_WIDTH - WALL_SIZE)
            y = random.randint(0, WINDOW_HEIGHT - WALL_SIZE)
            
            # Check if new wall position overlaps with old walls
            new_rect = pygame.Rect(x, y, WALL_SIZE, WALL_SIZE)
            overlap = False
            for old_wall in old_walls:
                if new_rect.colliderect(old_wall.rect):
                    overlap = True
                    break
            
            if not overlap:
                self.walls.append(Wall(x, y))
        
        # Always spawn player in center
        spawn_x = WINDOW_WIDTH // 2 - PLAYER_SIZE // 2
        spawn_y = WINDOW_HEIGHT // 2 - PLAYER_SIZE // 2
        
        # Check if center spawn is valid (not colliding with walls)
        spawn_rect = pygame.Rect(spawn_x, spawn_y, PLAYER_SIZE, PLAYER_SIZE)
        
        if spawn_rect.collidelist(self.walls) == -1:
            self.player = Player(spawn_x, spawn_y)
        else:
            # If center is blocked, find nearest valid position
            player_placed = False
            for offset in range(0, max(WINDOW_WIDTH, WINDOW_HEIGHT), 10):
                if player_placed:
                    break
                for dx, dy in [(0,offset), (0,-offset), (offset,0), (-offset,0)]:
                    test_x = spawn_x + dx
                    test_y = spawn_y + dy
                    if (0 <= test_x <= WINDOW_WIDTH - PLAYER_SIZE and 
                        0 <= test_y <= WINDOW_HEIGHT - PLAYER_SIZE):
                        test_rect = pygame.Rect(test_x, test_y, PLAYER_SIZE, PLAYER_SIZE)
                        if test_rect.collidelist(self.walls) == -1:
                            self.player = Player(test_x, test_y)
                            player_placed = True
                            break
        
        # Create potions last
        self.create_potions()
        
        # Reset game timer
        self.game_start_time = pygame.time.get_ticks()
        self.current_time = self.game_start_time

    def create_walls(self):
        if self.mode == "HARD":
            # Create border obstacles
            for _ in range(10):
                side = random.randint(0, 3)
                if side == 0:  # Top
                    x = random.randint(0, WINDOW_WIDTH)
                    y = random.randint(0, 100)
                elif side == 1:  # Right
                    x = WINDOW_WIDTH - 50
                    y = random.randint(0, WINDOW_HEIGHT)
                elif side == 2:  # Bottom
                    x = random.randint(0, WINDOW_WIDTH)
                    y = WINDOW_HEIGHT - 50
                else:  # Left
                    x = 0
                    y = random.randint(0, WINDOW_HEIGHT)
                self.walls.append(Wall(x, y))
            
            # Create obstacle clusters
            for _ in range(CLUSTER_COUNT):
                center_x = random.randint(WALL_SIZE_MAX, WINDOW_WIDTH - WALL_SIZE_MAX)
                center_y = random.randint(WALL_SIZE_MAX, WINDOW_HEIGHT - WALL_SIZE_MAX)
                
                for _ in range(OBSTACLES_PER_CLUSTER):
                    offset_x = random.randint(-WALL_SIZE_MAX*2, WALL_SIZE_MAX*2)
                    offset_y = random.randint(-WALL_SIZE_MAX*2, WALL_SIZE_MAX*2)
                    x = min(max(center_x + offset_x, 0), WINDOW_WIDTH - WALL_SIZE_MAX)
                    y = min(max(center_y + offset_y, 0), WINDOW_HEIGHT - WALL_SIZE_MAX)
                    self.walls.append(Wall(x, y))
        
        for _ in range(13):
            x = random.randint(0, WINDOW_WIDTH - WALL_SIZE_MAX)
            y = random.randint(0, WINDOW_HEIGHT - WALL_SIZE_MAX)
            self.walls.append(Wall(x, y))

    def create_potions(self):
        """Create collectible potions/stars"""
        attempts = 0
        max_attempts = 100  # Prevent infinite loop
        
        while len(self.potions) < 3 and attempts < max_attempts:
            x = random.randint(0, WINDOW_WIDTH - POTION_SIZE)
            y = random.randint(0, WINDOW_HEIGHT - POTION_SIZE)
            new_potion = Potion(x, y)
            
            # Check if position is valid
            valid_position = True
            
            # Check distance from walls
            for wall in self.walls:
                if wall.rect.colliderect(new_potion.rect):
                    valid_position = False
                    break
            
            # Check distance from other potions
            for potion in self.potions:
                dx = x - potion.rect.x
                dy = y - potion.rect.y
                if (dx * dx + dy * dy) ** 0.5 < MIN_STAR_DISTANCE:
                    valid_position = False
                    break
            
            if valid_position:
                self.potions.append(new_potion)
            
            attempts += 1

    def draw_lives(self):
        current_time = pygame.time.get_ticks()
        if self.heart_flash_timer > current_time:
            if (current_time // 100) % 2:  # Flash every 100ms
                return
        
        # Draw hearts
        for i in range(self.lives):
            self.screen.blit(self.heart_img, (10 + i * 35, 10))
        
        # Draw life counter
        text = self.pixel_font_tiny.render(f'Lives: {self.lives}/1', True, (255, 255, 255))
        self.screen.blit(text, (50, 15))

    def draw_light_circle(self):
        # Create a black surface for the darkness
        darkness = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        darkness.fill((0, 0, 0))  # Fill with black
        
        # Create a circle of light (reduced radius from 150 to 100)
        light_radius = 100  # Smaller light circle
        center = (self.player.rect.centerx, self.player.rect.centery)
        
        # Cut out a transparent circle where the player is
        pygame.draw.circle(darkness, (0, 0, 0, 0),  # Transparent
                          center, light_radius)
        
        # Set the alpha for the darkness (255 is completely opaque)
        darkness.set_alpha(245)  # Almost completely dark
        
        return darkness

    def draw_stars_collected(self):
        # Draw counter
        text = self.pixel_font_tiny.render(f'Stars: {self.stars_collected}/3', True, (255, 255, 255))
        text_x = WINDOW_WIDTH - text.get_width() - 10
        self.screen.blit(text, (text_x, 10))
        
        # Draw collected stars with more spacing
        for i in range(self.stars_collected):
            star_x = text_x - (i + 1) * 50 - 20
            self.screen.blit(self.star_img, (star_x, 5))

    def draw_mode_select(self):
        # Title
        title = self.pixel_font.render('Moon Odyssey', True, (255, 255, 255))
        self.screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 100))
        
        # Creator credit
        credit = self.pixel_font_tiny.render('Created by Estella Gu', True, (255, 255, 255))
        self.screen.blit(credit, (WINDOW_WIDTH//2 - credit.get_width()//2, 160))
        
        button_width = 400  # Increased width
        button_height = 80  # Increased height
        
        buttons = []
        modes = ['Limited Light (press 1)', 'No Light (press 2)']
        for i, mode in enumerate(modes):
            rect = pygame.Rect(WINDOW_WIDTH//2 - button_width//2, 250 + i*100, button_width, button_height)
            pygame.draw.rect(self.screen, (70, 70, 70), rect)
            text = self.pixel_font_small.render(mode, True, (255, 255, 255))
            self.screen.blit(text, (WINDOW_WIDTH//2 - text.get_width()//2, 
                           250 + i*100 + button_height//2 - text.get_height()//2))
            buttons.append(rect)
        
        # Draw high scores
        start_y = 450
        for mode in ['NORMAL', 'BLIND']:
            score_text = f"Best {mode}: "
            if self.high_scores[mode] == float('inf'):
                score_text += "No record"
            else:
                score_text += f"{self.high_scores[mode]:.1f}s"
            score = self.pixel_font_tiny.render(score_text, True, (255, 255, 0))
            self.screen.blit(score, (WINDOW_WIDTH//2 - score.get_width()//2, start_y))
            start_y += 30
        
        return buttons

    def draw_game_indicators(self):
        """Draw game HUD (lives, time, stars)"""
        # Create background for indicators
        indicator_bg = pygame.Surface((300, 40))
        indicator_bg.fill((0, 0, 0))
        indicator_bg.set_alpha(180)
        
        # Position at top center
        bg_rect = indicator_bg.get_rect(midtop=(WINDOW_WIDTH//2, 5))
        self.screen.blit(indicator_bg, bg_rect)
        
        # Draw lives
        self.screen.blit(self.heart_img, (bg_rect.left + 20, 10))
        lives_text = self.pixel_font_tiny.render(f'{self.lives}/1', True, (255, 255, 255))
        self.screen.blit(lives_text, (bg_rect.left + 55, 15))
        
        # Draw timer
        elapsed_time = (self.current_time - self.game_start_time) / 1000
        timer_text = self.pixel_font_tiny.render(f'{elapsed_time:.1f}s', True, (255, 255, 255))
        self.screen.blit(timer_text, (bg_rect.centerx - timer_text.get_width()//2, 15))
        
        # Draw stars collected
        self.screen.blit(self.star_img, (bg_rect.right - 60, 5))
        stars_text = self.pixel_font_tiny.render(f'{self.stars_collected}/3', True, (255, 255, 255))
        self.screen.blit(stars_text, (bg_rect.right - 30, 15))

    def run(self):
        running = True
        while running:
            self.screen.blit(self.background, (0, 0))
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F11:
                        self.toggle_fullscreen()
                    elif event.key == pygame.K_ESCAPE and self.fullscreen:
                        self.toggle_fullscreen()
                    elif event.key == pygame.K_SPACE:
                        if self.state == "STORY":
                            self.story_page += 1
                            self.fade_alpha = 255
                            if self.story_page >= len(STORY_TEXTS):
                                self.state = "MODE"
                        elif self.state == "MODE_INSTRUCTIONS":
                            self.state = "GAME"
                            self.reset_game()
                    elif self.state == "MODE":
                        if event.key == pygame.K_1:
                            self.mode = "NORMAL"
                            self.state = "GAME"
                            self.reset_game()
                        elif event.key == pygame.K_2:
                            self.mode = "BLIND"
                            self.state = "GAME"
                            self.reset_game()
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.state == "STORY":
                        self.story_page += 1
                        self.fade_alpha = 255
                        if self.story_page >= len(STORY_TEXTS):
                            self.state = "MODE"
                    mouse_pos = pygame.mouse.get_pos()
                    
                    if self.state == "MENU":
                        play_rect, inst_rect = self.draw_menu()
                        if play_rect.collidepoint(mouse_pos):
                            self.state = "MODE"
                        elif inst_rect.collidepoint(mouse_pos):
                            self.state = "INSTRUCTIONS"
                    
                    elif self.state == "MODE":
                        buttons = self.draw_mode_select()
                        for i, button in enumerate(buttons):
                            if button.collidepoint(mouse_pos):
                                self.mode = ["NORMAL", "BLIND"][i]
                                self.state = "GAME"
                                self.reset_game()
                    
                    elif self.state == "GAME" and (self.game_over or self.won):
                        if hasattr(self, 'restart_rect') and self.restart_rect.collidepoint(mouse_pos):
                            self.state = "MODE"  # Go back to mode selection
                            self.story_page = 0
                            continue
                
                if event.type == pygame.KEYDOWN and self.state == "INSTRUCTIONS":
                    if event.key == pygame.K_SPACE:
                        self.state = "MENU"

            if self.state == "STORY":
                self.draw_story()
            elif self.state == "MENU":
                self.draw_menu()
            elif self.state == "MODE":
                self.draw_mode_select()
            elif self.state == "INSTRUCTIONS":
                self.draw_instructions()
            elif self.state == "GAME":
                self.run_game()

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

    def run_game(self):
        if not self.game_over and not self.won:
            self.current_time = pygame.time.get_ticks()
            self.player.update(self.walls)
            
            if self.player.check_lava_collision():
                self.lives -= 1
                self.heart_flash_timer = pygame.time.get_ticks() + 1000
                if self.lives <= 0:
                    self.game_over = True
                else:
                    self.player.start_invulnerability()
                    self.player.lava_trail.clear()

            for potion in self.potions[:]:
                if self.player.rect.colliderect(potion.collision_rect):
                    self.potions.remove(potion)
                    self.stars_collected += 1
                    if self.stars_collected >= 3:
                        self.won = True

        # Drawing
        self.screen.blit(self.background, (0, 0))
        
        if self.mode == "NORMAL":
            # Draw all game elements first
            for wall in self.walls:
                wall.draw(self.screen)
            self.player.draw_lava(self.screen)
            for potion in self.potions:
                potion.draw(self.screen)
            self.player.draw_player(self.screen)
            
            # Apply the darkness with light circle last
            self.screen.blit(self.draw_light_circle(), (0, 0))
        else:
            # Blind mode - complete darkness except player and stars
            darkness = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            darkness.fill((0, 0, 0))
            
            # Draw player and stars on top of darkness
            self.player.draw_player(self.screen)  # Draw only player, not lava
            for potion in self.potions:
                potion.draw(self.screen)
                
            # Make everything else black
            darkness.set_alpha(240)
            self.screen.blit(darkness, (0, 0))
            
            # Redraw player and stars to ensure they're visible
            self.player.draw_player(self.screen)
            for potion in self.potions:
                potion.draw(self.screen)

        self.draw_game_indicators()

        if self.game_over:
            self.draw_game_over()
        elif self.won:
            final_time = (self.current_time - self.game_start_time) / 1000
            if final_time < self.high_scores[self.mode]:
                self.high_scores[self.mode] = final_time
            self.draw_win_screen()

    def draw_game_over(self):
        # Show full screen without darkness
        self.screen.blit(self.background, (0, 0))
        for wall in self.walls:
            wall.draw(self.screen)
        self.player.draw_lava(self.screen)
        self.player.draw_player(self.screen)
        for potion in self.potions:
            potion.draw(self.screen)
        
        # Create semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(160)  # More transparent overlay
        self.screen.blit(overlay, (0, 0))
        
        # Draw text with larger margins
        margin = 150
        text_width = WINDOW_WIDTH - (margin * 2)
        
        # Game over text
        text1 = self.pixel_font.render('Game Over!', True, TEXT_COLOR_LOSE)
        self.screen.blit(text1, (WINDOW_WIDTH//2 - text1.get_width()//2, WINDOW_HEIGHT//3))
        
        # Draw lose message
        text2 = self.pixel_font_small.render("You are your own enemy!", True, TEXT_COLOR_LOSE)
        self.screen.blit(text2, (WINDOW_WIDTH//2 - text2.get_width()//2, WINDOW_HEIGHT//2))
        
        self.restart_rect = self.draw_restart_button(WINDOW_HEIGHT * 3//4)

    def draw_win_screen(self):
        # Show full screen without darkness
        self.screen.blit(self.background, (0, 0))
        for wall in self.walls:
            wall.draw(self.screen)
        self.player.draw_lava(self.screen)
        self.player.draw_player(self.screen)
        for potion in self.potions:
            potion.draw(self.screen)
        
        # Create semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(160)  # More transparent overlay
        self.screen.blit(overlay, (0, 0))
        
        # Draw win text
        text1 = self.pixel_font.render("You Win!", True, TEXT_COLOR_WIN)
        self.screen.blit(text1, (WINDOW_WIDTH//2 - text1.get_width()//2, WINDOW_HEIGHT//3))
        
        # Draw message
        text2 = self.pixel_font_small.render("Congrats, you've saved humanity!", True, TEXT_COLOR_WIN)
        self.screen.blit(text2, (WINDOW_WIDTH//2 - text2.get_width()//2, WINDOW_HEIGHT//2))
        
        self.restart_rect = self.draw_restart_button(WINDOW_HEIGHT * 3//4)

    def draw_restart_button(self, y_position):
        button_width = 160
        button_height = 50
        button_x = WINDOW_WIDTH//2 - button_width//2
        
        button_rect = pygame.Rect(button_x, y_position, button_width, button_height)
        
        # Draw button
        pygame.draw.rect(self.screen, BUTTON_COLOR, button_rect)
        pygame.draw.rect(self.screen, (100, 100, 100), 
                        (button_x, y_position, button_width, button_height-5))
        pygame.draw.rect(self.screen, (120, 120, 120), 
                        button_rect, 2)
        
        # Draw text
        text = self.pixel_font_small.render('Restart', True, (255, 255, 255))
        text_rect = text.get_rect(center=button_rect.center)
        self.screen.blit(text, text_rect)
        
        return button_rect

    def draw_story(self):
        self.screen.fill((0, 0, 0))
        
        # Create semi-transparent background for text
        text_bg = pygame.Surface((700, 200))
        text_bg.fill((0, 0, 0))
        text_bg.set_alpha(180)
        
        # Position story elements based on page
        if self.story_page == 0:
            # First page - show large astronaut with stars
            large_astronaut = pygame.transform.scale(self.player.image, (PLAYER_SIZE * 2, PLAYER_SIZE * 2))
            astronaut_pos = (WINDOW_WIDTH//2 - PLAYER_SIZE, WINDOW_HEIGHT//3 - PLAYER_SIZE)
            self.screen.blit(large_astronaut, astronaut_pos)
            
            # Draw stars on either side
            star_size = 80
            scaled_star = pygame.transform.scale(self.star_img, (star_size, star_size))
            self.screen.blit(scaled_star, (astronaut_pos[0] - star_size - 20, astronaut_pos[1]))
            self.screen.blit(scaled_star, (astronaut_pos[0] + PLAYER_SIZE * 2 + 20, astronaut_pos[1]))
            
        elif self.story_page == 1:
            # Second page - show larger lava
            large_lava = pygame.transform.scale(self.player.lava_image, (LAVA_SIZE * 2, LAVA_SIZE * 2))
            for i in range(5):
                lava_pos = (WINDOW_WIDTH//4 + i*100, WINDOW_HEIGHT//3)
                self.screen.blit(large_lava, lava_pos)
            
        else:  # Final page
            # Draw moon background
            moon_size = 300
            scaled_moon = pygame.transform.scale(self.moon_img, (moon_size, moon_size))
            self.screen.blit(scaled_moon, (WINDOW_WIDTH//2 - moon_size//2, WINDOW_HEIGHT//4))
            
            # Draw astronaut
            astronaut_pos = (WINDOW_WIDTH//2 - PLAYER_SIZE, WINDOW_HEIGHT//3)
            self.screen.blit(self.player.image, astronaut_pos)
            
            # Draw stars
            for i in range(3):
                star_pos = (WINDOW_WIDTH//4 + i*200, WINDOW_HEIGHT//3 - 50)
                self.screen.blit(self.star_img, star_pos)
            
            # Draw lava trail
            for i in range(3):
                lava_pos = (WINDOW_WIDTH//4 + i*150, WINDOW_HEIGHT//2 + 50)
                self.screen.blit(self.player.lava_image, lava_pos)
        
        # Draw text background
        text_bg_rect = text_bg.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 100))
        self.screen.blit(text_bg, text_bg_rect)
        
        # Draw text
        text = STORY_TEXTS[self.story_page]
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            current_line.append(word)
            test_line = ' '.join(current_line)
            if self.pixel_font_small.size(test_line)[0] > 600:
                lines.append(' '.join(current_line[:-1]))
                current_line = [word]
        lines.append(' '.join(current_line))
        
        for i, line in enumerate(lines):
            text_surface = self.pixel_font_small.render(line, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + i*30))
            self.screen.blit(text_surface, text_rect)
        
        # Draw continue prompt (space only)
        continue_text = self.pixel_font_tiny.render("Press SPACE to continue", True, (255, 255, 255))
        self.screen.blit(continue_text, (WINDOW_WIDTH//2 - continue_text.get_width()//2, WINDOW_HEIGHT - 100))
        
        # Apply fade effect
        if self.fade_alpha > 0:
            fade_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            fade_surface.fill((0, 0, 0))
            fade_surface.set_alpha(self.fade_alpha)
            self.screen.blit(fade_surface, (0, 0))
            self.fade_alpha = max(0, self.fade_alpha - self.fade_speed)

if __name__ == "__main__":
    game = Game()
    game.run() 