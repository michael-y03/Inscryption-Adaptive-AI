import random
from data import cards, lookup_table_0blood, lookup_table_1blood, lookup_table_2blood, lookup_table_3blood, lookup_table_4blood, sigil_lookup, card_names

"""
board state representation = 
      (5 bit) - health scale --- 0b00000 = player 0 loss, 0b10100 = player 1 loss, 0b01010 = starting pos
      (1 bit) - current player turn --- 0b0 = player 0, 0b1 = player 1       
      (4 bit) - player 0 cards drawn
      (4 bit) - player 1 cards drawn
      (4 bit) - player 0 squirrels drawn
      (4 bit) - player 1 squirrels drawn

player 0 state = 
      (8bit x 4)(32bit) - player 0 tile types, current health, addition sigil info - 4bit tile type, 3 bit health, 1 bit sigil info
            --- i.e. 0b00010010 = Squirrel with 1 health, 0b00100100 = Wolf with 2 health 

player 1 state = 
      (8bit x 4)(32bit) - player 1 tile types, current health, addition sigil info - 4bit tile type, 3 bit health, 1 bit sigil info
            --- i.e. 0b00010010 = Squirrel with 1 health, 0b00100100 = Wolf with 2 health 

player 0 hand representation = 
      (4 bit x 16) - 4 bits for count of each card type, i.e. 0b0001... = 1 squirrel     
player 1 hand representation = 
      (4 bit x 16) - 4 bits for count of each card type, i.e. 0b0001... = 1 squirrel     

cards stored as list of tuples -> ID=1 => (attack=0, health=1, cost=0)
"""

# Global Variables
memo = {}

#  Getters and Setters
# General Constants
CARD_COUNT = 4
MIN_HEALTH = 0
MAX_HEALTH = 20
MIN_CARD_HEALTH = 0
MAX_CARD_HEALTH = 7
MIN_CARD_COUNT = 0
MAX_CARD_COUNT = 15

# Sigil identifer constants.
TOUCH_OF_DEATH = 0
AIRBORNE = 1
BIFURCATED_STRIKE = 2
MIGHTY_LEAP = 0
WATERBORNE = 1
FLEDGLING = 2
SHARP_QUILLS = 3
SPRINTER = 0

# Card bitwise constants
CARD_SHIFT = 8
CARD_MASK = 0b11111111
CARD_ID_SHIFT = 4
CARD_ID_MASK = 0b1111
CARD_HEALTH_SHIFT = 1
CARD_HEALTH_MASK = 0b111
CARD_SIGIL_SHIFT = 0
CARD_SIGIL_MASK = 0b1

# Hand bitwise constants
HAND_CARD_COUNT_SHIFT = 4
HAND_CARD_COUNT_MASK = 0b1111

# Board bitwise constants
BOARD_CURRENT_PLAYER_SHIFT = 5
BOARD_CURRENT_PLAYER_MASK = 0b1
BOARD_HEALTH_SHIFT = 0
BOARD_HEALTH_MASK = 0b11111
BOARD_PLAYER_0_DRAWN_RANDOM_SHIFT = 6
BOARD_PLAYER_1_DRAWN_RANDOM_SHIFT = 10
BOARD_PLAYER_DRAWN_RANDOM_MASK = 0b1111
BOARD_PLAYER_0_DRAWN_SQUIRREL_SHIFT = 14
BOARD_PLAYER_1_DRAWN_SQUIRREL_SHIFT = 18
BOARD_PLAYER_DRAWN_SQUIRREL_MASK = 0b1111



# Helper Functions

def get_card(cards, card_index):
    """Returns the card information for a given position on a player's state."""
    return (cards >> (card_index * CARD_SHIFT)) & CARD_MASK


def get_card_id(cards, card_index):
    """Returns the card id for a given position on a player's state."""
    return (get_card(cards, card_index) >> CARD_ID_SHIFT) & CARD_ID_MASK


def get_card_health(cards, card_index):
    """Returns the card health for a given position on a player's state."""
    return (get_card(cards, card_index) >> CARD_HEALTH_SHIFT) & CARD_HEALTH_MASK


def get_card_sigil_info(cards, card_index):
    """Returns the card sigil information for a given position on a player's state."""
    return (get_card(cards, card_index) >> CARD_SIGIL_SHIFT) & CARD_SIGIL_MASK


def get_card_count(hand, card_id):
    """Returns the count of a given card_id that a player has in their current hand."""
    return (hand >> (card_id * HAND_CARD_COUNT_SHIFT)) & HAND_CARD_COUNT_MASK


