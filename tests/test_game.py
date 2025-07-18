import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.insert(0, parent_dir)
import game


def run_tests():
    test_get_card()
    test_get_card_id()
    test_get_card_health()
    test_get_card_sigil_info()
    test_get_card_count()
    test_get_current_player()
    test_get_health()
    test_get_drawn_cards()
    test_get_drawn_squirrels()
    test_get_occupancy_4bit()
    test_set_card_sigil_info()
    test_set_card_health()
    test_set_card_count()
    test_set_health()
    test_set_drawn_squirrels()
    test_set_drawn_cards()
    test_set_card()
    test_count_current_player_cards()
    test_remove_card()
    test_remove_cards_in_difference()
    test_play_card()
    test_place_card()
    test_move_card()
    test_initialise_gamestate()
    test_switch_player()
    test_draw_squirrel()
    test_get_draw_options()
    test_next_states()
    test_touch_of_death()
    test_sprinter()
    test_airborne()
    test_bifurcated_strike()
    test_sharp_quills()
    test_apply_turn()
    print("All tests passed!")

def test_get_card():
    current_player_state = 0b00110010000000000000000000000000
    card_index = 1
    result = game.get_card(current_player_state, card_index)
    assert result == 0b00000000  # No card
    card_index = 3
    result = game.get_card(current_player_state, card_index)
    assert result == 0b00110010  # Wolf cub with 1 health, sigil_info 0.

def test_get_card_id():
    current_player_state = 0b00110010000000000000000000000000
    card_index = 1
    result = game.get_card_id(current_player_state, card_index)
    assert result == 0  # No card
    card_index = 3
    result = game.get_card_id(current_player_state, card_index)
    assert result == 3  # Wolf cub with 1 health, sigil_info 0.

def test_get_card_health():
    current_player_state = 0b00110010000000000000000000000000
    card_index = 1
    result = game.get_card_health(current_player_state, card_index)
    assert result == 0  # No card
    card_index = 3
    result = game.get_card_health(current_player_state, card_index)
    assert result == 1  # Wolf cub with 1 health, sigil_info 0.

def test_get_card_sigil_info():
    current_player_state = 0b00110011000000000000000000000000
    card_index = 1
    result = game.get_card_sigil_info(current_player_state, card_index)
    assert result == 0  # No card
    card_index = 3
    result = game.get_card_sigil_info(current_player_state, card_index)
    assert result == 1  # Wolf cub with 1 health, sigil_info 1.

def test_get_card_count():
    current_player_hand = (1 << (1 * game.HAND_CARD_COUNT_SHIFT)) | (8 << (12 * game.HAND_CARD_COUNT_SHIFT))
    card_id = 1
    result = game.get_card_count(current_player_hand, card_id)
    assert result == 1
    card_id = 12
    result = game.get_card_count(current_player_hand, card_id)
    assert result == 8

def test_get_current_player():
    board_state = 0b0000000000000000101010
    result = game.get_current_player(board_state)
    assert result == 1

def test_get_health():
    board_state = 0b0000000000000000101010
    result = game.get_health(board_state)
    assert result == 10

def test_get_drawn_cards():
    board_state = 0b00000000000000100101010
    player = 0
    result = game.get_drawn_cards(board_state, player)
    assert result == 4

def test_get_drawn_squirrels():
    board_state = 0b00000000100000100101010
    player = 0
    result = game.get_drawn_squirrels(board_state, player)
    assert result == 1

def test_get_occupancy_4bit():
    current_player_state = 0b00110010000000000000000000000000
    result = game.get_occupancy_4bit(current_player_state)
    assert result == 0b1000

def test_set_card_sigil_info():
    current_player_state = 0b00110010000000000000000000000000
    expected_player_state = 0b00110011000000000000000000000000
    card_index = 3
    result = game.set_card_sigil_info(current_player_state, card_index, 1)
    assert result == expected_player_state

def test_set_card_health():
    current_player_state = 0b00110010000000000000000000000000
    expected_player_state = 0b00111010000000000000000000000000
    card_index = 3
    result = game.set_card_health(current_player_state, card_index, 5)
    assert result == expected_player_state

