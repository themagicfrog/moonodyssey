import pygame
from constants import *

class Player:
    """Represents the player character (astronaut)"""
    def __init__(self, x, y):
        # Load and scale player image
        self.image = pygame.image.load("assets/astronaut.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (PLAYER_SIZE, PLAYER_SIZE))
        self.rect = self.image.get_rect(x=x, y=y)
        
        # Load and scale lava image
        self.lava_image = pygame.image.load("assets/lava.png").convert_alpha()
        self.lava_image = pygame.transform.scale(self.lava_image, (LAVA_SIZE, LAVA_SIZE))
        
        # Player properties
        self.speed = 5
        self.lava_trail = []
        self.invulnerable = False
        self.invulnerable_timer = 0
        self.visible = True

    def update(self, walls):
        """Update player position and handle movement"""
        keys = pygame.key.get_pressed()
        old_pos = self.rect.copy()
        moved = False

        # Handle movement
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: 
            self.rect.x -= self.speed
            moved = True
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: 
            self.rect.x += self.speed
            moved = True
        if keys[pygame.K_UP] or keys[pygame.K_w]: 
            self.rect.y -= self.speed
            moved = True
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: 
            self.rect.y += self.speed
            moved = True

        # Keep player in bounds
        self.rect.clamp_ip(pygame.Rect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT))

        # Check wall collisions
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                self.rect = old_pos
                moved = False
                break

        # Add lava trail if moved
        if moved and not self.invulnerable:
            self.add_lava_trail()

    def start_invulnerability(self):
        """Start invulnerability period"""
        self.invulnerable = True
        self.invulnerable_timer = pygame.time.get_ticks() + 1000  # 1 second

    def add_lava_trail(self):
        """Add new lava piece to trail"""
        center = self.rect.center
        lava_pos = (center[0] - LAVA_SIZE//2, center[1] - LAVA_SIZE//2)
        
        if not self.lava_trail or self.distance_to_last_lava(center[0], center[1]) > LAVA_SPACING:
            self.lava_trail.append(lava_pos)

    def check_lava_collision(self):
        """Check if player hits their own lava trail"""
        if len(self.lava_trail) <= 10:  # Ignore if trail is too short
            return False
            
        player_center = self.rect.inflate(-PLAYER_SIZE//2, -PLAYER_SIZE//2)
        
        for lava_pos in self.lava_trail[:-10]:  # Ignore last 10 pieces
            lava_rect = pygame.Rect(lava_pos[0], lava_pos[1], LAVA_SIZE, LAVA_SIZE)
            if player_center.colliderect(lava_rect):
                return True
        return False

    def draw_lava(self, screen):
        """Draw only the lava trail"""
        for pos in self.lava_trail:
            screen.blit(self.lava_image, pos)

    def draw_player(self, screen):
        """Draw only the player"""
        if self.visible:
            screen.blit(self.image, self.rect)

    def draw(self, screen):
        """Draw both player and lava trail"""
        self.draw_lava(screen)
        self.draw_player(screen)

    def distance_to_last_lava(self, x, y):
        """Calculate distance to last lava piece"""
        if not self.lava_trail:
            return float('inf')
        last_lava = self.lava_trail[-1]
        return ((x - (last_lava[0] + LAVA_SIZE // 2)) ** 2 + 
                (y - (last_lava[1] + LAVA_SIZE // 2)) ** 2) ** 0.5 