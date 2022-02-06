import pygame

class Settings():
    """A class to store all settings for Alien Invasion."""

    def __init__(self):
        """Initialize the game's static settings."""
        # Screen settings
        self.screen_width = 1280
        self.screen_height = 720
        self.bg_color = (0, 0, 0)
        self.background = pygame.image.load("./assets/img/space2.jpg")
        # background = pygame.image.load(os.path.join('images', 'bg.png')).convert()
        # Make a copy of the backgound image
        self.bg_copy = self.background.copy()
        self.bgY = 0
        self.bgY2 = self.background.get_height() * -1
        self.bg_speed = 1
        # Set a clock
        self.clock = pygame.time.Clock()
        
        # Game over check variable
        self.game_over = False

        # Set game pace
        self.pace = 100

        #Ship settings
        self.ship_speed_factor = 1.5
        self.ship_limit = 3

        # Bullet settings
        self.bullet_speed_factor = 3
        self.bullet_width = 3
        self.bullet_height = 15
        self.bullet_color = (255, 195, 0)
        self.bullets_allowed = 5

        # Alien settings
        self.fleet_drop_speed = 15

        # How quickly the game speeds up
        self.speedup_scale = 1.1
        # How quikly the alien point values increase
        self.score_scale = 1.5

        self.initialize_dynamic_settings()

    def update_game_over(self):
        self.game_over = not self.game_over

    def initialize_dynamic_settings(self):
        """Initialize settings that change throughout the game."""
        self.ship_speed_factor = 6
        self.bullet_speed_factor = 6
        self.alien_speed_factor = 1.5

        # fleet_direction of 1 represents right; -1 represents left
        self.fleet_direction = 1

        # Scoring
        self.alien_points = 15
    
    def increase_speed(self):
        """Increase speed settings and alien point values."""
        self.pace *= self.speedup_scale
        self.ship_speed_factor *= self.speedup_scale
        self.bullet_speed_factor *= self.speedup_scale
        self.alien_speed_factor *= self.speedup_scale

        self.alien_points = int(self.alien_points * self.score_scale)
        print(self.alien_points)
