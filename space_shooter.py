import pygame
import random
import sys
import math

# Initialize Pygame
pygame.init()

# Set up the display
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Space Shooter")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
DARK_RED = (200, 0, 0)
GRAY = (100, 100, 100)
DEEP_SPACE = (5, 5, 20)
NEBULA_COLOR = (30, 20, 50)

# Background
class Star:
    def __init__(self):
        self.x = random.randint(0, WINDOW_WIDTH)
        self.y = random.randint(0, WINDOW_HEIGHT)
        self.size = random.uniform(1, 3)
        self.brightness = random.uniform(0.3, 1.0)
        self.twinkle_speed = random.uniform(0.02, 0.05)
        self.twinkle_direction = 1

    def update(self):
        self.brightness += self.twinkle_speed * self.twinkle_direction
        if self.brightness >= 1.0:
            self.brightness = 1.0
            self.twinkle_direction = -1
        elif self.brightness <= 0.3:
            self.brightness = 0.3
            self.twinkle_direction = 1

    def draw(self, surface):
        color = (int(255 * self.brightness), 
                int(255 * self.brightness), 
                int(255 * self.brightness))
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.size)

class Nebula:
    def __init__(self):
        self.points = []
        self.num_points = 100
        self.generate_points()

    def generate_points(self):
        center_x = WINDOW_WIDTH // 2
        center_y = WINDOW_HEIGHT // 2
        for i in range(self.num_points):
            angle = (2 * math.pi * i) / self.num_points
            radius = random.uniform(100, 300)
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            self.points.append((x, y))

    def draw(self, surface):
        # Draw nebula background
        for i in range(len(self.points)):
            p1 = self.points[i]
            p2 = self.points[(i + 1) % len(self.points)]
            alpha = int(50 + 20 * math.sin(pygame.time.get_ticks() * 0.001 + i))
            color = (*NEBULA_COLOR, alpha)
            pygame.draw.line(surface, color, p1, p2, 2)

