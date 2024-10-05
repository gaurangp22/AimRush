import math
import random
import time
import pygame

# Alright, let's get this party started by initializing Pygame!
pygame.init()

# Setting up the window dimensions
WIDTH, HEIGHT = 800, 600
TARGET_INCREMENT = 400  # Time to wait before spawning a new target (in milliseconds)
TARGET_EVENT = pygame.USEREVENT  # Custom event we’ll use to create new targets
TARGET_PADDING = 30  # Just some space to keep targets from spawning too close to the edges
BG_COLOR = (0, 25, 40)  # Our lovely background color
LIVES = 3  # You get three chances before it’s game over!
TOP_BAR_HEIGHT = 50  # Height for the top bar where we’ll show the stats

# Setting up a font for displaying text
LABEL_FONT = pygame.font.SysFont("comicsans", 24)

# Creating the display window for our game
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Aim Trainer")  # Title of our game


class Target:
    """This class represents the targets we need to hit."""
    MAX_SIZE = 30  # The biggest the target can get
    GROWTH_RATE = 0.2  # How quickly it expands and contracts
    COLOR = "red"  # The main color of the target
    SECOND_COLOR = "white"  # A secondary color for some flair

    def __init__(self, x, y):
        # When we create a target, we give it an initial position and size
        self.x = x
        self.y = y
        self.size = 0  # Start small
        self.grow = True  # It’s going to grow at first

    def update(self):
        # Let’s make the target grow and shrink
        if self.size + self.GROWTH_RATE >= self.MAX_SIZE:
            self.grow = False  # Once it hits max size, stop growing

        if self.grow:
            self.size += self.GROWTH_RATE  # Keep growing
        else:
            self.size -= self.GROWTH_RATE  # Start shrinking

    def draw(self, win):
        # Time to draw the target on the window
        pygame.draw.circle(win, self.COLOR, (self.x, self.y), self.size)  # Main circle
        pygame.draw.circle(win, self.SECOND_COLOR, (self.x, self.y), self.size * 0.8)  # Inner circle
        pygame.draw.circle(win, self.COLOR, (self.x, self.y), self.size * 0.6)  # Another inner circle
        pygame.draw.circle(win, self.SECOND_COLOR, (self.x, self.y), self.size * 0.4)  # Even smaller circle

    def collide(self, x, y):
        # Check if a click hit the target
        dis = math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)  # Calculate the distance
        return dis <= self.size  # If the distance is less than the target size, we hit it!


def draw(win, targets):
    # Clear the window with the background color
    win.fill(BG_COLOR)

    # Draw all the targets
    for target in targets:
        target.draw(win)


def format_time(secs):
    # Convert time in seconds into a nice readable format
    milli = math.floor(int(secs * 1000 % 1000) / 100)
    seconds = int(round(secs % 60, 1))
    minutes = int(secs // 60)

    return f"{minutes:02d}:{seconds:02d}.{milli}"  # Return formatted time


def draw_top_bar(win, elapsed_time, targets_pressed, misses):
    # Draw the top bar that shows important game stats
    pygame.draw.rect(win, "grey", (0, 0, WIDTH, TOP_BAR_HEIGHT))  # Top bar background
    time_label = LABEL_FONT.render(f"Time: {format_time(elapsed_time)}", 1, "black")  # Time display

    # Calculate and show speed of hits per second
    speed = round(targets_pressed / elapsed_time, 1)
    speed_label = LABEL_FONT.render(f"Speed: {speed} t/s", 1, "black")

    hits_label = LABEL_FONT.render(f"Hits: {targets_pressed}", 1, "black")  # Show hits
    lives_label = LABEL_FONT.render(f"Lives: {LIVES - misses}", 1, "black")  # Show remaining lives

    # Blit the labels onto the window
    win.blit(time_label, (5, 5))
    win.blit(speed_label, (200, 5))
    win.blit(hits_label, (450, 5))
    win.blit(lives_label, (650, 5))


def end_screen(win, elapsed_time, targets_pressed, clicks):
    # Show the end screen when the game is over
    win.fill(BG_COLOR)  # Fill the screen with background color
    time_label = LABEL_FONT.render(f"Time: {format_time(elapsed_time)}", 1, "white")  # Time spent

    # Calculate speed and hits for display
    speed = round(targets_pressed / elapsed_time, 1)
    speed_label = LABEL_FONT.render(f"Speed: {speed} t/s", 1, "white")
    hits_label = LABEL_FONT.render(f"Hits: {targets_pressed}", 1, "white")

    # Calculate accuracy and display it
    accuracy = round(targets_pressed / clicks * 100, 1)
    accuracy_label = LABEL_FONT.render(f"Accuracy: {accuracy}%", 1, "white")

    # Center the labels on the screen
    win.blit(time_label, (get_middle(time_label), 100))
    win.blit(speed_label, (get_middle(speed_label), 200))
    win.blit(hits_label, (get_middle(hits_label), 300))
    win.blit(accuracy_label, (get_middle(accuracy_label), 400))

    pygame.display.update()  # Update the display

    # Wait for player to quit or press a key to exit
    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                quit()


def get_middle(surface):
    # Helper function to center text on the screen
    return WIDTH / 2 - surface.get_width() / 2


def main():
    run = True  # Main game loop flag
    targets = []  # List to keep track of active targets
    clock = pygame.time.Clock()  # Clock to control frame rate

    # Stats for tracking performance
    targets_pressed = 0
    clicks = 0
    misses = 0
    start_time = time.time()  # Start time of the game

    # Set up a timer to spawn targets
    pygame.time.set_timer(TARGET_EVENT, TARGET_INCREMENT)

    while run:
        clock.tick(60)  # Maintain 60 FPS
        click = False  # Reset click state
        mouse_pos = pygame.mouse.get_pos()  # Get current mouse position
        elapsed_time = time.time() - start_time  # Calculate elapsed time

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Quit the game if the window is closed
                run = False
                break

            if event.type == TARGET_EVENT:  # Time to spawn a new target
                x = random.randint(TARGET_PADDING, WIDTH - TARGET_PADDING)
                y = random.randint(TARGET_PADDING + TOP_BAR_HEIGHT, HEIGHT - TARGET_PADDING)
                target = Target(x, y)  # Create a new target
                targets.append(target)

            if event.type == pygame.MOUSEBUTTONDOWN:  # Check if the mouse is clicked
                click = True
                clicks += 1  # Count the click

        # Update each target
        for target in targets:
            target.update()

            # Remove targets that have shrunk to zero size and count misses
            if target.size <= 0:
                targets.remove(target)
                misses += 1

            # Check for clicks on targets
            if click and target.collide(*mouse_pos):
                targets.remove(target)  # Hit! Remove the target
                targets_pressed += 1  # Increment score

        # If we run out of lives, show the end screen
        if misses >= LIVES:
            end_screen(WIN, elapsed_time, targets_pressed, clicks)

        # Draw everything on the window
        draw(WIN, targets)
        draw_top_bar(WIN, elapsed_time, targets_pressed, misses)
        pygame.display.update()  # Update the display

    pygame.quit()  # Close the game


if __name__ == "__main__":
    main()  # Start the game
