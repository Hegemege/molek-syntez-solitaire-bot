import PIL
import pyscreenshot as ImageGrab
import time
import functools
import math
from pynput.mouse import Button, Controller

from game_state import GameState, STACK_COUNT, INITIAL_STACK_SIZE, MAX_STACK_SIZE

# Constants used to crop the game view from the whole screen
# Works properly if game is in native resolution

GAME_WIDTH = 1300
GAME_HEIGHT = 870

# Will be calculated by code
GAME_LEFT = 1000
GAME_TOP = 500

# Image parsing parameters
BOARD_TOP_LEFT = (168, 183)
BOARD_HORIZONTAL_DELIMITER = 164
BOARD_VERTICAL_DELIMITER = 32

CARD_VALUE_OFFSET = (10, 10)
CARD_VALUE_SIZE = (16, 18)

# Card identification parameters
COLOR_MATCH_THRESHOLD = 2

CARD_LOOKUP = {}
CARD_LOOKUP[6] = (100, 100, 100)
CARD_LOOKUP[7] = (100, 100, 100)
CARD_LOOKUP[8] = (100, 100, 100)
CARD_LOOKUP[9] = (100, 100, 100)
CARD_LOOKUP[10] = (100, 100, 100)
CARD_LOOKUP[11] = (100, 100, 100)
CARD_LOOKUP[12] = (100, 100, 100)
CARD_LOOKUP[13] = (100, 100, 100)
CARD_LOOKUP[14] = (100, 100, 100)

# Autoplay parmeters
CLICK_STACKS = [[(0, 0) for j in range(MAX_STACK_SIZE)]
                for i in range(STACK_COUNT)]

MAX_SOLUTION_LENGTH = 100

REPLAY_WAIT_BETWEEN_ACTIONS = 0.06
REPLAY_MOUSE_MOVE_TIME = 0.06
REPLAY_COLLAPSE_WAIT_TIME = 0.50


def main():
    intro_print()
    # time.sleep(5)

    solve()


def intro_print():
    """
        Prints introductory test of the program's features
    """
    print("Launching in 5 seconds")
    print("Make sure the game is opened in fullscreen on the main window")
    print("To exit, close the script between games")


def solve():
    """
        Solves the current game configuration
    """
    image = ImageGrab.grab()
    image = crop(image)

    image = PIL.Image.open("reference.bmp")

    # Initialize the beginning game state
    state = GameState()

    # Parse the image and populate the state
    populate_state(image, state)

    return

    # Setup lookups and other structures for the main solving loop
    state_history = {}
    search_stack = []

    # Initialize the search stack
    search_stack.append((state, [], 0))
    shortest_solution = [0 for i in range(10000)]

    original_state = state.clone()
    highest_heuristic = -999

    # Start the main solving loop
    states_searched = 0

    while True:
        if len(search_stack) == 0 and len(state_history) > 0:
            print("Unable to find solution")
            break

        # Take state from the end of stack
        current_search_item = search_stack.pop()
        current_state = current_search_item[0]
        current_history = current_search_item[1]

        # End searches that run too deep
        if len(current_history) > MAX_SOLUTION_LENGTH:
            continue

        if current_state.is_won():
            print("New solution")
            print("Length:", len(current_history))
            print("States searched:", states_searched)
            print("Stack size:", len(search_stack))
            print()
            break

        current_actions = current_state.get_legal_actions()

        for action in current_actions:
            clone = current_state.clone()
            clone.apply_action(action)

            # Hash the state, make sure we don't revisit a state
            clone_hash = hash(clone)
            if clone_hash in state_history:
                if state_history[clone_hash] == clone:
                    continue
            state_history[clone_hash] = clone

            heuristic_score = clone.get_heuristic_value()

            if heuristic_score >= highest_heuristic:
                highest_heuristic = heuristic_score
                shortest_solution = current_history + [action]
                shortest_solution_suit_order = clone.suit_insert_order

            new_history = list(current_history)
            new_history += [action]

            search_stack.append((clone, new_history, heuristic_score))
            states_searched += 1

    replay_actions(shortest_solution)


def replay_actions(actions):
    """
        Plays the solved actions on the board
    """
    mouse = Controller()

    print("Replaying", len(actions), "actions")
    time.sleep(0.5)

    # Click on the area once to make sure the first click doesn't get captured by window focus
    #drag_from_to(mouse, CLICK_OPEN_SLOTS[0], CLICK_OPEN_SLOTS[1])
    time.sleep(0.5)

    for action in actions:
        print(action)

        # Stack to stack
        from_position = CLICK_STACKS[action[0][0]][action[0][1]]
        # Always drag onto the 6th card, which will cover all vertical positions
        # TODO test
        to_position = CLICK_STACKS[action[1][1]][5]
        drag_from_to(mouse, from_position, to_position)


