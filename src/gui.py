import math
import sys
import pygame
import os
import time
from game import get_current_player, get_card_sigil_info, get_card_health, get_card_id, get_health, get_card_count, get_drawn_cards, get_drawn_squirrels, MIN_HEALTH, MAX_HEALTH
from data import cards, sigil_descriptions

# link asset dir to .exe temp location
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(__file__)
assets_dir = os.path.join(base_path, "assets")

# Colour Constants.
WHITE = (254, 255, 255)
PURE_BLACK = (0, 0, 0)
BLACK = (20, 20, 20)
DARKEST_GRAY = (30, 30, 30)
DARK_GRAY = (50, 50, 50)
GRAY = (70, 70, 70)
LIGHT_GRAY = (255, 100, 100)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
YELLOW = (255,146,50)
ORANGE = (195, 50, 0)


# Layout Constants.
SCALE_X = 232
SCALE_Y = 52
SCALE_WIDTH = 8
SCALE_HEIGHT = 374
POINTER_WIDTH = 14
POINTER_HEIGHT = 10
POINTER_X = 229
CARD_WIDTH = 98
CARD_HEIGHT = 149
CARD_X = 273
CARD_Y = 476
CARD_Y_OFFSET = 17
CARD_SPACING = 105
INDICATOR_WIDTH = 98
INDICATOR_HEIGHT = 149
BELL_WIDTH = 203
BELL_HEIGHT = 80
BELL_X = 35
BELL_Y = 476
BOARD_CARD_WIDTH = 131
BOARD_CARD_HEIGHT = 199
COL_SPACING = 140
ROW_SPACING = 210
TOP_MARGIN = 35
LEFT_MARGIN = 273
DESCRIPTION_X = 859
DESCRIPTION_Y = 52
DESCRIPTION_WIDTH = 296
DESCRIPTION_HEIGHT = 374
SQUIRREL_INDICATOR_X = 952
RANDOM_INDICATOR_X = 1057
SQUIRREL_INDICATOR_Y = 476

BORDER = 2
THIN_BORDER = 2
MARGIN = 7
BOARD_POSITIONS = 4