def get_current_player(board_state):
    """Returns the current player (0,1) in a given board state."""
    return (board_state >> BOARD_CURRENT_PLAYER_SHIFT) & BOARD_CURRENT_PLAYER_MASK


def get_health(board_state):
    """Returns the current health value in a given board state."""
    return (board_state >> BOARD_HEALTH_SHIFT) & BOARD_HEALTH_MASK


def get_drawn_cards(board_state, player):
    """Returns the number of random cards that a player has drawn in a given board state."""
    if player == 0:
        return (board_state >> BOARD_PLAYER_0_DRAWN_RANDOM_SHIFT) & BOARD_PLAYER_DRAWN_RANDOM_MASK
    else:
        return (board_state >> BOARD_PLAYER_1_DRAWN_RANDOM_SHIFT) & BOARD_PLAYER_DRAWN_RANDOM_MASK
    

def get_drawn_squirrels(board_state, player):
    """Returns the number of squirrels that a player has drawn in a given board state."""
    if player == 0:
        return (board_state >> BOARD_PLAYER_0_DRAWN_SQUIRREL_SHIFT) & BOARD_PLAYER_DRAWN_SQUIRREL_MASK
    else:
        return (board_state >> BOARD_PLAYER_1_DRAWN_SQUIRREL_SHIFT) & BOARD_PLAYER_DRAWN_SQUIRREL_MASK


def get_occupancy_4bit(player_state):
    """Returns a 4bit occupancy pattern for a given player state where
       where 1 = card occupying position and 0 = no card occupying."""
    occupancy = 0
    for tile_index in range(CARD_COUNT):
        occupant_id = get_card_id(player_state, tile_index)
        if occupant_id != 0:
            occupancy |= (1 << tile_index)

    return occupancy


def set_card_sigil_info(cards, card_index, info):
    """Sets the sigil information for a card in a player state using a given info value,
       Returns the updated player state."""
    old_card_data = get_card(cards, card_index)
    old_card_id = (old_card_data >> CARD_ID_SHIFT) & CARD_ID_MASK
    old_health = (old_card_data >> CARD_HEALTH_SHIFT) & CARD_HEALTH_MASK
    new_card_data = (old_card_id << CARD_ID_SHIFT) | (old_health << CARD_HEALTH_SHIFT) | (info & CARD_SIGIL_MASK)
    cards  &= ~(CARD_MASK << (card_index * CARD_SHIFT))
    cards  |= (new_card_data & CARD_MASK) << (card_index * CARD_SHIFT)
    return cards 


def set_card_health(cards, card_index, new_health):
    """Sets the card health for a card in a player state using a given new_health value
       Returns the updated player state."""
    new_health = max(MIN_CARD_HEALTH, min(new_health, MAX_CARD_HEALTH))
    card_data = get_card(cards, card_index)
    card_id = card_data >> CARD_ID_SHIFT
    card_sigil_info = card_data & CARD_SIGIL_MASK
    new_card_data = (card_id << CARD_ID_SHIFT) | ((new_health & CARD_HEALTH_MASK) << CARD_HEALTH_SHIFT) | card_sigil_info
    new_cards = (cards & ~(CARD_MASK << (card_index * CARD_SHIFT))) | (new_card_data << (card_index * CARD_SHIFT))
    return new_cards


def set_card_count(hand, card_id, count):
    """Sets the count of a card_id in a player's hand using a given count value, returns the updated hand."""
    count = max(MIN_CARD_COUNT, min(count, MAX_CARD_COUNT))
    return (hand & ~(HAND_CARD_COUNT_MASK << (card_id * HAND_CARD_COUNT_SHIFT))) | (count << (card_id * HAND_CARD_COUNT_SHIFT))


def set_health(board_state, new_health):
    """Sets the player health in a board_state with a given new_health value, returns the updated board_state."""
    new_health = max(MIN_HEALTH, min(new_health, MAX_HEALTH))
    board_state &= ~BOARD_HEALTH_MASK
    board_state |= new_health
    return board_state
    

