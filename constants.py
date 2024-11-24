import pygame

# Window settings
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

# Game object sizes
PLAYER_SIZE = 60
POTION_SIZE = 60
WALL_SIZE = 40
LAVA_SIZE = 30
LAVA_SPACING = 20

# Game mechanics
MIN_STAR_DISTANCE = 150  # Minimum distance between stars
LIGHT_RADIUS = 100      # Size of light circle in normal mode
WALL_COUNT = 10         # Number of walls to create

# Game colors
TEXT_COLOR_LOSE = (255, 150, 150)  # Red
TEXT_COLOR_WIN = (150, 255, 150)   # Green
BUTTON_COLOR = (70, 70, 70)        # Dark gray

# Story text
STORY_TEXTS = [
    "You are an astronaut on a critical mission to retrieve magical stars from a mysterious moon.",
    "But beware! The ground beneath you is unstable. Where you walk the rocky surface crumbles away revealing deadly lava below.",
    "Large rocks will block your path, and darkness limits your vision. Be careful where you step - you are your own enemy! Good luck!"
]