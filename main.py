# Import required modules
import sys
import os
import pygame
from math import sqrt
from random import choice
from hangman_word_list import words, alphabet
from pygame.locals import (
    MOUSEBUTTONDOWN,
    K_ESCAPE,
    KEYDOWN,
    KEYUP,
    K_RETURN,
)


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller.
    URL: https://stackoverflow.com/questions/31836104/pyinstaller-and-onefile-how-to-include-an-image-in-the-exe-file
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS2  # Adjust to MEIPASS2 if not working
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)


class HangmanGame:
    def __init__(self):
        # Initialize pygame and pygame mixer
        pygame.init()
        pygame.mixer.init()

        # Set up the screen
        self.WIDTH = 800
        self.HEIGHT = 580
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Galge Markanove")

        # Other initialization
        self.RADIUS = 25
        self.GAP = 25
        self.images = self.load_images()
        self.music = self.load_music()
        self.background_image = pygame.image.load(resource_path("images\\background.jpg"))

        # Fonts - font, size, bold, italic
        self.LETTER_FONT = pygame.font.SysFont("Times New Roman", 30, True, False)
        self.WORD_FONT = pygame.font.SysFont("Comicsans", 60, True, True)
        self.TITLE_FONT = pygame.font.SysFont("Calibri", 50, True, True)
        self.END_GAME_FONT = pygame.font.SysFont("Calibri", 30, True, True)
        self.GAME_STATUS_FONT = pygame.font.SysFont("Calibri", 20, True, False)

        # Initialize game variables
        self.hangman_status = 0
        self.word = choice(words)
        self.guessed = []
        self.games_won = 0
        self.total_games = 1
        self.letters = []

        # Iterate to set the position of buttons in accordance with the CROATIAN alphabet
        startx = round((self.WIDTH - (self.RADIUS * 2 + self.GAP) * 10) // 2)
        starty = self.HEIGHT - 200
        for i in range(len(alphabet)):
            x = startx + self.GAP * 2 + \
                ((self.RADIUS * 2 + self.GAP) * (i % 10))
            y = starty + ((i // 10) * (self.GAP + self.RADIUS * 2))
            self.letters.append([x, y, alphabet[i], True])

    def load_images(self):
        """Load images"""
        images = []
        for i in range(7):
            image = pygame.image.load(resource_path(f"images\\hangman{i}.png"))
            images.append(image)
        return images

    def load_music(self):
        """Load music"""
        music = pygame.mixer.music.load(resource_path("music\\Tazi_Tazi.ogg"))
        pygame.mixer.music.play(-1)
        return music

    def draw(self):
        """Draw word, buttons, hangman and messages"""
        self.screen.blit(self.background_image, (0, 0))
        # Draw title
        text = self.TITLE_FONT.render("Galge Markanove", 1, RED)
        self.screen.blit(text, (self.WIDTH // 2 - text.get_width() // 2, 10))

        # Draw word
        display_word = ""
        for letter in self.word:
            if letter in self.guessed:
                display_word += letter + " "
            else:
                display_word += "_ "
        text = self.WORD_FONT.render(display_word, 1, (YELLOW))
        self.screen.blit(text, (250, 250))

        # Draw buttons
        for letter in self.letters:
            x, y, ltr, visible = letter
            if visible:
                pygame.draw.circle(self.screen, BLACK,
                                   (x, y), self.RADIUS, 3)
                text = self.LETTER_FONT.render(ltr, 1, BLACK)
                self.screen.blit(text, (x - text.get_width() //
                                 2, y - text.get_height() // 2))

        # Draw the hangman
        if self.hangman_status <= 6:
            self.screen.blit(self.images[self.hangman_status], (50, 50))

        # Draw the message about games won and total games played
        text = self.GAME_STATUS_FONT.render(
            f"Won: {self.games_won} / Games played: {self.total_games}", 1, YELLOW)
        self.screen.blit(text, (self.WIDTH - text.get_width() - 5, 5))

        pygame.display.update()

    def display_end_message(self, message):
        """Display end message"""
        pygame.time.delay(2500)
        self.screen.blit(self.background_image, (0, 0))
        lines = [line.strip() for line in message.split("\n")]
        line_height = self.END_GAME_FONT.get_height()
        y_position = (self.HEIGHT - line_height * len(lines)) // 2

        for line in lines:
            line_text = self.END_GAME_FONT.render(line, 1, YELLOW)
            x_position = (self.WIDTH - line_text.get_width()) // 2
            self.screen.blit(line_text, (x_position, y_position))
            y_position += line_height

        pygame.display.update()

    def reset_game(self):
        """Reset game"""
        self.word = choice(words)
        self.guessed = []
        self.hangman_status = 0
        for letter in self.letters:
            letter[3] = True
        self.total_games += 1

    def run(self):
        """Run the game - main game loop"""
        FPS = 60
        clock = pygame.time.Clock()
        running = True
        pressed_keys = {}

        while running:
            clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                keys = pygame.key.get_pressed()
                if keys[K_ESCAPE]:
                    running = False

                if event.type == MOUSEBUTTONDOWN:
                    m_x, m_y = pygame.mouse.get_pos()
                    for letter in self.letters:
                        x, y, ltr, visible = letter
                        if visible:
                            distance = sqrt((x - m_x)**2 + (y - m_y)**2)
                            if distance < self.RADIUS:
                                letter[3] = False
                                self.guessed.append(ltr)
                                if ltr not in self.word:
                                    self.hangman_status += 1

                elif event.type == KEYDOWN:
                    pressed_key = event.unicode.upper()
                    if pressed_key in alphabet:
                        if pressed_key == "L":
                            pressed_keys["L"] = True
                        elif pressed_key == "J" and pressed_keys.get("L"):
                            pressed_key = "LJ"
                        elif pressed_key == "N":
                            pressed_keys["N"] = True
                        elif pressed_key == "J" and pressed_keys.get("N"):
                            pressed_key = "NJ"
                        elif pressed_key == "D":
                            pressed_keys["D"] = True
                        elif pressed_key == "Ž" and pressed_keys.get("D"):
                            pressed_key = "DŽ"
                        else:
                            pressed_keys.clear()

                        for letter in self.letters:
                            if letter[2] == pressed_key and letter[3]:
                                letter[3] = False
                                self.guessed.append(pressed_key)
                                if pressed_key not in self.word:
                                    self.hangman_status += 1

                elif event.type == KEYUP:
                    pressed_keys.clear()

            self.draw()

            won = all(letter in self.guessed for letter in self.word)
            lost = self.hangman_status == 6

            if won or lost:
                if won:
                    self.games_won += 1
                    message = f"""You have WON!
                              Click or press ENTER if you want to play again,
                              or press \"ESCAPE\" if you want to quit."""
                else:
                    message = f"""You have LOST!
                              The requested word was: {self.word}.
                              Click or press ENTER if you want to play again,
                              or press \"ESCAPE\" if you want to quit."""

                self.display_end_message(message)

                waiting = True
                while waiting:
                    for event in pygame.event.get():
                        if event.type == MOUSEBUTTONDOWN or (event.type == KEYDOWN
                                                             and event.key == K_RETURN):
                            self.reset_game()
                            waiting = False
                        elif event.type == KEYDOWN:
                            if event.key == K_ESCAPE:
                                running = False
                                waiting = False

        pygame.mixer.quit()
        pygame.quit()

    def main(self):
        self.run()


if __name__ == "__main__":
    game = HangmanGame()
    game.main()