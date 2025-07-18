import math
import time
import random
from game import get_current_player, get_drawn_cards, switch_player, apply_turn, set_drawn_cards, next_states, is_game_over, get_drawn_squirrels, set_drawn_squirrels, state_to_key

# Constants.
MAX_DRAWABLE_RANDOM = 10
MAX_DRAWABLE_SQUIRRELS = 10
HAS_BEEN_DRAWN = -1
CANNOT_DRAW = 0
CAN_DRAW = 1
MAX_ITERATIONS = 40


def set_drawn_and_apply_state(state, current_player_state, current_hand, random_draw, squirrel_draw):
    """
    Apply drawn card adjustments, apply the turn and switch the current player, then return the updated state.

    Parameters:
        state (dict): The current game state.
        current_player_state (int): The temporary players bitboard state representation.
        current_hand (int): The temporary players bitboard hand representation.
        random_draw (int): Flag to determine if random card has been drawn.
        squirrel_draw (int): Flag to determine if squirrel card has been drawn.

    Returns:
        new_state (dict): The updated game state
    """
    if random_draw == HAS_BEEN_DRAWN:
        board_state = set_drawn_cards(state["board_state"])
        current_player_state, other_state, board_state = apply_turn(current_player_state, state["other_player_state"], board_state)
    elif squirrel_draw == HAS_BEEN_DRAWN:
        board_state = set_drawn_squirrels(state["board_state"])
        current_player_state, other_state, board_state = apply_turn(current_player_state, state["other_player_state"], board_state)
    else:
        current_player_state, other_state, board_state = apply_turn(current_player_state, state["other_player_state"], state["board_state"])
    new_state = {
        "board_state": board_state,
        "current_player_state": current_player_state,
        "current_player_hand": current_hand,
        "other_player_state": other_state,
        "other_player_hand": state["other_player_hand"],
        "p0_draws": state["p0_draws"],
        "p1_draws": state["p1_draws"]
    }
    new_state = switch_player(new_state)

    return new_state


def get_draw_id_and_squirrel_drawable(state):
    """
    Returns the draw id and squirrel drawable bool for the current player.
    
    Parameters:
        state (dict): The current game state

    Returns:
        draw_id: (int): 0 if cannot draw a random card, else card id
        squirrel_drawable (int): 0 if cannot draw a squirrel card, else 1
    """
    current_player = get_current_player(state["board_state"])
    drawn = get_drawn_cards(state["board_state"], current_player)
    if drawn == MAX_DRAWABLE_RANDOM:
        draw_id = CANNOT_DRAW
    else:
        draw_id = state["p0_draws"][drawn] if current_player == 0 else state["p1_draws"][drawn]
    if get_drawn_squirrels(state["board_state"], current_player) == MAX_DRAWABLE_SQUIRRELS:
        squirrel_drawable = CANNOT_DRAW
    else:
        squirrel_drawable = CAN_DRAW

    return draw_id, squirrel_drawable


def run_mcts(state, search_time=13, exploration_constant=1.5):
    """
    Run a Monte Carlo Tree Search (MCTS) from the given state and 
    return the visit counts from the roots children and their children.

    Parameters:
        state (int): The starting game state.  
        search_time (int): The Maximum length of time to run for.
        exploration_constant (float): Value to control exploration/exploitation balance.

    Returns:
        children_visits (dict): Dictionary holding total visits for root children nodes
        submove_visits (dict): Dictionary holding total visits for children of root children nodes
    """
    mcts = MCTS(exploration_constant)
    root = mcts.search(state, search_time)
    children_visits = {}
    submove_visits = {}
    for child in root.children:
        child_key = state_to_key(child.state)
        children_visits[child_key] = child.visits
        submove_visits[child_key] = {}
        for submove in child.children:
            submove_key = state_to_key(submove.state)
            submove_visits[child_key][submove_key] = submove.visits

    return children_visits, submove_visits