def set_drawn_squirrels(board_state):
    """Increments the drawn squirrels value for the current player in a given board state."""
    player = get_current_player(board_state)
    count = max(MIN_CARD_COUNT, min(get_drawn_squirrels(board_state, player)+1, MAX_CARD_COUNT))
    if player == 0:
        board_state &= ~(BOARD_PLAYER_DRAWN_SQUIRREL_MASK << BOARD_PLAYER_0_DRAWN_SQUIRREL_SHIFT)
        board_state |= (count << BOARD_PLAYER_0_DRAWN_SQUIRREL_SHIFT)
    else:
        board_state &= ~(BOARD_PLAYER_DRAWN_SQUIRREL_MASK << BOARD_PLAYER_1_DRAWN_SQUIRREL_SHIFT)
        board_state |= (count << BOARD_PLAYER_1_DRAWN_SQUIRREL_SHIFT)
    return board_state


def set_drawn_cards(board_state):
    """Increments the drawn random cards value for the current player in a given board state."""
    player = get_current_player(board_state)
    count = max(MIN_CARD_COUNT, min(get_drawn_cards(board_state, player)+1, MAX_CARD_COUNT))
    if player == 0:
        board_state &= ~(BOARD_PLAYER_DRAWN_RANDOM_MASK << BOARD_PLAYER_0_DRAWN_RANDOM_SHIFT)
        board_state |= (count << BOARD_PLAYER_0_DRAWN_RANDOM_SHIFT)
    else:
        board_state &= ~(BOARD_PLAYER_DRAWN_RANDOM_MASK << BOARD_PLAYER_1_DRAWN_RANDOM_SHIFT)
        board_state |= (count << BOARD_PLAYER_1_DRAWN_RANDOM_SHIFT)
    return board_state


def set_card(state, card_index, tile_value):
    """Helper function that updates the card value at a given index using a new value."""
    state &= ~(CARD_MASK << (card_index * CARD_SHIFT))
    state |= (tile_value & CARD_MASK) << (card_index * CARD_SHIFT)
    return state


def count_current_player_cards(player_state):
    """Returns the number of cards that a player has in a given player state."""
    card_count = 0
    for card_index in range(CARD_COUNT):
        occupant_id = get_card_id(player_state, card_index)
        if occupant_id != 0:
            card_count += 1
    return card_count


def remove_card(player_state, card_index):
    """Removes a card in a player state using a given card index."""
    return set_card(player_state, card_index, 0)


def remove_cards_in_difference(player_state, starting_occupancy, new_occupancy):
    """Calculates the difference between 2 occupancy patterns, then removes the cards where 
       the occupancy has changed in a given player state."""
    difference = starting_occupancy & (~new_occupancy & CARD_ID_MASK)
    for card_index in range(CARD_COUNT):
        if difference & (1 << card_index):
            player_state = remove_card(player_state, card_index)
    return player_state


def state_to_key(s):
    """Given a state, returns a tuple for use as a key."""
    return (
        s["board_state"],
        s["current_player_state"],
        s["current_player_hand"],
        s["other_player_state"],
        s["other_player_hand"],
        tuple(s["p0_draws"]),
        tuple(s["p1_draws"])
    )


def key_to_state(key):
    """Given a key, returns a dictionary for use as a state."""
    return {
        "board_state": key[0],
        "current_player_state": key[1],
        "current_player_hand": key[2],
        "other_player_state": key[3],
        "other_player_hand": key[4],
        "p0_draws": list(key[5]),
        "p1_draws": list(key[6])
    }



#   Game Functions

def play_card(player_state, hand, card_id, card_index):
    """Plays a card at a card location in a players state and removes it from their hand."""
    default_health = cards[card_id][1] & CARD_HEALTH_MASK
    sigil_info = 0
    card_data = (card_id << CARD_ID_SHIFT) | (default_health << CARD_HEALTH_SHIFT) | sigil_info
    player_state = set_card(player_state, card_index, card_data)
    new_hand = set_card_count(hand, card_id, max(0, get_card_count(hand, card_id) - 1))
    return player_state, new_hand


def place_card(player_state, card_id, card_index):
    """Plays a card at a card location in a players state."""
    default_health = cards[card_id][1] & CARD_HEALTH_MASK
    sigil_info = 0
    card_data = (card_id << CARD_ID_SHIFT) | (default_health << CARD_HEALTH_SHIFT) | sigil_info
    return set_card(player_state, card_index, card_data)


def move_card(player_state, from_index, to_index):
    """Moves a card from a location on a players state, to another location"""
    card_data = get_card(player_state, from_index)
    player_state = set_card(player_state, from_index, 0)
    player_state = set_card(player_state, to_index, card_data)
    return player_state