def test_set_card_count():
    current_player_hand = (1 << (1 * game.HAND_CARD_COUNT_SHIFT)) | (8 << (12 * game.HAND_CARD_COUNT_SHIFT))
    expected_current_player_hand = (5 << (1 * game.HAND_CARD_COUNT_SHIFT)) | (8 << (12 * game.HAND_CARD_COUNT_SHIFT))
    card_id = 1
    result = game.set_card_count(current_player_hand, card_id, 5)
    assert result == expected_current_player_hand

def test_set_health():
    board_state = 0b0000000000000000101010
    expected_board_state = 0b0000000000000000100010
    result = game.set_health(board_state, 2)
    assert result == expected_board_state

def test_set_drawn_squirrels():
    board_state = 0b0000000000000000001010
    expected_board_state = 0b0000000100000000001010
    result = game.set_drawn_squirrels(board_state)
    assert result == expected_board_state

def test_set_drawn_cards():
    board_state = 0b0000000000000000001010
    expected_board_state = 0b0000000000000001001010
    result = game.set_drawn_cards(board_state)
    assert result == expected_board_state

def test_set_card():
    current_player_state = 0b00110010000000000000000000000000
    expected_player_state = 0b00110010000000000010010000000000
    card_index = 1
    card = 0b00100100
    result = game.set_card(current_player_state, card_index, card)
    assert result == expected_player_state

def test_count_current_player_cards():
    current_player_state = 0b00110010000000000000000000000000
    result = game.count_current_player_cards(current_player_state)
    assert result == 1

def test_remove_card():
    current_player_state = 0b00110010000000000010010000000000
    expected_player_state = 0b00110010000000000000000000000000
    card_index = 1
    result = game.remove_card(current_player_state, card_index)
    assert result == expected_player_state

def test_remove_cards_in_difference():
    current_player_state = 0b00110010000000000010010000000000
    expected_player_state = 0b00110010000000000000000000000000
    starting_occupancy = 0b1010
    new_occupancy = 0b1000
    result = game.remove_cards_in_difference(current_player_state, starting_occupancy, new_occupancy)
    assert result == expected_player_state

def test_play_card():
    current_player_state = 0b00000000000000000000000000000000
    expected_player_state = 0b00110010000000000000000000000000
    current_player_hand = (1 << (1 * game.HAND_CARD_COUNT_SHIFT)) | (1 << (3 * game.HAND_CARD_COUNT_SHIFT))
    expected_player_hand = (1 << (1 * game.HAND_CARD_COUNT_SHIFT))
    card_id = 3
    card_index = 3
    result_player_state, result_player_hand = game.play_card(current_player_state, current_player_hand, card_id, card_index)
    assert result_player_state == expected_player_state
    assert result_player_hand == expected_player_hand

def test_place_card():
    current_player_state = 0b00000000000000000000000000000000
    expected_player_state = 0b00110010000000000000000000000000
    card_id = 3
    card_index = 3
    result = game.place_card(current_player_state, card_id, card_index)
    assert result == expected_player_state

def test_move_card():
    current_player_state = 0b00110010000000000000000000000000
    expected_player_state = 0b00000000000000000000000000110010
    from_index = 3
    to_index = 0
    result = game.move_card(current_player_state, from_index, to_index)
    assert result == expected_player_state

def test_initialise_gamestate():
    state = game.initialise_gamestate()
    assert state["board_state"] == 0b0001000100100010001010
    assert state["current_player_state"] == 0
    assert state["other_player_state"] == 0
    assert len(state["p0_draws"]) >= 10
    assert len(state["p1_draws"]) >= 10

def test_switch_player():
    state = game.initialise_gamestate()
    result = game.switch_player(state)
    assert result["board_state"] == 0b0001000100100010101010
    assert result["current_player_state"] == state["other_player_state"]
    assert result["other_player_state"] == state["current_player_state"]
    assert result["current_player_hand"] == state["other_player_hand"]
    assert result["other_player_hand"] == state["current_player_hand"]