# Player Rocket
class Rocket:
    def __init__(self):
        self.width = 50
        self.height = 80
        self.x = WINDOW_WIDTH // 2 - self.width // 2
        self.y = WINDOW_HEIGHT - self.height - 20
        self.speed = 5
        self.bullets = []

    def move(self, direction):
        if direction == "left" and self.x > 0:
            self.x -= self.speed
        if direction == "right" and self.x < WINDOW_WIDTH - self.width:
            self.x += self.speed

    def shoot(self):
        bullet = Bullet(self.x + self.width // 2, self.y)
        self.bullets.append(bullet)

    def draw(self, screen):
        pygame.draw.rect(screen, WHITE, (self.x, self.y, self.width, self.height))

# Bullet
class Bullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 7
        self.radius = 5

    def move(self):
        self.y -= self.speed

    def draw(self, screen):
        pygame.draw.circle(screen, WHITE, (self.x, self.y), self.radius)

# Debris
class Debris:
    def __init__(self, speed_multiplier=1.0):
        self.size = random.randint(25, 40)  # Size of the asteroid
        self.x = random.randint(0, WINDOW_WIDTH - self.size)
        self.y = -self.size
        self.base_speed = random.randint(2, 5)
        self.speed = self.base_speed * speed_multiplier
        self.rotation = random.randint(0, 360)
        self.rotation_speed = random.uniform(-2, 2)
        
        # Generate random points for the asteroid shape
        self.points = self.generate_asteroid_shape()
        self.holes = self.generate_holes()
        
        # Calculate bounding box for collision detection
        self.width = self.size
        self.height = self.size

    def generate_asteroid_shape(self):
        points = []
        num_points = random.randint(8, 12)
        for i in range(num_points):
            angle = (2 * math.pi * i) / num_points
            # Add some randomness to the radius
            radius = self.size/2 * random.uniform(0.8, 1.2)
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            points.append((x, y))
        return points

    def generate_holes(self):
        holes = []
        num_holes = random.randint(1, 3)
        for _ in range(num_holes):
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(0, self.size/3)
            x = distance * math.cos(angle)
            y = distance * math.sin(angle)
            radius = random.uniform(3, 8)
            holes.append((x, y, radius))
        return holes

    def move(self):
        self.y += self.speed
        self.rotation += self.rotation_speed

    def draw(self, screen):
        # Create a surface for the asteroid
        asteroid_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        
        # Draw the main asteroid shape
        rotated_points = []
        for x, y in self.points:
            # Rotate points
            angle_rad = math.radians(self.rotation)
            rotated_x = x * math.cos(angle_rad) - y * math.sin(angle_rad)
            rotated_y = x * math.sin(angle_rad) + y * math.cos(angle_rad)
            # Center the points
            rotated_points.append((rotated_x + self.size, rotated_y + self.size))
        
        # Draw the main asteroid body
        pygame.draw.polygon(asteroid_surface, GRAY, rotated_points)
        pygame.draw.polygon(asteroid_surface, DARK_RED, rotated_points, 2)
        
        # Draw the holes
        for hole_x, hole_y, radius in self.holes:
            # Rotate hole positions
            angle_rad = math.radians(self.rotation)
            rotated_hole_x = hole_x * math.cos(angle_rad) - hole_y * math.sin(angle_rad)
            rotated_hole_y = hole_x * math.sin(angle_rad) + hole_y * math.cos(angle_rad)
            # Center the holes
            pygame.draw.circle(asteroid_surface, BLACK, 
                             (int(rotated_hole_x + self.size), 
                              int(rotated_hole_y + self.size)), 
                             int(radius))
        
        # Draw the asteroid surface on the screen
        screen.blit(asteroid_surface, 
                   (self.x - self.size//2, self.y - self.size//2))

# Game setup
rocket = Rocket()
debris_list = []
score = 0
clock = pygame.time.Clock()
spawn_timer = 0
game_time = 0
difficulty_level = 1
speed_multiplier = 1.0
spawn_interval = 60  # Initial spawn interval in frames

# Create background elements
stars = [Star() for _ in range(200)]  # Create 200 stars
nebula = Nebula()

# Create a surface for the background
background_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
background_surface.fill(DEEP_SPACE)

# Game loop
running = True
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                rocket.shoot()

    # Get keyboard state
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        rocket.move("left")
    if keys[pygame.K_RIGHT]:
        rocket.move("right")

    # Update game time and difficulty
    game_time += 1
    if game_time % (30 * 60) == 0:  # Every 30 seconds (60 frames per second)
        difficulty_level += 1
        speed_multiplier += 0.2  # Increase speed by 20%
        spawn_interval = max(20, 60 - (difficulty_level * 5))  # Decrease spawn interval, minimum 20 frames

    # Spawn debris
    spawn_timer += 1
    if spawn_timer >= spawn_interval:
        debris_list.append(Debris(speed_multiplier))
        spawn_timer = 0

    # Update bullets
    for bullet in rocket.bullets[:]:
        bullet.move()
        if bullet.y < 0:
            rocket.bullets.remove(bullet)

    # Update debris
    for debris in debris_list[:]:
        debris.move()
        if debris.y > WINDOW_HEIGHT:
            debris_list.remove(debris)
            continue

        # Check collision with bullets
        for bullet in rocket.bullets[:]:
            # Calculate distance between bullet and debris center
            debris_center_x = debris.x + debris.size//2
            debris_center_y = debris.y + debris.size//2
            distance = math.sqrt((bullet.x - debris_center_x)**2 + 
                               (bullet.y - debris_center_y)**2)
            
            if distance < debris.size//2:  # If bullet is within debris radius
                if debris in debris_list:
                    debris_list.remove(debris)
                if bullet in rocket.bullets:
                    rocket.bullets.remove(bullet)
                score += 10
                break

        # Check collision with rocket
        if (rocket.x < debris.x + debris.size and
            rocket.x + rocket.width > debris.x and
            rocket.y < debris.y + debris.size and
            rocket.y + rocket.height > debris.y):
            running = False

    # Update stars
    for star in stars:
        star.update()

    # Draw everything
    # Draw background
    screen.fill(DEEP_SPACE)
    nebula.draw(screen)
    for star in stars:
        star.draw(screen)

    # Draw game elements
    rocket.draw(screen)
    for bullet in rocket.bullets:
        bullet.draw(screen)
    for debris in debris_list:
        debris.draw(screen)

    # Draw score and difficulty
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Score: {score}", True, WHITE)
    difficulty_text = font.render(f"Level: {difficulty_level}", True, WHITE)
    screen.blit(score_text, (10, 10))
    screen.blit(difficulty_text, (10, 50))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit() 