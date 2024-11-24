import pygame
from constants import *

class Potion:
    """Represents a collectible star/potion in the game"""
    def __init__(self, x, y):
        # Load and scale the image
        self.image = pygame.image.load("assets/potion2.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (POTION_SIZE, POTION_SIZE))
        self.rect = self.image.get_rect(x=x, y=y)
        
        # Create smaller collision rect for better gameplay
        shrink = 15
        self.collision_rect = self.rect.inflate(-shrink*2, -shrink*2)

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class Wall:
    """Represents an obstacle in the game"""
    def __init__(self, x, y):
        # Create wall rectangle
        self.rect = pygame.Rect(x, y, WALL_SIZE, WALL_SIZE)
        
        # Load and create circular wall image
        background = pygame.image.load("assets/background.png").convert()
        self.image = pygame.Surface((WALL_SIZE, WALL_SIZE), pygame.SRCALPHA)
        
        # Create circular mask
        pygame.draw.circle(self.image, (0, 0, 0, 180), 
                         (WALL_SIZE//2, WALL_SIZE//2), 
                         WALL_SIZE//2)
        
        # Create smaller collision rect
        shrink = 12
        self.collision_rect = self.rect.inflate(-shrink*2, -shrink*2)

    def draw(self, screen):
        screen.blit(self.image, self.rect)