class GameGUI:
    """Handles the graphical user interface. This includes drawing the board, 
       the players hand, the health scale, and other UI elements, as well as processing 
       user input events to interact with the game."""
    def __init__(self, event_queue=None, width=1190, height=686):
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Inscryption AI")
        self.clock = pygame.time.Clock()
        self.running = True
        self.event_queue = event_queue
        self.hand_card_rects = []
        self.draw_indicators = []
        self.board_position_rects = []
        self.end_turn_indicator = None
        self.description = sigil_descriptions[0]
        self.start_game = False
        self.settings_indicators = []
        self.adaptive_mode = True
        self.visualise_moves = False
        self.winner = False
        self.defeated = False
        self.font = pygame.font.Font(os.path.join(assets_dir, "HEAVYWEI.TTF"), 16)
        self.font_large = pygame.font.Font(os.path.join(assets_dir, "HEAVYWEI.TTF"), 50)
        self.card_images = self.load_card_images()


    def load_card_images(self):
        """Loads card images and related assets from the 'assets' directory. 
           Different cards are keyed by by their ID and health and, for certain cards 
           (such as Elks), keys for variants are used (e.g. 'l', 'r')."""
        card_images = {}
        for card_id in range(0, len(cards)):
            max_health = cards[card_id][1]
            if card_id == 9:
                card_images[card_id] = {"l": {}, "r": {}}
                for h in range(1, max_health + 1):
                    filename_left = f"{card_id}_{h}_l.png"
                    filename_right = f"{card_id}_{h}_r.png"
                    path_left = os.path.join(assets_dir, filename_left)
                    path_right = os.path.join(assets_dir, filename_right)
                    image_left = pygame.image.load(path_left).convert_alpha()
                    image_right = pygame.image.load(path_right).convert_alpha()
                    card_images[card_id]["l"][h] = image_left
                    card_images[card_id]["r"][h] = image_right
            elif card_id == 0:
                image = pygame.image.load(os.path.join(assets_dir, "card_slot_orange.png")).convert_alpha()
                card_images[card_id] = {}
                card_images[card_id][0] = image
            else:
                card_images[card_id] = {}
                for h in range(1, max_health + 1):
                    image_filename = f"{card_id}_{h}.png"
                    image_path = os.path.join(assets_dir, image_filename)
                    image = pygame.image.load(image_path).convert_alpha()
                    card_images[card_id][h] = image
        extra_filenames = ["squirrel_back.png", "card_back.png", "bell_icon.png"]
        card_images[len(cards)] = {}
        for extra in range(3):
            image = pygame.image.load(os.path.join(assets_dir, extra_filenames[extra])).convert_alpha()
            card_images[len(cards)][extra] = image
        return card_images


    def draw_health_scale(self):
        """Draws the scale representing the both players health on the screen, 
           with a pointer to indicate the current health value."""
        pygame.draw.rect(self.screen, GRAY, (SCALE_X, SCALE_Y, SCALE_WIDTH, SCALE_HEIGHT))
        pygame.draw.rect(self.screen, BLACK, (SCALE_X, SCALE_Y, SCALE_WIDTH, SCALE_HEIGHT), BORDER)
        health = get_health(self.state["board_state"])
        health = max(MIN_HEALTH, min(health, MAX_HEALTH))
        pointer_y = SCALE_Y + SCALE_HEIGHT - (health / MAX_HEALTH * SCALE_HEIGHT)
        arrow_points = [(POINTER_X, pointer_y),(POINTER_X - POINTER_WIDTH, pointer_y - POINTER_HEIGHT // 2),(POINTER_X - POINTER_WIDTH, pointer_y + POINTER_HEIGHT // 2)]
        pygame.draw.polygon(self.screen, WHITE, arrow_points)


    def wrap_text(self, text, max_width):
        """Wraps a string into multiple lines based on a given max_width value."""
        words = text.split(' ')
        lines = []
        current_line = ""
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            if self.font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        return lines
    

    def draw_description(self):
        """Draws a description box on the right side of the screen, displaying either a short 
           how to play guide, or sigil names and their subsequent descriptions."""
        box_rect = pygame.Rect(DESCRIPTION_X, DESCRIPTION_Y, DESCRIPTION_WIDTH, DESCRIPTION_HEIGHT)
        self.screen.fill(GRAY, box_rect)
        pygame.draw.rect(self.screen, BLACK, box_rect, BORDER)
        available_width = box_rect.width - 2 * MARGIN
        line_height = self.font.get_linesize()
        line_x = box_rect.x + MARGIN
        extra = 0
        for title, description_text in self.description:
            title_surface = self.font.render(title, True, BLACK)
            title_pos = (box_rect.x + MARGIN, box_rect.y + MARGIN + extra)
            self.screen.blit(title_surface, title_pos)
            wrapped_lines = self.wrap_text(description_text, available_width)
            i = 0
            for line in wrapped_lines:
                line_surface = self.font.render(line, True, WHITE)
                line_y = box_rect.y + MARGIN + title_surface.get_height() + MARGIN + i * line_height + extra
                self.screen.blit(line_surface, (line_x, line_y))
                i += 1
            extra+=(line_height*(len(wrapped_lines)+2))


    def draw_setting_option(self, label, state_flag, y_offset, setting_name, box_rect, title_height):
        """Draws a single settings option inside of the settings box."""
        line_surface = self.font.render("    - " + label, True, WHITE)
        self.screen.blit(line_surface, (box_rect.x + MARGIN, y_offset))
        indicator_rect = pygame.Rect(box_rect.x + MARGIN, y_offset + 1, title_height - 3, title_height - 3)
        self.screen.fill(GREEN if state_flag else RED, indicator_rect)
        pygame.draw.rect(self.screen, BLACK, indicator_rect, BORDER)
        self.settings_indicators.append((setting_name, indicator_rect))


    def draw_settings(self):
        """Draws the Settings box on the right side of the screen, including 
           toggles for adaptive mode and move visualisation."""
        self.settings_indicators = []
        box_rect = pygame.Rect(DESCRIPTION_X, DESCRIPTION_Y, DESCRIPTION_WIDTH, DESCRIPTION_HEIGHT)
        self.screen.fill(GRAY, box_rect)
        pygame.draw.rect(self.screen, BLACK, box_rect, BORDER)
        title_surface = self.font.render("Settings.", True, BLACK)
        title_pos = (box_rect.x + MARGIN, box_rect.y + MARGIN)
        self.screen.blit(title_surface, title_pos)
        first_option_y = box_rect.y + MARGIN + title_surface.get_height() + MARGIN
        second_option_y = box_rect.y + MARGIN + title_surface.get_height() * 2 + MARGIN
        self.draw_setting_option("Adaptive Mode", self.adaptive_mode, first_option_y, "adaptive_mode", box_rect, title_surface.get_height())
        self.draw_setting_option("Visualise Moves - Best, Worst", self.visualise_moves, second_option_y, "visualise_moves", box_rect, title_surface.get_height())


    def draw_card(self, card_id, count, card_index):
        """Draws a stacked set of cards in the players hand (with the topmost 
           card showing its face, whilst the others show their backs.)"""
        default_health = cards[card_id][1]
        if card_id == 9:
            card_image = self.card_images[card_id]["r"].get(default_health)
            card_back = self.card_images[len(cards)][1]
        elif card_id == 1:
            card_image = self.card_images[card_id].get(default_health)
            card_back = self.card_images[len(cards)][0]
        else:
            card_image = self.card_images[card_id].get(default_health)
            card_back = self.card_images[len(cards)][1]
        scaled_image = pygame.transform.scale(card_image, (CARD_WIDTH, CARD_HEIGHT))
        scaled_back = pygame.transform.scale(card_back, (CARD_WIDTH, CARD_HEIGHT))
        x_slot = CARD_X + card_index * CARD_SPACING
        for i in range(count):
            y_offset = CARD_Y + i * CARD_Y_OFFSET
            if i == count-1:
                scaled_back = scaled_image
                card_rect = pygame.Rect(x_slot, y_offset, CARD_WIDTH, CARD_HEIGHT)
                self.hand_card_rects.append((card_id, card_rect))
            self.screen.blit(scaled_back, (x_slot, y_offset))
            pygame.draw.rect(self.screen,BLACK,(x_slot, y_offset, CARD_WIDTH, CARD_HEIGHT),THIN_BORDER)


    def draw_player_hand(self):
        """Draws the players hand at the bottom of the screen."""
        hand = self.state["current_player_hand"] if get_current_player(self.state["board_state"]) == 1 else self.state["other_player_hand"]
        card_index = 0
        self.hand_card_rects = []
        for card_id in range(len(cards)):
            count = get_card_count(hand, card_id)
            if count == 0:
                continue
            self.draw_card(card_id, count, card_index)
            card_index += 1


    def draw_drawable_indicators(self):
        """Draws indicators for whether or not the player can 
           draw a new card or a squirrel."""
        drawn_cards = get_drawn_cards(self.state["board_state"], 1)
        drawn_squirrels = get_drawn_squirrels(self.state["board_state"], 1)
        self.draw_indicators = []
        if drawn_cards < 10:
            card_back_image = self.card_images[len(cards)][1]
            scaled_card_back = pygame.transform.scale(card_back_image, (INDICATOR_WIDTH, INDICATOR_HEIGHT))
            self.screen.blit(scaled_card_back, (RANDOM_INDICATOR_X, SQUIRREL_INDICATOR_Y))
            indicator_rect = pygame.Rect(RANDOM_INDICATOR_X, SQUIRREL_INDICATOR_Y, INDICATOR_WIDTH, INDICATOR_HEIGHT)
            self.draw_indicators.append((self.state["p1_draws"][drawn_cards], indicator_rect))
        if drawn_squirrels < 10:
            squirrel_back_image = self.card_images[len(cards)][0]
            scaled_squirrel_back = pygame.transform.scale(squirrel_back_image, (INDICATOR_WIDTH, INDICATOR_HEIGHT))
            self.screen.blit(scaled_squirrel_back, (SQUIRREL_INDICATOR_X, SQUIRREL_INDICATOR_Y))
            indicator_rect = pygame.Rect(SQUIRREL_INDICATOR_X, SQUIRREL_INDICATOR_Y, INDICATOR_WIDTH, INDICATOR_HEIGHT)
            self.draw_indicators.append((1, indicator_rect))


    def draw_end_turn_bell(self):
        """Draws the bell icon that the player can click to end their turn."""
        self.end_turn_indicator = None
        bell_image = self.card_images[len(cards)][2]
        scaled_bell_image = pygame.transform.scale(bell_image, (BELL_WIDTH, BELL_HEIGHT))
        self.screen.blit(scaled_bell_image, (BELL_X, BELL_Y))
        indicator_rect = pygame.Rect(BELL_X, BELL_Y, BELL_WIDTH, BELL_HEIGHT)
        self.end_turn_indicator = indicator_rect


    def draw_board(self):
        """Draws the board slots and any cards currently placed. the top row 
           belongs to the opponent and the bottom row to the human player"""
        self.board_position_rects.clear()
        boards = [("Opponent", self.state["other_player_state"]),("You", self.state["current_player_state"])] if get_current_player(self.state["board_state"]) == 1 else [("Opponent", self.state["current_player_state"]), ("You", self.state["other_player_state"])]
        row_index = 0
        for (label, board_state) in boards:
            y = TOP_MARGIN + row_index * ROW_SPACING
            for card_index in range(BOARD_POSITIONS):
                x = LEFT_MARGIN + card_index * COL_SPACING
                card_id = get_card_id(board_state, card_index)
                if card_id == 0:
                    pygame.draw.rect(self.screen, DARK_GRAY, (x, y, BOARD_CARD_WIDTH, BOARD_CARD_HEIGHT))
                    pygame.draw.rect(self.screen, BLACK, (x, y, BOARD_CARD_WIDTH, BOARD_CARD_HEIGHT), BORDER)
                    scaled_image = pygame.transform.scale(self.card_images[0][0], (BOARD_CARD_WIDTH, BOARD_CARD_HEIGHT))
                    if row_index == 0:
                        scaled_image = pygame.transform.flip(scaled_image, True, True)
                    self.screen.blit(scaled_image, (x, y))
                else:
                    current_health = get_card_health(board_state, card_index)
                    if card_id == 9:
                        sigil = get_card_sigil_info(board_state, card_index)
                        variant = "l" if sigil == 1 else "r"
                        card_image = self.card_images[card_id][variant].get(current_health, self.card_images[card_id][variant].get(cards[card_id][1]))
                    else:
                        card_image = self.card_images[card_id].get(current_health, self.card_images[card_id].get(cards[card_id][1]))
                    scaled_image = pygame.transform.scale(card_image, (BOARD_CARD_WIDTH, BOARD_CARD_HEIGHT))
                    self.screen.blit(scaled_image, (x, y))
                    pygame.draw.rect(self.screen, BLACK, (x, y, BOARD_CARD_WIDTH, BOARD_CARD_HEIGHT), BORDER)
                indicator_rect = pygame.Rect(x, y, BOARD_CARD_WIDTH, BOARD_CARD_HEIGHT)
                self.board_position_rects.append((row_index, card_index, indicator_rect))
            row_index += 1
                

    def draw_game_end(self, text):
        """Animates a slide effect using a cos wave to reveal the final message."""
        steps = 60
        amplitude = 546
        for i in range(steps):
            t = math.pi * (i / (steps - 1))
            wave = (1 - math.cos(t)) / 2
            x = int(wave * amplitude)
            self.screen.fill(PURE_BLACK, (0, 0, x, 686))
            pygame.display.flip()
            self.clock.tick(60)
        turn_text = self.font_large.render(text, True, YELLOW)
        self.screen.blit(turn_text, (70, 70))
        pygame.display.flip()
        time.sleep(4)
        self.winner = False
    

    def reset_gui(self):
        """Resets all GUI-related values to defaults."""
        self.hand_card_rects = []
        self.draw_indicators = []
        self.board_position_rects = []
        self.end_turn_indicator = None
        self.settings_indicators = []
        self.start_game = False
        self.adaptive_mode = True
        self.visualise_moves = False
        self.winner = False
        self.defeated = False
        self.running = True


    def process_events(self):
        """
        Listens for pygame events and handles user interaction:
            - Quit events
            - Mouse clicks for card drawing, playing, board interactions
            - Right-click for viewing sigil descriptions
            - Toggling settings
            - Ending turn.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                for card_id, rect in self.draw_indicators:
                    if rect.collidepoint(mouse_x, mouse_y):
                        self.event_queue.put(("draw_card", card_id))
                for card_id, rect in self.hand_card_rects:
                    if rect.collidepoint(mouse_x, mouse_y):
                        if event.button == 3:
                            if card_id in sigil_descriptions.keys():
                                self.description = sigil_descriptions[card_id]
                            else:
                                self.description = []
                        else:
                            self.event_queue.put(("hand_card", card_id))
                for row_index, tile_id, rect in self.board_position_rects:
                    if rect.collidepoint(mouse_x, mouse_y):
                        if event.button == 3:
                            if get_current_player(self.state["board_state"]) == 1:
                                state = self.state["other_player_state"] if row_index == 0 else self.state["current_player_state"]
                            else:
                                state = self.state["current_player_state"] if row_index == 0 else self.state["other_player_state"]
                            if get_card_id(state, tile_id) in sigil_descriptions.keys():
                                self.description = sigil_descriptions[get_card_id(state, tile_id)]
                            else:
                                self.description = []
                        else:
                            self.event_queue.put(("board_position", tile_id))
                for setting, rect in self.settings_indicators:
                    if rect.collidepoint(mouse_x, mouse_y):
                        if setting == "adaptive_mode":
                            self.event_queue.put(("adaptive_mode", 0))
                            self.adaptive_mode = False if self.adaptive_mode is True else True
                        else:
                            self.event_queue.put(("visualise_moves", 0))
                            self.visualise_moves = False if self.visualise_moves is True else True
                if self.end_turn_indicator:
                    if self.end_turn_indicator.collidepoint(mouse_x, mouse_y):
                        self.event_queue.put(("end_turn", 0))
                        self.start_game = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.event_queue.put(("end_turn", 0))
                    self.start_game = True

    def draw_game(self):
        """Draws the main gameplay screen once the player has started the game."""
        self.screen.fill(DARKEST_GRAY)
        self.screen.fill(GRAY, (0, 458, 1190, 378))
        pygame.draw.rect(self.screen, (BLACK), (-3, 458, 1194, 378), BORDER)
        self.draw_health_scale()
        self.draw_player_hand()
        self.draw_drawable_indicators()
        self.draw_end_turn_bell()
        self.draw_board()
        self.draw_description()
        turn_text = self.font.render("Current Turn - {}".format("AI" if get_current_player(self.state["board_state"]) == 0 else "You"), True, (ORANGE))
        self.screen.blit(turn_text, (35, 14))

    def draw_start(self):
        """Draws the screen before the player starts the game. 
           Shows the board, settings, and the end-turn bell, but doesnt 
           display the hand or interactive UI elements that appear mid-game"""
        self.screen.fill(DARKEST_GRAY)
        self.screen.fill(GRAY, (0, 458, 1190, 378))
        pygame.draw.rect(self.screen, (BLACK), (-3, 458, 1194, 378), BORDER)
        self.draw_end_turn_bell()
        self.draw_board()
        self.draw_settings()

    def run(self):
        """The main loop for the GUI. Continously processes events, 
           then draws either the 'start' screen or the main gameplay 
           screen, depending on start_game value"""
        while True:
            self.process_events()
            if self.start_game:
                self.draw_game()
                if not self.running:
                    if self.winner:
                        self.draw_game_end("You Won.")
                    if self.defeated:
                        self.draw_game_end("You were defeated.")
                    break
            else:
                self.draw_start()
            self.clock.tick(30)
            pygame.display.flip()