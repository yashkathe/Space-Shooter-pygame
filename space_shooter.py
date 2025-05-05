import math
import random
import sys

import pygame

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
SILVER = (192, 192, 192)
BLUE = (0, 100, 255)


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
        color = (
            int(255 * self.brightness),
            int(255 * self.brightness),
            int(255 * self.brightness),
        )
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
        for i in range(len(self.points)):
            p1 = self.points[i]
            p2 = self.points[(i + 1) % len(self.points)]
            alpha = int(50 + 20 * math.sin(pygame.time.get_ticks() * 0.001 + i))
            color = (*NEBULA_COLOR, alpha)
            pygame.draw.line(surface, color, p1, p2, 2)


# Player Rocket
class Rocket:
    def __init__(self):
        self.width = 40  # Made narrower for better rocket proportions
        self.height = 100  # Made taller for better rocket proportions
        self.x = WINDOW_WIDTH // 2 - self.width // 2
        self.y = WINDOW_HEIGHT - self.height - 20
        self.speed = 5
        self.bullets = []
        self.num_launchers = 1
        self.launcher_width = 8
        self.launcher_height = 12
        self.engine_flame_height = 0
        self.engine_flame_direction = 1

    def move(self, direction):
        if direction == "left" and self.x > 0:
            self.x -= self.speed
        if direction == "right" and self.x < WINDOW_WIDTH - self.width:
            self.x += self.speed

    def shoot(self):
        # Calculate launcher positions
        launcher_spacing = self.width / (self.num_launchers + 1)
        for i in range(self.num_launchers):
            launcher_x = self.x + launcher_spacing * (i + 1)
            bullet = Bullet(launcher_x, self.y + self.height * 0.7)  # Adjusted bullet spawn position
            self.bullets.append(bullet)

    def upgrade(self):
        self.num_launchers += 1
        self.width += 20  # Increase width for new launcher

    def draw(self, screen):
        # Draw engine flame
        self.engine_flame_height += 0.5 * self.engine_flame_direction
        if self.engine_flame_height >= 20 or self.engine_flame_height <= 10:
            self.engine_flame_direction *= -1

        # Draw main body
        body_rect = pygame.Rect(self.x, self.y + self.height * 0.2, self.width, self.height * 0.6)
        pygame.draw.rect(screen, SILVER, body_rect)
        
        # Draw nose cone
        nose_points = [
            (self.x + self.width//2, self.y),  # Top point
            (self.x, self.y + self.height * 0.2),  # Bottom left
            (self.x + self.width, self.y + self.height * 0.2)  # Bottom right
        ]
        pygame.draw.polygon(screen, SILVER, nose_points)
        
        # Draw fins
        fin_height = self.height * 0.15
        fin_width = self.width * 0.4
        fin_y = self.y + self.height * 0.7
        
        # Left fin
        left_fin_points = [
            (self.x - fin_width//2, fin_y),
            (self.x, fin_y + fin_height),
            (self.x, fin_y)
        ]
        pygame.draw.polygon(screen, DARK_RED, left_fin_points)
        
        # Right fin
        right_fin_points = [
            (self.x + self.width, fin_y),
            (self.x + self.width + fin_width//2, fin_y),
            (self.x + self.width, fin_y + fin_height)
        ]
        pygame.draw.polygon(screen, DARK_RED, right_fin_points)

        # Draw cockpit
        cockpit_width = self.width * 0.4
        cockpit_height = self.height * 0.15
        cockpit_x = self.x + (self.width - cockpit_width) / 2
        cockpit_y = self.y + self.height * 0.3
        pygame.draw.ellipse(screen, BLUE, (cockpit_x, cockpit_y, cockpit_width, cockpit_height))

        # Draw launchers
        launcher_spacing = self.width / (self.num_launchers + 1)
        for i in range(self.num_launchers):
            launcher_x = self.x + launcher_spacing * (i + 1) - self.launcher_width/2
            pygame.draw.rect(screen, DARK_RED, 
                           (launcher_x, self.y + self.height * 0.5,
                            self.launcher_width, self.launcher_height))

        # Draw engine flame
        flame_width = self.width * 0.4
        flame_x = self.x + (self.width - flame_width) / 2
        flame_points = [
            (flame_x, self.y + self.height),
            (flame_x + flame_width/2, self.y + self.height + self.engine_flame_height),
            (flame_x + flame_width, self.y + self.height)
        ]
        # Draw multiple flame layers for better effect
        pygame.draw.polygon(screen, (255, 100, 0), flame_points)  # Orange inner flame
        outer_flame_points = [
            (flame_x - 5, self.y + self.height),
            (flame_x + flame_width/2, self.y + self.height + self.engine_flame_height + 5),
            (flame_x + flame_width + 5, self.y + self.height)
        ]
        pygame.draw.polygon(screen, RED, outer_flame_points)  # Red outer flame


# Bullet
class Bullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 7
        self.radius = 3

    def move(self):
        self.y -= self.speed

    def draw(self, screen):
        pygame.draw.circle(screen, WHITE, (self.x, self.y), self.radius)


# Debris
class Debris:
    def __init__(self, speed_multiplier=1.0):
        self.size = random.randint(25, 40)
        self.x = random.randint(0, WINDOW_WIDTH - self.size)
        self.y = -self.size
        self.base_speed = random.randint(2, 5)
        self.speed = self.base_speed * speed_multiplier
        self.rotation = random.randint(0, 360)
        self.rotation_speed = random.uniform(-2, 2)
        self.points = self.generate_asteroid_shape()
        self.holes = self.generate_holes()
        self.width = self.size
        self.height = self.size

    def generate_asteroid_shape(self):
        points = []
        num_points = random.randint(8, 12)
        for i in range(num_points):
            angle = (2 * math.pi * i) / num_points
            radius = self.size / 2 * random.uniform(0.8, 1.2)
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            points.append((x, y))
        return points

    def generate_holes(self):
        holes = []
        num_holes = random.randint(1, 3)
        for _ in range(num_holes):
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(0, self.size / 3)
            x = distance * math.cos(angle)
            y = distance * math.sin(angle)
            radius = random.uniform(3, 8)
            holes.append((x, y, radius))
        return holes

    def move(self):
        self.y += self.speed
        self.rotation += self.rotation_speed

    def draw(self, screen):
        asteroid_surface = pygame.Surface(
            (self.size * 2, self.size * 2), pygame.SRCALPHA
        )

        rotated_points = []
        for x, y in self.points:
            angle_rad = math.radians(self.rotation)
            rotated_x = x * math.cos(angle_rad) - y * math.sin(angle_rad)
            rotated_y = x * math.sin(angle_rad) + y * math.cos(angle_rad)
            rotated_points.append((rotated_x + self.size, rotated_y + self.size))

        pygame.draw.polygon(asteroid_surface, GRAY, rotated_points)
        pygame.draw.polygon(asteroid_surface, DARK_RED, rotated_points, 2)

        for hole_x, hole_y, radius in self.holes:
            angle_rad = math.radians(self.rotation)
            rotated_hole_x = hole_x * math.cos(angle_rad) - hole_y * math.sin(angle_rad)
            rotated_hole_y = hole_x * math.sin(angle_rad) + hole_y * math.cos(angle_rad)
            pygame.draw.circle(
                asteroid_surface,
                BLACK,
                (int(rotated_hole_x + self.size), int(rotated_hole_y + self.size)),
                int(radius),
            )

        screen.blit(
            asteroid_surface, (self.x - self.size // 2, self.y - self.size // 2)
        )


class ScatterParticle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.uniform(4, 8)  # Increased size
        self.life = 1.0  # Full life
        angle = random.uniform(0, 2 * math.pi)  # Random angle
        speed = random.uniform(2, 6)  # Increased speed
        self.speed_x = math.cos(angle) * speed
        self.speed_y = math.sin(angle) * speed
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-10, 10)  # Increased rotation speed
        self.points = self.generate_shape()

    def generate_shape(self):
        points = []
        num_points = 6  # More points for better shape
        for i in range(num_points):
            angle = (2 * math.pi * i) / num_points
            radius = self.size
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            points.append((x, y))
        return points

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.rotation += self.rotation_speed
        self.life -= 0.015  # Slower fade
        self.size *= 0.99  # Slower shrink
        # Add gravity effect
        self.speed_y += 0.1

    def draw(self, screen):
        if self.life <= 0:
            return False

        # Create surface for the particle
        particle_surface = pygame.Surface((self.size * 4, self.size * 4), pygame.SRCALPHA)
        
        # Draw the particle
        rotated_points = []
        for x, y in self.points:
            angle_rad = math.radians(self.rotation)
            rotated_x = x * math.cos(angle_rad) - y * math.sin(angle_rad)
            rotated_y = x * math.sin(angle_rad) + y * math.cos(angle_rad)
            rotated_points.append((rotated_x + self.size * 2, rotated_y + self.size * 2))

        # Calculate alpha based on life
        alpha = int(255 * self.life)
        color_with_alpha = (*self.color, alpha)
        
        # Draw multiple layers for better visibility
        pygame.draw.polygon(particle_surface, color_with_alpha, rotated_points)
        # Draw inner glow
        inner_color = (min(255, self.color[0] + 50), 
                      min(255, self.color[1] + 50), 
                      min(255, self.color[2] + 50), 
                      alpha)
        pygame.draw.polygon(particle_surface, inner_color, rotated_points, 1)
        
        screen.blit(particle_surface, (self.x - self.size * 2, self.y - self.size * 2))
        return True


def show_pause_screen():
    # Create semi-transparent overlay
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    overlay.set_alpha(128)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))
    
    # Draw pause text
    font = pygame.font.Font(None, 74)
    pause_text = font.render("PAUSED", True, WHITE)
    screen.blit(pause_text, (WINDOW_WIDTH//2 - pause_text.get_width()//2, WINDOW_HEIGHT//2 - 50))
    
    # Draw instructions
    instruction_font = pygame.font.Font(None, 36)
    instructions = [
        "Press P to resume",
        "Press R to restart",
        "Press Q to quit"
    ]
    
    for i, instruction in enumerate(instructions):
        text = instruction_font.render(instruction, True, WHITE)
        screen.blit(text, (WINDOW_WIDTH//2 - text.get_width()//2, 
                          WINDOW_HEIGHT//2 + 50 + i * 40))
    
    pygame.display.flip()

def show_game_over(score, level):
    # Create semi-transparent overlay
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    overlay.set_alpha(128)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))
    
    font = pygame.font.Font(None, 74)
    game_over_text = font.render("Game Over!", True, WHITE)
    score_text = font.render(f"Final Score: {score}", True, WHITE)
    level_text = font.render(f"Level Reached: {level}", True, WHITE)
    
    # Draw game over information
    screen.blit(game_over_text, 
                (WINDOW_WIDTH//2 - game_over_text.get_width()//2, 
                 WINDOW_HEIGHT//2 - 150))
    screen.blit(score_text, 
                (WINDOW_WIDTH//2 - score_text.get_width()//2, 
                 WINDOW_HEIGHT//2 - 50))
    screen.blit(level_text, 
                (WINDOW_WIDTH//2 - level_text.get_width()//2, 
                 WINDOW_HEIGHT//2 + 50))
    
    # Draw restart instructions
    instruction_font = pygame.font.Font(None, 36)
    instructions = [
        "Press R to restart",
        "Press Q to quit"
    ]
    
    for i, instruction in enumerate(instructions):
        text = instruction_font.render(instruction, True, WHITE)
        screen.blit(text, (WINDOW_WIDTH//2 - text.get_width()//2, 
                          WINDOW_HEIGHT//2 + 150 + i * 40))
    
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return True  # Restart game
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
    return False


def show_start_screen():
    screen.fill(DEEP_SPACE)
    
    # Draw title
    title_font = pygame.font.Font(None, 74)
    title_text = title_font.render("SPACE SHOOTER", True, WHITE)
    screen.blit(title_text, (WINDOW_WIDTH//2 - title_text.get_width()//2, WINDOW_HEIGHT//4))
    
    # Draw instructions
    instruction_font = pygame.font.Font(None, 36)
    instructions = [
        "Use LEFT and RIGHT arrows to move",
        "Press SPACEBAR to shoot",
        "Destroy the space debris!",
        "",
        "Press ENTER to start"
    ]
    
    for i, instruction in enumerate(instructions):
        text = instruction_font.render(instruction, True, WHITE)
        screen.blit(text, (WINDOW_WIDTH//2 - text.get_width()//2, 
                          WINDOW_HEIGHT//2 + i * 40))
    
    # Draw a sample rocket
    sample_rocket = Rocket()
    sample_rocket.x = WINDOW_WIDTH//2 - sample_rocket.width//2
    sample_rocket.y = WINDOW_HEIGHT//2 - 100
    sample_rocket.draw(screen)
    
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    waiting = False


# Game setup
def initialize_game():
    rocket = Rocket()
    debris_list = []
    # Create initial debris
    for _ in range(15):  # Start with 15 debris
        debris = Debris(speed_multiplier=1.0)
        debris.y = random.randint(-WINDOW_HEIGHT, 0)  # Random starting position
        debris_list.append(debris)
    
    score = 0
    clock = pygame.time.Clock()
    spawn_timer = 0
    game_time = 0
    difficulty_level = 1
    speed_multiplier = 1.0
    spawn_interval = 60
    max_debris = 15  # Maximum number of debris to maintain
    
    return rocket, debris_list, score, clock, spawn_timer, game_time, difficulty_level, speed_multiplier, spawn_interval, max_debris


# Main game function
def main():
    while True:  # Main game loop for restart functionality
        # Show start screen
        show_start_screen()
        
        # Initialize game
        rocket, debris_list, score, clock, spawn_timer, game_time, difficulty_level, speed_multiplier, spawn_interval, max_debris = initialize_game()
        
        # Create background elements
        stars = [Star() for _ in range(200)]
        nebula = Nebula()
        
        # Initialize scatter particles list
        scatter_particles = []
        
        # Game loop
        running = True
        paused = False
        while running:
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        rocket.shoot()
                    elif event.key == pygame.K_p:
                        paused = not paused
                    elif event.key == pygame.K_r:
                        running = False  # Restart game
                    elif event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()

            if paused:
                show_pause_screen()
                continue

            # Get keyboard state
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                rocket.move("left")
            if keys[pygame.K_RIGHT]:
                rocket.move("right")

            # Update game time and difficulty
            game_time += 1
            if game_time % (20 * 60) == 0:  # Every 20 seconds
                difficulty_level += 1
                speed_multiplier += 0.2  # Increase speed by 20%
                spawn_interval = max(15, 60 - (difficulty_level * 8))  # Faster spawn rate decrease
                
                # Add new launcher every 2 levels
                if difficulty_level % 2 == 0:
                    rocket.upgrade()

            # Spawn debris
            spawn_timer += 1
            if spawn_timer >= spawn_interval:
                # Only spawn new debris if we're below the maximum
                if len(debris_list) < max_debris:
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
                    # Immediately spawn a new debris to maintain count
                    if len(debris_list) < max_debris:
                        new_debris = Debris(speed_multiplier)
                        new_debris.y = -new_debris.size
                        debris_list.append(new_debris)
                    continue

                # Check collision with bullets
                for bullet in rocket.bullets[:]:
                    debris_center_x = debris.x + debris.size//2
                    debris_center_y = debris.y + debris.size//2
                    distance = math.sqrt((bullet.x - debris_center_x)**2 + 
                                       (bullet.y - debris_center_y)**2)
                    
                    if distance < debris.size//2:
                        if debris in debris_list:
                            # Create scatter particles
                            for _ in range(40):  # Increased number of particles
                                particle = ScatterParticle(
                                    debris_center_x,
                                    debris_center_y,
                                    (200, 200, 200)  # Brighter color
                                )
                                scatter_particles.append(particle)
                            
                            debris_list.remove(debris)
                            # Spawn new debris to maintain count
                            if len(debris_list) < max_debris:
                                new_debris = Debris(speed_multiplier)
                                new_debris.y = -new_debris.size
                                debris_list.append(new_debris)
                        if bullet in rocket.bullets:
                            rocket.bullets.remove(bullet)
                        score += 10
                        break

                # Check collision with rocket
                if (rocket.x < debris.x + debris.size and
                    rocket.x + rocket.width > debris.x and
                    rocket.y < debris.y + debris.size and
                    rocket.y + rocket.height > debris.y):
                    if not show_game_over(score, difficulty_level):
                        return  # Exit game if not restarting
                    running = False
                    break

            # Update scatter particles
            scatter_particles = [particle for particle in scatter_particles if particle.update()]

            # Update stars
            for star in stars:
                star.update()

            # Draw everything
            screen.fill(DEEP_SPACE)
            nebula.draw(screen)
            for star in stars:
                star.draw(screen)

            rocket.draw(screen)
            for bullet in rocket.bullets:
                bullet.draw(screen)
            for debris in debris_list:
                debris.draw(screen)
            for particle in scatter_particles:
                particle.draw(screen)

            # Draw score and difficulty
            font = pygame.font.Font(None, 36)
            score_text = font.render(f"Score: {score}", True, WHITE)
            difficulty_text = font.render(f"Level: {difficulty_level}", True, WHITE)
            debris_count_text = font.render(f"Debris: {len(debris_list)}", True, WHITE)
            screen.blit(score_text, (10, 10))
            screen.blit(difficulty_text, (10, 50))
            screen.blit(debris_count_text, (10, 90))

            pygame.display.flip()
            clock.tick(60)


if __name__ == "__main__":
    main()
