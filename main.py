from argparse import ArgumentParser
from copy import deepcopy
import logging
from time import time

PLAYERS = ["x", "o"]
COLORS = [
    "\033[91m", # red
    "\033[94m" # blue
]

BOARD_SPACES = [
    "TL", "TM", "TR",
    "ML", "MM", "MR",
    "BL", "BM", "BR",
]

PAYOFFS = {}

class Node:
    def __init__(self, value="", player=1, state=""):
        self.value = value
        self.children = []
        self.player = player
        self.state = state
        self.payoff = [PAYOFFS["tie"], PAYOFFS["tie"]]

    def add_child(self, node):
        self.children.append(node)

    def __str__(self, level=0):
        if MAX_LEVEL <= 0:
            return ""

        color = COLORS[self.player]
        ret = "" if not self. value else color + "   " * level + "|" + "__" + self.value
        if level < MAX_LEVEL and self.children:
            ret += "\n"
            for child in self.children:
                ret += child.__str__(level+1)
        else:
            ret += " " + str(find_spne(self, 1 - self.player)[0].payoff) + "\n"
        return ret


def winner(state):
    rows = [
        state[:3],
        state[3:6],
        state[6:],
    ]

    cols = [
        [state[0], state[3], state[6]],
        [state[1], state[4], state[7]],
        [state[2], state[5], state[8]],
    ]

    diags = [
        [state[0], state[4], state[8]],
        [state[2], state[4], state[6]],
    ]

    for vals in [rows, cols, diags]:
        for v in vals:
            if len(set(v)) == 1 and v[0] in PLAYERS:
                return v[0]


def build_subgame(root, spaces, player):
    num_games = int(len(spaces) == 0)

    for space in spaces:
        new_state = list(root.state)
        new_state[BOARD_SPACES.index(space)] = PLAYERS[player]
        new_state = "".join(new_state)

        child = Node(space, player, new_state)

        w = winner(new_state)
        if w:
            player_wins = w == PLAYERS[player]

            payoff = [PAYOFFS["tie"]] * 2
            payoff[player] = PAYOFFS["win"] if player_wins else PAYOFFS["lose"]
            payoff[1 - player] = PAYOFFS["lose"] if player_wins else PAYOFFS["win"]
            child.payoff = payoff

            free_spaces = []
        else:
            free_spaces = [s for s in spaces if s != space]

        num_games += build_subgame(child, free_spaces, 1 - player)

        root.add_child(child)

    return num_games


def utility(payoff, levels, goal=None):
    if goal == "shortest":
        min_turns = 3
        return payoff - (1 - (min_turns / levels))

    return payoff

def parse_player(value):
    return PLAYERS.index(value)


def parse_state(value):
    free_spaces = []

    for i, space in enumerate(value):
        if space == ".":
            free_spaces.append(BOARD_SPACES[i])

    return free_spaces


def print_state(state):
    def row(a,b):
        return " " + " | ".join(state[a:b]) + "\n"
    rows = [row(i*3,(i+1)*3) for i in range(3)]

    divider = "-----------\n"
    print(divider.join(rows))


def find_spne(root, player, level=0):
    if len(root.children) == 0:
        return root, level

    choice_level = None
    choice = Node()
    choice.payoff = [-1000, -1000]

    for child in root.children:
        spne_node, spne_level = find_spne(child, 1 - player, level+1)
        if spne_node.payoff[player] > choice.payoff[player]:
            choice = spne_node
            choice_level = spne_level

    n = deepcopy(root)
    n.children = [choice]
    n.payoff = choice.payoff
    return n, choice_level


def find_spne_state(root):
    try:
        return find_spne_state(root.children[0])
    except IndexError:
        return root.state


def main(args):
    global MAX_LEVEL
    global PAYOFFS

    if args.v:
        logging.getLogger().setLevel(logging.DEBUG)

    MAX_LEVEL = args.gt
    logging.debug("Game tree max display level: %d", MAX_LEVEL)

    PAYOFFS["win"] = args.win
    PAYOFFS["lose"] = args.lose
    PAYOFFS["tie"] = args.tie
    logging.debug("Payoffs: %s", PAYOFFS)

    # game state
    starting_state = args.starting_state
    assert len(starting_state) == len(BOARD_SPACES), "Invalid board state"
    assert not winner(starting_state), "Board is already in a winning state"
    print_state(starting_state)
    free_spaces = parse_state(starting_state)
    logging.debug("Free spaces: %s", free_spaces)

    # player
    player = parse_player(args.player)
    logging.debug("Whose turn: player %d %s", player, PLAYERS[player])

    # game tree
    gt = Node(player=player, state=starting_state)
    num_subgames = build_subgame(gt, free_spaces, player)
    logging.debug(f"Number of subgames: {num_subgames}")
    print(gt)

    # spne
    start = time()
    spne, level = find_spne(gt, player)
    end = time()

    ml = MAX_LEVEL
    MAX_LEVEL = 1000
    print("SPNE:")
    print(spne)
    MAX_LEVEL = ml

    print_state(find_spne_state(spne))
    logging.debug("SPNE has %d levels", level)
    logging.debug("Time to find SPNE: %f seconds", end - start)

if __name__ == "__main__":
    ap = ArgumentParser()
    ap.add_argument("starting_state", type=str, default="", help="Starting state of the board from top-left to bottom-right. Example: \"xxo..ox..\"")
    ap.add_argument("player", type=str, choices=PLAYERS, default=PLAYERS[0], help="Player whose turn it is")
    ap.add_argument("--gt", type=int, default=0, help="Levels of game tree to print")
    ap.add_argument("-v", action="store_true", help="Enable verbose output")
    ap.add_argument("-w", "--win", type=int, default=1, help="Payoff for win")
    ap.add_argument("-l", "--lose", type=int, default=-1, help="Payoff for lose")
    ap.add_argument("-t", "--tie", type=int, default=0, help="Payoff for tie")
    ap.add_argument("-g", "--goal", type=str, default=None, choices=["none", "shortest"], help="Goal for utility function")
    args = ap.parse_args()
    main(args)