def initialise_gamestate():
    """Initialises the state dictionary for future use."""
    health = 10
    turn = 0
    p0_drawn = 2
    p1_drawn = 2
    p0_squirrels_drawn = 1
    p1_squirrels_drawn = 1
    player_0_state = 0
    player_1_state = 0
    hand_p0_state = 0
    hand_p1_state = 0
    board_state = (health) | (turn << BOARD_CURRENT_PLAYER_SHIFT) | (p0_drawn << BOARD_PLAYER_0_DRAWN_RANDOM_SHIFT) | (p1_drawn << BOARD_PLAYER_1_DRAWN_RANDOM_SHIFT) | (p0_squirrels_drawn << BOARD_PLAYER_0_DRAWN_SQUIRREL_SHIFT) | (p1_squirrels_drawn << BOARD_PLAYER_1_DRAWN_SQUIRREL_SHIFT)
    p0_draws = [random.randint(3, len(card_names)) for _ in range(12)]  # Only needs 10 random card id's : 12 added for good luck.
    p1_draws = [random.randint(3, len(card_names)) for _ in range(12)]  # ^
    hand_p0_state = set_card_count(hand_p0_state, 1, 1)
    hand_p1_state = set_card_count(hand_p1_state, 1, 1)
    for x in range(2):
        draw_id = p0_draws[x]
        hand_p0_state = set_card_count(hand_p0_state, draw_id, get_card_count(hand_p0_state, draw_id)+1)
    for x in range(2):
        draw_id = p1_draws[x]
        hand_p1_state = set_card_count(hand_p1_state, draw_id, get_card_count(hand_p1_state, draw_id)+1)
    state = {
        "board_state": board_state,
        "current_player_state": player_0_state,
        "other_player_state": player_1_state,
        "current_player_hand": hand_p0_state,
        "other_player_hand": hand_p1_state,
        "p0_draws": p0_draws,
        "p1_draws": p1_draws,
    }
    return state


def switch_player(state):
    """Flips the current player and switches the current player state and hand, 
       with the other player state and hand of a state."""
    new_turn = state["board_state"] ^ (1 << BOARD_CURRENT_PLAYER_SHIFT)
    switched_state = {
                "board_state": new_turn,
                "current_player_state": state["other_player_state"],
                "current_player_hand": state["other_player_hand"],
                "other_player_state": state["current_player_state"],
                "other_player_hand": state["current_player_hand"],
                "p0_draws": state["p0_draws"],
                "p1_draws": state["p1_draws"]
            }
    return switched_state


def draw_squirrel(hand):
    """Adds a squirrel card to the given hand."""
    return set_card_count(hand, 1, get_card_count(hand, 1)+1)


def get_draw_options(player_state, hand, canDraw, draw_id, squirrel_drawable):
    """
    For use in next_states().
    Determines the drawing options for a given state.

    Parameters:
        player_state (int): The current players board state.
        hand (int): The current players hand representation.
        canDraw (bool): Whether or not the player can draw a card.
        draw_id (int): The card id for a random draw (or 0 if not applicable).
        squirrel_drawable (int): Indicator for if drawing a squirrel is allowed.

    Returns:
        list of tuples: Each tuple represents an option in the form
            (player_state, hand, draw_id, squirrel_drawable), where
            draw_id or squirrel_drawable may be set to -1 if a draw action is taken
    """
    if canDraw:
        if draw_id != 0 and squirrel_drawable == 1:  # Can draw random card or squirrel
            return [
                (player_state, draw_squirrel(hand), draw_id, -1),
                (player_state, set_card_count(hand, draw_id, get_card_count(hand, draw_id) + 1), -1, squirrel_drawable)
            ]
        elif draw_id == 0 and squirrel_drawable == 1:  # Can't draw random card but can draw squirrel
            return [(player_state, draw_squirrel(hand), draw_id, -1)]
        elif draw_id != 0 and squirrel_drawable != 1:  # Can draw random card but can't draw squirrel
            return [(player_state, set_card_count(hand, draw_id, get_card_count(hand, draw_id) + 1), -1, squirrel_drawable)]
        else:  # Cant draw anything
            return [(player_state, hand, draw_id, squirrel_drawable)]
    else:
        return [(player_state, hand, draw_id, squirrel_drawable)]


