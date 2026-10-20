
"""
Alien Invasion - ICT 362 Project 2

Controls:
    Left Arrow or A: Move left
    Right Arrow or D: Move right
    Space: Fire bullets
    R: Restart after winning or losing
    Q or Escape: Quit
"""

import sys
import pygame

# -------------------- Settings --------------------

WIDTH = 1000
HEIGHT = 700
FPS = 60

BG_COLOR = (225, 225, 225)  # Light gray
SHIP_COLOR = (35, 75, 160)
BULLET_COLOR = (30, 30, 30)
ALIEN_COLOR = (40, 145, 75)
TEXT_COLOR = (30, 30, 30)

SHIP_SPEED = 6
BULLET_SPEED = 9
MAX_BULLETS = 5

ALIEN_ROWS = 4
ALIEN_COLUMNS = 9
ALIEN_X_GAP = 85
ALIEN_Y_GAP = 65
ALIEN_SPEED = 1.3
ALIEN_DROP = 25


class Ship:
    """Represent the player spaceship."""

    def __init__(self):
        """Initialize the ship at the bottom center."""
        self.width = 54
        self.height = 42
        self.x = WIDTH // 2
        self.y = HEIGHT - 50
        self.left = False
        self.right = False

    @property
    def rect(self):
        """Return the ship's collision rectangle."""
        return pygame.Rect(
            int(self.x - self.width / 2),
            int(self.y - self.height / 2),
            self.width,
            self.height,
        )

    def update(self):
        """Move the ship while keeping it inside the screen."""
        if self.left:
            self.x -= SHIP_SPEED
        if self.right:
            self.x += SHIP_SPEED

        self.x = max(
            self.width / 2,
            min(WIDTH - self.width / 2, self.x)
        )

    def draw(self, screen):
        """Draw the spaceship using Pygame shapes."""
        nose = (int(self.x), int(self.y - 21))
        left = (int(self.x - 27), int(self.y + 21))
        right = (int(self.x + 27), int(self.y + 21))

        pygame.draw.polygon(
            screen, SHIP_COLOR, [nose, left, right]
        )
        pygame.draw.rect(
            screen,
            (180, 210, 245),
            (int(self.x - 7), int(self.y - 2), 14, 15),
            border_radius=3,
        )


class Bullet:
    """Represent a bullet traveling upward."""

    def __init__(self, x, y):
        """Create a bullet at the ship's position."""
        self.x = int(x)
        self.y = int(y)
        self.width = 5
        self.height = 16

    @property
    def rect(self):
        """Return the bullet's collision rectangle."""
        return pygame.Rect(
            self.x - self.width // 2,
            self.y - self.height // 2,
            self.width,
            self.height,
        )

    def update(self):
        """Move the bullet upward."""
        self.y -= BULLET_SPEED

    def draw(self, screen):
        """Draw the bullet."""
        pygame.draw.rect(
            screen, BULLET_COLOR, self.rect,
            border_radius=2
        )


class Alien:
    """Represent one alien in the fleet."""

    def __init__(self, x, y):
        """Create an alien at the specified position."""
        self.x = float(x)
        self.y = float(y)
        self.width = 42
        self.height = 32

    @property
    def rect(self):
        """Return the alien's collision rectangle."""
        return pygame.Rect(
            int(self.x - self.width / 2),
            int(self.y - self.height / 2),
            self.width,
            self.height,
        )

    def draw(self, screen):
        """Draw an alien using simple shapes."""
        r = self.rect

        pygame.draw.ellipse(screen, ALIEN_COLOR, r)

        # Alien eyes
        pygame.draw.circle(
            screen, (255, 255, 255),
            (r.centerx - 8, r.centery - 3), 5
        )
        pygame.draw.circle(
            screen, (255, 255, 255),
            (r.centerx + 8, r.centery - 3), 5
        )
        pygame.draw.circle(
            screen, (20, 20, 20),
            (r.centerx - 8, r.centery - 3), 2
        )
        pygame.draw.circle(
            screen, (20, 20, 20),
            (r.centerx + 8, r.centery - 3), 2
        )

        # Alien feet
        pygame.draw.line(
            screen, ALIEN_COLOR,
            (r.left + 8, r.bottom - 2),
            (r.left + 3, r.bottom + 5), 3
        )
        pygame.draw.line(
            screen, ALIEN_COLOR,
            (r.centerx, r.bottom - 2),
            (r.centerx, r.bottom + 5), 3
        )
        pygame.draw.line(
            screen, ALIEN_COLOR,
            (r.right - 8, r.bottom - 2),
            (r.right - 3, r.bottom + 5), 3
        )