class MCTSNode:
    """
    A node in the Monte Carlo Tree Search (MCTS) tree representing a specific game state.

    Attributes:
        state (dict): The game state associated with this node.
        parent (MCTSNode or None): The parent node (None for the root).
        children (list): A list of all child MCTSNode instance expanded from this node.
        visits (int): The number of times that this node has been visited during search.
        total_reward (int): The total reward from all simulations passing through this node.
        untried_actions (list): A list of game states not yet explored from this node.
    """

    def __init__(self, state, parent=None):
        """Initialise the MCTSNode object and compute the avaliable states direcly reachable from this node."""
        self.state = state
        self.parent = parent
        self.children = []
        self.visits = 0
        self.total_reward = 0
        self.untried_actions = []

        draw_id, squirrel_drawable = get_draw_id_and_squirrel_drawable(state)
        actions = next_states(state["current_player_state"], state["current_player_hand"], True, draw_id, squirrel_drawable)
        for current_state, current_hand, random_draw, squirrel_draw in actions:
            new_state = set_drawn_and_apply_state(state, current_state, current_hand, random_draw, squirrel_draw)
            self.untried_actions.append(new_state)

    def is_fully_expanded(self):
        """Returns True if no untried actions remain (i.e. the node is fully expanded, otherwise False)."""
        return len(self.untried_actions) == 0

    def add_child(self, child_state):
        """Given a child state, constructs a new MCTSNode object, adds it to its list of children, then returns the child object."""
        child_node = MCTSNode(state=child_state, parent=self)
        self.children.append(child_node)
        return child_node

    def update(self, reward):
        """Increment the visit count and add a reward value to the total reward."""
        self.visits += 1
        self.total_reward += reward

    def uct_value(self, exploration_constant):
        """Return the UCT value for this node using the given exploration constant."""
        if self.visits == 0:
            return float('inf')
        exploitation = self.total_reward / self.visits
        exploration = exploration_constant * math.sqrt(math.log(self.parent.visits) / self.visits)
        return exploitation + exploration


class MCTS:
    """
    Implements Monte Carlo Tree Search (MCTS) to explore and evaluate game states.

    Attributes:
        exploration_constant (float): A parameter to balance exploration and exploitation in UCT calculations.
    """

    def __init__(self, exploration_constant):
        self.exploration_constant = exploration_constant

    def search(self, root_state, time_limit):
        """
        Executes the MCTS search starting from the root state for a given time limit and returns the root node.

        Parameters:
            root_state (dict): the root game state to begin search from.
            time_limit (int): The Maximum length of time to run for.

        Returns:
            root (MCTSNode): the root node of the tree.
        """
        root = MCTSNode(state=root_state)
        start_time = time.time()
        while time.time() - start_time < time_limit:
            node = self.select(root)

            if not is_game_over(node.state["board_state"]) and node.untried_actions:
                node = self.expand(node)

            reward = self.simulate(node.state, get_current_player(root.state["board_state"]))

            self.backpropagate(node, reward)
        return root

    def select(self, node):
        """Traverses the tree by selecting child nodes with the highest UCT value until a node with untried actions is found."""
        while node.is_fully_expanded() and not is_game_over(node.state["board_state"]):
            node = max(node.children, key=lambda child: child.uct_value(self.exploration_constant))
        return node

    def expand(self, node):
        """Expands a node by removing a random untried action and adding the corresponding child node."""
        next_state = node.untried_actions.pop(random.randint(0, len(node.untried_actions) - 1))
        return node.add_child(next_state)
    
    def simulate(self, state, root_player_id):
        """
        Runs a simulation from a given state until a player wins or the maximum number of 
        iterations is reached, returning a reward based on the outcome.
        
        Parameters:
            state (dict): Rhe game state to run a simulation from.
            root_player_id: Rhe root player.

        Returns:
            reward (int): The reward for the simulation relative to the root player
        """
        iterations = 0
        while not is_game_over(state["board_state"]):

            current_player = get_current_player(state["board_state"])
            if get_drawn_cards(state["board_state"], current_player) >= MAX_DRAWABLE_RANDOM and get_drawn_squirrels(state["board_state"], current_player) >= MAX_DRAWABLE_SQUIRRELS:
                if iterations == MAX_ITERATIONS:   # stalemate reached
                    return 0
                else:
                    iterations += 1
            
            draw_id, squirrel_drawable = get_draw_id_and_squirrel_drawable(state)
            possible_actions = next_states(state["current_player_state"], state["current_player_hand"], True, draw_id, squirrel_drawable)
            current_state, current_hand, random_draw, squirrel_draw = random.choice(possible_actions)

            state = set_drawn_and_apply_state(state, current_state, current_hand, random_draw, squirrel_draw)
        reward = self.evaluate(state, root_player_id)
        return reward

    def evaluate(self, state, root_player_id):
        """Evaluates the reward for given state relative to the root player,
           returning -1 if root player has lost, or 1 if it has won."""
        if get_current_player(state["board_state"]) == root_player_id:
            return -1
        return 1

    def backpropagate(self, node, reward):
        """Propagates the reward up the tree by updating visit counts and 
           total reward until the root state is found"""
        while node is not None:
            node.update(reward)
            node = node.parent