def next_states(player_state, hand, canDraw, draw_id, squirrel_drawable):
    """
    Recursively generates all possible next states from the current state.

    This function explores the state space by calculating the avaliable drawing options
    and potential card plays based on card lookup tables and the current states occupancy. It uses
    memoisation to cache previously computed states for efficiency.

    Parameters:
        player_state (int): The current player's board state as a bitfield.
        hand (int): The current player's hand representation as a bitfield.
        canDraw (bool): Indicates whether the player is allowed to draw a card.
        draw_id (int): The card id for a random draw (or 0 if not applicable).
        squirrel_drawable (int): Indicator (typically 1 if allowed) specifying if drawing a 
                                 squirrel is permitted.

    Returns:
        list of tuples: a list of possible next states in the form
            (player_state, hand, draw_id, squirrel_drawable), where
            draw_id or squirrel_drawable may be set to -1 if a draw action is taken

    """
    state_hash = (player_state, hand, canDraw, draw_id, squirrel_drawable)
    if state_hash in memo:
        return memo[state_hash]
    
    ns = []
    max_blood = count_current_player_cards(player_state)
    ns = get_draw_options(player_state, hand, canDraw, draw_id, squirrel_drawable)
    child_states = []

    for (temp_player_state_option, temp_hand_option, id, sd) in ns:
        starting_occupancy = get_occupancy_4bit(temp_player_state_option)
        for card_id in range(1, len(cards)):
            card_count = get_card_count(temp_hand_option, card_id)
            if card_count > 0:
                blood = cards[card_id][2]
                if blood <= max_blood:
                    lookup_table = lookup_table_0blood if blood == 0 else lookup_table_1blood if blood == 1 else lookup_table_2blood if blood == 2 else lookup_table_3blood if blood == 3 else lookup_table_4blood

                    lookup = lookup_table[starting_occupancy]
                    for (new_occupancy, placement_index) in lookup:
                        temp_player_state = remove_cards_in_difference(temp_player_state_option, starting_occupancy, new_occupancy)
                        temp_player_state, temp_hand = play_card(temp_player_state, temp_hand_option, card_id, placement_index)

                        states = next_states(temp_player_state, temp_hand, False, id, sd)
                        child_states.extend(states)
    ns.extend(child_states)
    unique_children = list(set(ns))
    memo[state_hash] = unique_children  
    return unique_children


def touch_of_death(current_player_state, other_player_state, board_state, card, attack):
    """Overrides the base attack calculation in apply_turn so that if a card with this sigil
       attacks another card it kills it, else it changes the health by its base amount of damage."""
    other_card = get_card_id(other_player_state, card)
    if other_card and WATERBORNE not in sigil_lookup[other_card][1]:
        other_player_state = remove_card(other_player_state, card)
    else:
        health = get_health(board_state)
        board_state = set_health(board_state, (health - attack) if get_current_player(board_state) == 0 else (health + attack))
    return current_player_state, other_player_state, board_state


def sprinter(current_player_state, card):
    """Moves a card on the given player state to one of its adjacent sides if possible,
       depending on its sigil information."""
    sigil_info = get_card_sigil_info(current_player_state, card)
    if sigil_info == 0:
        sigil_info = 1
    else:
        sigil_info = -1
    for _ in range(2):
        if card + sigil_info <= 3 and card + sigil_info >= 0:
            if not get_card_id(current_player_state, card+sigil_info):
                current_player_state = move_card(current_player_state, card, card+sigil_info)
                current_player_state = set_card_sigil_info(current_player_state, card+sigil_info, 0 if sigil_info == 1 else 1)
                return current_player_state
            else:
                sigil_info *= -1
        else:
            sigil_info *= -1
    return current_player_state


def airborne(current_player_state, other_player_state, board_state, card, attack):
    """Overrides the base attack calculation in apply_turn so that this card only directly 
       attacks either the opponent or other cards with the mighty leap sigil."""
    other_card = get_card_id(other_player_state, card)
    if other_card and MIGHTY_LEAP in sigil_lookup[other_card][1]:
        other_health = get_card_health(other_player_state, card)
        if other_health > attack:
            other_player_state = set_card_health(other_player_state, card, other_health-attack)
        else:
            other_player_state = remove_card(other_player_state, card)
        return current_player_state, other_player_state, board_state
    health = get_health(board_state)
    board_state = set_health(board_state, (health - attack) if get_current_player(board_state) == 0 else (health + attack))
    return current_player_state, other_player_state, board_state


def bifurcated_strike(current_player_state, other_player_state, board_state, card, attack):
    """Overrides the base attack calculation in apply_turn so that this card attacks the opponent in 
       position card=-1,+1 instead of card."""
    positions = []
    if card > 0:
        positions.append(card-1)
    if card < 3:
        positions.append(card+1)
    for position in positions:
        other_card = get_card_id(other_player_state, position)
        if other_card and AIRBORNE not in sigil_lookup[other_card][1]:
            other_health = get_card_health(other_player_state, position)
            if other_health > attack:
                other_player_state = set_card_health(other_player_state, position, other_health-attack)
            else:
                other_player_state = remove_card(other_player_state, position)
        else:
            health = get_health(board_state)
            board_state = set_health(board_state, (health - attack) if get_current_player(board_state) == 0 else (health + attack))
    return current_player_state, other_player_state, board_state