class AlienInvasion:
    """Manage game setup, events, updates, and drawing."""

    def __init__(self):
        """Initialize Pygame and start a new game."""
        pygame.init()
        pygame.display.set_caption("Alien Invasion - ICT 362")

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 30)
        self.large_font = pygame.font.SysFont(None, 64)

        self.reset_game()

    def reset_game(self):
        """Reset the ship, bullets, aliens, and game status."""
        self.ship = Ship()
        self.bullets = []
        self.aliens = []
        self.direction = 1
        self.score = 0
        self.game_over = False
        self.won = False
        self.create_fleet()

    def create_fleet(self):
        """Create rows of aliens across the upper screen."""
        total_width = (ALIEN_COLUMNS - 1) * ALIEN_X_GAP
        start_x = (WIDTH - total_width) // 2
        start_y = 90

        for row in range(ALIEN_ROWS):
            for col in range(ALIEN_COLUMNS):
                x = start_x + col * ALIEN_X_GAP
                y = start_y + row * ALIEN_Y_GAP
                self.aliens.append(Alien(x, y))

    def check_events(self):
        """Respond to keyboard input and window events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_game()

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_q, pygame.K_ESCAPE):
                    self.quit_game()

                if event.key in (pygame.K_LEFT, pygame.K_a):
                    self.ship.left = True

                if event.key in (pygame.K_RIGHT, pygame.K_d):
                    self.ship.right = True

                if (
                    event.key == pygame.K_SPACE
                    and not self.game_over
                    and not self.won
                ):
                    self.fire_bullet()

                if (
                    event.key == pygame.K_r
                    and (self.game_over or self.won)
                ):
                    self.reset_game()

            if event.type == pygame.KEYUP:
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    self.ship.left = False

                if event.key in (pygame.K_RIGHT, pygame.K_d):
                    self.ship.right = False

    def fire_bullet(self):
        """Fire a bullet if fewer than five are active."""
        if len(self.bullets) < MAX_BULLETS:
            bullet_y = self.ship.y - self.ship.height // 2
            self.bullets.append(
                Bullet(self.ship.x, bullet_y)
            )

    def update_bullets(self):
        """Move bullets and remove bullets that hit aliens."""
        for bullet in self.bullets[:]:
            bullet.update()

            # Remove bullets that leave the screen.
            if bullet.rect.bottom < 0:
                self.bullets.remove(bullet)
                continue

            # Check for alien collisions.
            hit_alien = None
            for alien in self.aliens:
                if bullet.rect.colliderect(alien.rect):
                    hit_alien = alien
                    break

            if hit_alien is not None:
                self.bullets.remove(bullet)
                self.aliens.remove(hit_alien)
                self.score += 10

    def update_aliens(self):
        """Move the fleet and drop it when it reaches an edge."""
        if not self.aliens:
            self.won = True
            return

        reached_edge = False

        for alien in self.aliens:
            alien.x += ALIEN_SPEED * self.direction

            if (
                alien.rect.right >= WIDTH - 10
                or alien.rect.left <= 10
            ):
                reached_edge = True

        if reached_edge:
            self.direction *= -1

            for alien in self.aliens:
                alien.y += ALIEN_DROP

        # Lose if the aliens reach the ship's level.
        for alien in self.aliens:
            if alien.rect.bottom >= self.ship.rect.top:
                self.game_over = True
                break

    def update(self):
        """Update moving objects while the game is active."""
        if self.game_over or self.won:
            return

        self.ship.update()
        self.update_bullets()
        self.update_aliens()

    def draw_status(self):
        """Display score and current active bullet count."""
        score_text = self.font.render(
            f"Score: {self.score}", True, TEXT_COLOR
        )
        bullet_text = self.font.render(
            f"Bullets: {len(self.bullets)}/{MAX_BULLETS}",
            True, TEXT_COLOR
        )

        self.screen.blit(score_text, (15, 15))
        self.screen.blit(
            bullet_text,
            (WIDTH - bullet_text.get_width() - 15, 15)
        )

    def draw_end_message(self):
        """Display win/loss text and restart instructions."""
        if not self.game_over and not self.won:
            return

        message = "YOU WIN!" if self.won else "GAME OVER"
        title = self.large_font.render(
            message, True, TEXT_COLOR
        )
        subtitle = self.font.render(
            "Press R to restart or Q to quit",
            True, TEXT_COLOR
        )

        self.screen.blit(
            title,
            title.get_rect(
                center=(WIDTH // 2, HEIGHT // 2 - 25)
            )
        )
        self.screen.blit(
            subtitle,
            subtitle.get_rect(
                center=(WIDTH // 2, HEIGHT // 2 + 30)
            )
        )

    def update_screen(self):
        """Draw all game objects and refresh the display."""
        self.screen.fill(BG_COLOR)

        for bullet in self.bullets:
            bullet.draw(self.screen)

        for alien in self.aliens:
            alien.draw(self.screen)

        self.ship.draw(self.screen)
        self.draw_status()
        self.draw_end_message()

        pygame.display.flip()

    @staticmethod
    def quit_game():
        """Close Pygame and exit."""
        pygame.quit()
        sys.exit()

    def run(self):
        """Run the main game loop."""
        while True:
            self.check_events()
            self.update()
            self.update_screen()
            self.clock.tick(FPS)


def main():
    """Create and run the game."""
    game = AlienInvasion()
    game.run()


if __name__ == "__main__":
    main()