def test_draw_squirrel():
    current_player_hand = (1 << (1 * game.HAND_CARD_COUNT_SHIFT))
    expected_player_hand = (2 << (1 * game.HAND_CARD_COUNT_SHIFT))
    result = game.draw_squirrel(current_player_hand)
    assert result == expected_player_hand

def test_get_draw_options():
    current_player_state = 0b00000000000000000000000000000000
    current_player_hand = (1 << (1 * game.HAND_CARD_COUNT_SHIFT))
    canDraw = True
    draw_id = 0
    squirrel_drawable = 1

    result = game.get_draw_options(current_player_state, current_player_hand, canDraw, draw_id, squirrel_drawable)
    assert result == [(current_player_state, game.draw_squirrel(current_player_hand), draw_id, -1)]

def test_next_states():
    current_player_state = 0b00000000000000000000000000000000
    current_player_hand = (1 << (1 * game.HAND_CARD_COUNT_SHIFT))
    canDraw = True
    draw_id = 0
    squirrel_drawable = 1
    expected_result = [(1179666, 0, 0, -1), (18, 16, 0, -1), (4608, 16, 0, -1), (301989888, 16, 0, -1), (301989906, 0, 0, -1), (4626, 0, 0, -1), (1184256, 0, 0, -1), (301994496, 0, 0, -1), (0, 32, 0, -1), (1179648, 16, 0, -1), (303169536, 0, 0, -1)]
    result = game.next_states(current_player_state, current_player_hand, canDraw, draw_id, squirrel_drawable)
    assert result == expected_result

def test_touch_of_death():
    current_player_state = 0b10000010000000000000000000000000
    other_player_state = 0b00110010000000000000000000000000
    expected_other_player_state = 0b00000000000000000000000000000000
    board_state = 0b0001000100100010001010
    card_index = 3
    attack = 1
    result_current_player_state, result_other_player_state, result_board_state = game.touch_of_death(current_player_state, other_player_state, board_state, card_index, attack)
    assert result_current_player_state == current_player_state
    assert result_other_player_state == expected_other_player_state
    assert result_board_state == board_state

def test_sprinter():
    current_player_state = 0b1001100000000000000000000000000
    expected_player_state = 0b0000000010011010000000000000000
    card_index = 3
    result = game.sprinter(current_player_state, card_index)
    assert result == expected_player_state

def test_airborne():
    current_player_state = 0b1010001000000000000000000000000
    other_player_state =   0b0001001000000000000000000000000
    board_state = 0b0001000100100010001010
    expected_board_state = 0b0001000100100010001001

    result_current_player_state, result_other_player_state, result_board_state = game.airborne(current_player_state, other_player_state, board_state, 3, 1)
    assert result_current_player_state == current_player_state
    assert result_other_player_state == result_other_player_state
    assert result_board_state == expected_board_state

def test_bifurcated_strike():
    current_player_state = 0b00000000101100100000000000000000
    other_player_state =   0b00010010000000000001001000000000
    board_state = 0b0001000100100010001010
    result_current_player_state, result_other_player_state, result_board_state = game.bifurcated_strike(current_player_state, other_player_state, board_state, 2, 1)
    assert result_current_player_state == current_player_state
    assert result_other_player_state == 0
    assert result_board_state == board_state

def test_sharp_quills():
    current_player_state = 0b1100001000000000000000000000000
    other_player_state =   0b1100001000000000000000000000000
    board_state = 0b0001000100100010001010
    result_current_player_state, result_other_player_state, result_board_state = game.sharp_quills(current_player_state, other_player_state, board_state, 3, 1)
    assert result_current_player_state == 0
    assert result_other_player_state == 0
    assert result_board_state == board_state

def test_apply_turn():
    current_player_state = 0b00000000001000100000000000000000
    other_player_state =   0b00010010000000000001001000000000
    board_state = 0b0001000100100010001010
    expected_board_state = 0b0001000100100010000111

    result_current_player_state, result_other_player_state, result_board_state = game.apply_turn(current_player_state, other_player_state, board_state)
    assert result_current_player_state == current_player_state
    assert result_other_player_state == other_player_state
    assert result_board_state == expected_board_state


run_tests()