def sharp_quills(current_player_state, other_player_state, board_state, card, attack):
    """Overrides the base attack calculation (if opponent card has sigil sharp quills) so that
       when a the current player attacks this card, the current players card is dealt 1 damage.
       If both players cards have sharp quills, this triggers back and forth activation. Until one
       the cards dies."""
    other_health = get_card_health(other_player_state, card)
    if other_health > attack:
        other_player_state = set_card_health(other_player_state, card, other_health-attack)
        if SHARP_QUILLS in sigil_lookup[get_card_id(current_player_state, card)][1]:
            while True:
                if get_card_health(current_player_state, card) > 1:
                    current_player_state = set_card_health(current_player_state, card, get_card_health(current_player_state, card)-1)
                    if get_card_health(other_player_state, card) > 1:
                        other_player_state = set_card_health(other_player_state, card, get_card_health(other_player_state, card)-1)
                    else:
                        other_player_state = remove_card(other_player_state, card)
                        return current_player_state, other_player_state, board_state
                else:
                    current_player_state = remove_card(current_player_state, card)
                    return current_player_state, other_player_state, board_state
        if get_card_health(current_player_state, card) > 1:
            current_player_state = set_card_health(current_player_state, card, get_card_health(current_player_state, card)-1)
        else:
            current_player_state = remove_card(current_player_state, card)
    else:
        other_player_state = remove_card(other_player_state, card)
        if get_card_health(current_player_state, card) > 1:
            current_player_state = set_card_health(current_player_state, card, get_card_health(current_player_state, card)-1)
        else:
            current_player_state = remove_card(current_player_state, card)
    return current_player_state, other_player_state, board_state
            

def apply_turn(current_player_state, other_player_state, board_state):
    """Given a current_player_state, opponent state and board state, simulates the effects of
       applying (ending) their turn and the resulting player/card healths after attacking."""
    c = []
    for card in range(4):
        if get_card_id(current_player_state, card):
            c.append(card)
    for card in c:
        attack = cards[get_card_id(current_player_state, card)][0]
        if attack != 0:
            attack_sigils = sigil_lookup[get_card_id(current_player_state, card)][0]
            if attack_sigils:
                for sigil in attack_sigils:
                    if sigil == TOUCH_OF_DEATH:
                        current_player_state, other_player_state, board_state = touch_of_death(current_player_state, other_player_state, board_state, card, attack) 
                    elif sigil == AIRBORNE:
                        current_player_state, other_player_state, board_state = airborne(current_player_state, other_player_state, board_state, card, attack) 
                    elif sigil == BIFURCATED_STRIKE:
                        current_player_state, other_player_state, board_state = bifurcated_strike(current_player_state, other_player_state, board_state, card, attack) 
            else:
                other_card = get_card_id(other_player_state, card)
                if other_card and AIRBORNE not in sigil_lookup[other_card][1]:
                    other_health = get_card_health(other_player_state, card)
                    if SHARP_QUILLS in sigil_lookup[other_card][1]:
                        current_player_state, other_player_state, board_state = sharp_quills(current_player_state, other_player_state, board_state, card, attack)                            
                    elif other_health > attack:
                        other_player_state = set_card_health(other_player_state, card, other_health-attack)
                    else:
                        other_player_state = remove_card(other_player_state, card)
                else:
                    health = get_health(board_state)
                    board_state = set_health(board_state, (health - attack) if get_current_player(board_state) == 0 else (health + attack))
        on_turn_end_sigils = sigil_lookup[get_card_id(current_player_state, card)][2]
        for sigil in on_turn_end_sigils:
            if sigil == SPRINTER:
                current_player_state = sprinter(current_player_state, card) 
    for x in range(CARD_COUNT):
        card_id = get_card_id(other_player_state, x)
        if card_id and FLEDGLING in sigil_lookup[card_id][1]:
            other_player_state = place_card(other_player_state, 2, x)
    return current_player_state, other_player_state, board_state


def is_game_over(board_state):
    """Returns True if either player has died, else False"""
    if get_health(board_state) <= 0 or get_health(board_state) >= 20:
        return True