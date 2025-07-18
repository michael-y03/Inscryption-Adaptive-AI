import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.insert(0, parent_dir)
import game
import ai


def run_tests():
    test_set_drawn_and_apply_state()
    get_draw_id_and_squirrel_drawable()
    print("All tests passed!")

def test_set_drawn_and_apply_state():
    temp_current_player_state = 0b1010001000000000000000000000000
    original_current_player_state = 0b1010001010100010000000000000000
    temp_other_player_state =   0b0001001000000000000000000000000
    board_state = 0b0001000100100010001010
    current_player_hand = (1 << (1 * game.HAND_CARD_COUNT_SHIFT))
    original_state = {"board_state": board_state, "current_player_state": temp_current_player_state, "current_player_hand": None, "other_player_state": temp_other_player_state, "other_player_hand": None, "p0_draws": None, "p1_draws": None}
    expected_state = {'board_state': 280744, 'current_player_state': 150994944, 'current_player_hand': None, 'other_player_state': 1364262912, 'other_player_hand': 16, 'p0_draws': None, 'p1_draws': None}
    result = ai.set_drawn_and_apply_state(original_state, original_current_player_state, current_player_hand, 0, 1)
    assert result == expected_state

def get_draw_id_and_squirrel_drawable():
    board_state = 0b0000000000000000001010
    state = {"board_state": board_state, "current_player_state": None, "current_player_hand": None, "other_player_state": None, "other_player_hand": None, "p0_draws": [2], "p1_draws": [2]}
    result_draw_id, result_squirrel_drawable = ai.get_draw_id_and_squirrel_drawable(state)
    assert result_draw_id == 2
    assert result_squirrel_drawable == 1

run_tests()