def click_on(mouse, position):
    screen_position = game_to_screen(position)
    mouse.position = screen_position
    time.sleep(REPLAY_MOUSE_MOVE_TIME)
    mouse.click(Button.left, 1)
    time.sleep(REPLAY_MOUSE_MOVE_TIME)


def drag_from_to(mouse, from_position, to_position):
    screen_from_position = game_to_screen(from_position)
    screen_to_position = game_to_screen(to_position)
    mouse.position = screen_from_position
    time.sleep(REPLAY_MOUSE_MOVE_TIME)
    mouse.press(Button.left)
    time.sleep(REPLAY_MOUSE_MOVE_TIME)
    mouse.position = screen_to_position
    time.sleep(REPLAY_MOUSE_MOVE_TIME)
    mouse.release(Button.left)
    time.sleep(REPLAY_MOUSE_MOVE_TIME)


def crop(image):
    """
        Crop the image to only contain the game view
        Define the game view as a defined rectangle around the center of the screen
        Assume the game is in native resolution
        Confirmed to work in 1080p and 1440p
    """
    global GAME_LEFT
    global GAME_TOP

    width = image.size[0]
    height = image.size[1]
    game_width = GAME_WIDTH
    game_height = GAME_HEIGHT

    GAME_LEFT = (width - game_width)/2.0
    GAME_TOP = (height - game_height)/2.0

    return image.crop((GAME_LEFT, GAME_TOP, width - GAME_LEFT, height - GAME_TOP))


def populate_state(image, state):
    """
        Parse the image and populate the given game state
    """

    sampled_colors = {}

    # Loop through the board and extract color data from card values
    for i in range(STACK_COUNT):
        for j in range(MAX_STACK_SIZE):
            left = BOARD_TOP_LEFT[0] + i * \
                BOARD_HORIZONTAL_DELIMITER + CARD_VALUE_OFFSET[0]
            top = BOARD_TOP_LEFT[1] + j * \
                BOARD_VERTICAL_DELIMITER + CARD_VALUE_OFFSET[1]

            CLICK_STACKS[i][j] = (left, top)

            if j >= INITIAL_STACK_SIZE:
                continue

            right = left + CARD_VALUE_SIZE[0]
            bottom = top + CARD_VALUE_SIZE[1]
            card_value = image.crop((left, top, right, bottom))

            card_value.save("slot_" + str(i) + "_" + str(j) + ".bmp")

            # Get avg from top left corner
            top_left_avg = sample_avg_color(card_value, (2, 2))

            # Get overall color average
            pixels = list(card_value.getdata())
            avg_color = avg_color_list(pixels)

            comb_color = avg_color + top_left_avg

            sampled_colors[(i, j)] = comb_color

    position_lookup = {}

    # Find the card colors and values
    for position in sampled_colors:
        comb_color = sampled_colors[position]

        found = False

        # Go through all color settings and try to find the correct one, that is as close to the given values as possible
        for suit in CARD_LOOKUP:
            if found:
                break
            suit_cards = CARD_LOOKUP[suit]
            for card_index in range(len(suit_cards)):
                comparison_color = suit_cards[card_index]

                # Split the 6-tuples into 3-tuples
                sampled_avg_color = comb_color[:3]
                sampled_check_color = comb_color[3:]

                comparison_avg_color = comparison_color[:3]
                comparison_check_color = comparison_color[3:]

                # Test if the colors are close to each other. Store the card position
                if color_distance(sampled_avg_color, comparison_avg_color) < COLOR_MATCH_THRESHOLD and color_distance(sampled_check_color, comparison_check_color) < COLOR_MATCH_THRESHOLD:
                    position_lookup[position] = (suit, card_index)
                    found = True
                    break

    for position in sorted(position_lookup.keys()):
        stack_index = position[0]
        state.parse_card_into_stack(stack_index, position_lookup[position])


def sample_avg_color(image, position):
    """
        Sample an average color from the image at the given position
        Averages a 3x3 kernel around the pixel
    """
    kernel = []
    topleft = (position[0] - 1, position[1] - 1)
    for i in range(3):
        for j in range(3):
            kernel.append(image.getpixel((topleft[0] + j, topleft[1] + i)))
    return avg_color_list(kernel)


def avg_color_list(color_list):
    """
        Returns the average color of the given list of 3-tuples
    """
    colors = tuple(functools.reduce(lambda x, y: tuple(
        map(lambda a, b: a + b, x, y)), color_list))
    colors = tuple(map(lambda x: x // len(color_list), colors))
    return colors


def color_distance(from_color, to_color):
    """
        Calculate the euclidean distance of two colors in 3D space
    """
    return math.sqrt((from_color[0] - to_color[0]) ** 2 + (from_color[1] - to_color[1]) ** 2 + (from_color[2] - to_color[2]) ** 2)


def game_to_screen(position):
    """
        Converts coordinates from game view into screen coordinates for mouse interaction
    """
    return (GAME_LEFT + position[0], GAME_TOP + position[1])


if __name__ == "__main__":
    main()
