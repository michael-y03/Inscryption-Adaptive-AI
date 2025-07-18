import sys
import time
import concurrent.futures
import threading
import queue
import multiprocessing
from game import (get_card_id, get_current_player, get_drawn_cards, switch_player, is_game_over, initialise_gamestate, get_drawn_squirrels, play_card, apply_turn, draw_squirrel,
                set_card_count, get_card_count, set_drawn_squirrels, set_drawn_cards, count_current_player_cards, remove_card, state_to_key, key_to_state)
from ai import run_mcts
from data import cards


def clear_queue(queue):
    """Clears a given queue by getting all items 
       from queue until queue is empty."""
    while not queue.empty():
        try:
            queue.get_nowait()
        except:
            break


def handle_draw_phase(state):
    """Handles human draw logic, returns the updated state if a draw is possible."""
    drawn = get_drawn_cards(state["board_state"], get_current_player(state["board_state"]))
    drawn_squirrels = get_drawn_squirrels(state["board_state"], get_current_player(state["board_state"]))
    clear_queue(draw_event_queue)
    if drawn < 10 or drawn_squirrels < 10:
        while True:
            try:
                draw_type = draw_event_queue.get(timeout=0.1)
                if draw_type[0] == "draw_card":
                    if draw_type[1] == 1:
                        state["current_player_hand"] = draw_squirrel(state["current_player_hand"])
                        state["board_state"] = set_drawn_squirrels(state["board_state"])
                        break
                    else:
                        state["current_player_hand"] = set_card_count(state["current_player_hand"], draw_type[1], get_card_count(state["current_player_hand"], draw_type[1])+1)
                        state["board_state"] = set_drawn_cards(state["board_state"])
                        break
            except queue.Empty:
                continue
    return state


def handle_play_phase(state):
    """Handles human play logic, including placing cards, sacrificing cards and ending turn."""
    clear_queue(draw_event_queue)
    while True:
        if not gui.running:
            sys.exit()
        gui.state = state
        try:
            events = draw_event_queue.get(timeout=0.1)
            if events[0] == "end_turn":
                return state
            elif events[0] == "hand_card":
                blood_cost = cards[events[1]][2]
                if blood_cost == 0:
                    while True:
                        if not gui.running:
                            sys.exit()
                        try:
                            position = draw_event_queue.get(timeout=0.1)
                            if position[0] == "board_position" and not get_card_id(state["current_player_state"], position[1]):
                                state["current_player_state"], state["current_player_hand"] = play_card(state["current_player_state"], state["current_player_hand"], events[1], position[1])
                                break
                        except queue.Empty:
                            continue
                else:
                    if count_current_player_cards(state["current_player_state"]) >= blood_cost:
                        sacrificed = 0
                        while True:
                            gui.state = state
                            if not gui.running:
                                sys.exit()
                            if sacrificed == blood_cost:
                                try:
                                    position = draw_event_queue.get(timeout=0.1)
                                    if position[0] == "board_position" and not get_card_id(state["current_player_state"], position[1]):
                                        state["current_player_state"], state["current_player_hand"] = play_card(state["current_player_state"], state["current_player_hand"], events[1], position[1])
                                        break
                                except queue.Empty:
                                    continue
                            try:
                                sacrifice = draw_event_queue.get(timeout=0.1)
                                if sacrifice[0] == "board_position" and get_card_id(state["current_player_state"], sacrifice[1]) and sacrificed != blood_cost:
                                    state["current_player_state"] = remove_card(state["current_player_state"], sacrifice[1])
                                    sacrificed += 1
                            except queue.Empty:
                                continue
        except queue.Empty:
            continue


def handle_ai_turn(state, player_efficiency_rates):
    """
    This handles the ai turn logic, and updates the state with the chosen move.

    This function creates 4 processes to run a root parallelised Monte Carlo Tree Search 
    simulation from a given state. After these return, it normalises the visits for all child 
    states of the root and calculates their overall efficiency. It then averages the values in player 
    efficiency rates and attempts to choose a move from the roots children with the same or a
    slightly higher efficiency rating (if one exists).

    It returns this state and a dictionary containing the roots children and their subsequent children.
    """
    aggregated_visits = {}
    aggregated_submoves = {}
    with concurrent.futures.ProcessPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(run_mcts, state) for _ in range(4)]
        for future in concurrent.futures.as_completed(futures):
            child_visits, subchild_visits = future.result()
            for key, visits in child_visits.items():
                aggregated_visits[key] = aggregated_visits.get(key, 0) + visits
            for child_key, subchild_dict in subchild_visits.items():
                if child_key not in aggregated_submoves:
                    aggregated_submoves[child_key] = {}
                for subchild_key, subchild_visits in subchild_dict.items():
                    aggregated_submoves[child_key][subchild_key] = aggregated_submoves[child_key].get(subchild_key, 0) + subchild_visits
    percentages = normalise_visits(aggregated_visits)
    target_avg = sum(player_efficiency_rates) / len(player_efficiency_rates)
    print(f"Number of rollouts: {sum(aggregated_visits.values())}")
    print(f"Target Average: {target_avg}")
    best_move_key, best_move_visits = max(aggregated_visits.items(), key=lambda item: item[1])
    best_percentage = (best_move_visits / max(aggregated_visits.values())) * 100
    if best_percentage <= target_avg:
        chosen_key = best_move_key
    else:
        candidates = {key: perc for key, perc in percentages.items() if perc >= target_avg}
        chosen_key = min(candidates, key=lambda k: candidates[k] - target_avg)
    return chosen_key, aggregated_submoves


