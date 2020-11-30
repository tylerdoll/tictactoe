def default(payoff, levels):
    """ Keep the payoff the same. """
    return 1


def shortest(payoff, levels):
    """ The more moves needed to win, the worse the moves are. """
    return 1 - longest(payoff, levels)


def longest(payoff, levels):
    """ The more moves needed to win, the better the moves are.

    The bounds on the penality are (1/10, 9/10). The limits are just shy of 1 in order to prevent the utility from going to 0 for all outcomes.
    """
    max_levels = 9
    return levels / (max_levels + 1)