def get_submove_efficiencies(chosen_key, aggregated_submoves):
    """This calculates and returns the efficiencies of submoves for a chosen move."""
    submoves_for_chosen = aggregated_submoves.get(chosen_key, {})
    if not submoves_for_chosen:
        return {}
    normalized = normalise_subvisits(submoves_for_chosen)
    return {k: (submoves_for_chosen[k], normalized[k]) for k in submoves_for_chosen}
    

def normalise_visits(visits):
    """Normalises visits linearly to a 0-100 scale (unless all values are 
       the same, which returns 100 for all)"""
    min_visits = min(visits.values())
    max_visits = max(visits.values())
    if max_visits > min_visits:
        norm = {k: ((v - min_visits) / (max_visits - min_visits)) * 100 for k, v in visits.items()}
    else:
        norm = {k: 100 for k in visits}
    return norm


def normalise_subvisits(visits):
    """Normalises submove visits relative to the minimum. flips the percentages (100>0, 0>100) 
       so that they are relative to the human player, instead of the AI"""
    if not visits:
        return {}
    min_val = min(visits.values())
    norm = {k: (min_val / v) * 100 for k, v in visits.items()}
    return norm


def visualise_best_move(aggregated_submoves):
    """Calculates the best and worst moves the human could have made and shows them on-screen for 3 seconds each."""
    human_efficiencies = { key: norm_eff for key, (raw, norm_eff) in aggregated_submoves.items() }
    best_human_key = max(human_efficiencies.items(), key=lambda x: x[1])[0]
    worst_human_key = min(human_efficiencies.items(), key=lambda x: x[1])[0]
    best_human_state = key_to_state(best_human_key)
    gui.state = best_human_state
    time.sleep(3)
    worst_human_state = key_to_state(worst_human_key)
    gui.state = worst_human_state
    time.sleep(3)


def update_player_efficiency_rates(aggregated_submoves, human_move_key, player_efficiency_rates):
    """Updates the player_efficiency_rates with the humans latest move efficiency percentage. if len(player_efficiency_rates) 
       becomes more than or equal to max_player_efficiency_rates, it removes the earliest element. essentially keeping the 
       player_efficiency_rates as a rolling average."""
    if human_move_key in aggregated_submoves:
        visits, human_eff = aggregated_submoves[human_move_key]
        print(f"Move efficiency: {human_eff}")
        if len(player_efficiency_rates) >= 5:
            player_efficiency_rates.pop(0)
        player_efficiency_rates.append(human_eff)
    return player_efficiency_rates


def run_game(state, player_efficiency_rates, adaptive_mode, visualise_moves):
    """This function controls the overall game loop, current_players, applying turns etc."""
    while not is_game_over(state["board_state"]):
        if not gui.running:
            sys.exit()
        gui.state = state
        if get_current_player(state["board_state"]) == 0:
            chosen_key, aggregated_submoves  = handle_ai_turn(state, player_efficiency_rates)
            state = key_to_state(chosen_key)
            aggregated_submoves = get_submove_efficiencies(chosen_key, aggregated_submoves)
        else:
            state = handle_draw_phase(state)
            state = handle_play_phase(state)
            state["current_player_state"], state["other_player_state"], state["board_state"] = apply_turn(state["current_player_state"], state["other_player_state"], state["board_state"])
            state = switch_player(state)
            if adaptive_mode:
                player_efficiency_rates = update_player_efficiency_rates(aggregated_submoves, state_to_key(state), player_efficiency_rates)
            if visualise_moves:
                visualise_best_move(aggregated_submoves)
                gui.state = state
    return state


def main_controller(state,player_efficiency_rates, adaptive_mode, visualise_moves):
    """This function displays the settings screen, runs the game, and updates the human 
       players game over state in the gui so that a game over screen can be drawn."""
    clear_queue(draw_event_queue)
    while True:
        if not gui.running:
            sys.exit()
        try:
            start = draw_event_queue.get(timeout=0.1)
            if start[0] == "end_turn":
                break
            if start[0] == "adaptive_mode":
                adaptive_mode = not adaptive_mode
                if not adaptive_mode:
                    player_efficiency_rates = [100]
                else:
                    player_efficiency_rates = [70]

            if start[0] == "visualise_moves":
                visualise_moves = not visualise_moves
        except queue.Empty:
            continue
    state = run_game(state, player_efficiency_rates, adaptive_mode, visualise_moves)
    gui.state = state
    if get_current_player(state['board_state']) == 0:
        time.sleep(2)
        gui.winner = True
    else:
        time.sleep(2)
        gui.defeated = True
    gui.running = False



if __name__ == "__main__":
    """This freezes support for multiprocessing so that processes/threads do not reinitalise the GUI. 
       It sets the standard settings for the game, initialises a queue (draw_event_queue) for communication 
       between the GUI and main game loop.
       
       It then initalises the GUI and gamestate, and creates a thread to run the game_loop.
    """
    multiprocessing.freeze_support()
    from gui import GameGUI
    adaptive_mode = True
    visualise_moves = False
    player_efficiency_rates = [70]
    draw_event_queue = queue.Queue()
    gui = GameGUI(event_queue=draw_event_queue)
    while True:
        state = initialise_gamestate()
        controller_thread = threading.Thread(
            target=main_controller,
            args=(state, player_efficiency_rates, adaptive_mode, visualise_moves)
        )
        controller_thread.start()
        gui.state = state
        gui.run()
        controller_thread.join()
        gui.reset_gui()

