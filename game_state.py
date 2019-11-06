STACK_COUNT = 6
INITIAL_STACK_SIZE = 6
MAX_STACK_SIZE = 15

STACK_RANGE = range(STACK_COUNT)


class GameState:
    def __init__(self):
        self.actions_taken = 0

        # List of lists of tuples
        # Finished stacks become None - won state contains 4 Nones and 2 empty lists
        self.stacks = []

        # List of booleans
        # True if the stack at index i has a cheated card on top
        self.cheats = []

        # Initialize all stacks as empty
        for i in STACK_RANGE:
            self.stacks.append([])
            self.cheats.append(False)

    def clone(self):
        """
            Clones the given GameState object
        """
        clone = GameState()

        for i in STACK_RANGE:
            if self.stacks[i] is None:
                clone.stacks[i] = None
                continue
            for j in range(len(self.stacks[i])):
                # Copy each card from each stack
                card = self.stacks[i][j]
                clone.stacks[i].append(card)

        clone.actions_taken = self.actions_taken

        return clone

    def is_won(self):
        """
            Determine if the current state is the won end state
        """
        # If any stack has open cards, return False
        for i in STACK_RANGE:
            if self.stacks[i] is not None and len(self.stacks[i]) > 0:
                return False

        return True

    def query_stack_top(self, index):
        """
            Return the card that is on top of the given stack at index. Returns None if stack is empty or finished
            Does not remove the card from the stack
        """
        stack = self.stacks[index]
        if stack is None or len(stack) == 0:
            return None
        return stack[-1]

    def get_total_card_count(self):
        """
            Returns the total card count in the stacks
        """
        return sum([len(x) for x in self.stacks])

    def pull_from_stack(self, index, count):
        """
            Return given number of cards from the given stack
            Removes the said cards from the stack
        """
        stack = self.stacks[index]
        start = stack[:-count]
        end = stack[-count:]

        # Set the "new" stack and return the extra
        self.stacks[index] = start
        return end

    def parse_card_into_stack(self, index, card):
        """
            Puts the given card at the top of the stack, used in the image parsing
        """
        self.stacks[index].append(card)

    def get_legal_actions(self):
        """
            Returns all legal actions as a 2-tuple:
                (from, to)

            "from" is a 2-tuple
                (stack_index, card_index)
            with card_index meaning the index of the card in the given stack

            "to" is a 2-tuple
                (cheat, index)
            with cheat meaning whether the move is a "cheating" move, index being the target stack index
        """
        actions = []

        # Loop through all stacks, and list out all legal actions
        for stack_index in STACK_RANGE:
            stack = self.stacks[stack_index]
            for card_index in range(len(stack))[::-1]:
                card = stack[card_index]

                # Early exit conditions for cards that are not the topmost
                if card_index < len(stack) - 1:
                    # If the value of the card is not +1 of the value on top of it, break from this stack loop
                    # (no cards below can be moved either)
                    if stack[card_index + 1] + 1 != stack[card_index]:
                        break

                    # Any card below a cheated card cannot be moved, break
                    if self.cheats[stack_index] == True:
                        break

                # Check if the card can be placed onto any other stack
                for target_stack_index in STACK_RANGE:
                    # Can not move onto the same stack (legal nor cheating)
                    if stack_index == target_stack_index:
                        continue

                    # Can not move onto a finished stack (legal nor cheating)
                    if self.stacks[target_stack_index] is None:
                        continue

                    # Can not move onto a cheated stack
                    if self.cheats[target_stack_index]:
                        continue

                    if self.can_place(card, target_stack_index):
                        actions.append((
                            (stack_index, card_index), (False, target_stack_index)
                        ))
                    else:
                        # Check for cheat moves (only for other stacks that have cards and where we cannot normally move)
                        # Can only cheat the topmost card
                        # Can not re-cheat a cheated card
                        if card_index == len(stack) - 1 and not self.cheats[stack_index]:
                            actions.append((
                                (stack_index, card_index), (True, target_stack_index)
                            ))

        return actions

    def can_place(self, card, stack_index):
        """
            Returns true if the given card can be placed onto the given stack (legally)
        """

        # Can always place on empty stack
        if len(self.stacks[stack_index]) == 0:
            return True

        target_card = self.stacks[stack_index][-1]
        return target_card == card + 1

    def apply_action(self, action):
        """
            Applies the given action to this state. Assumes that the action is valid.
        """
        self.actions_taken += 1

        action_from = action[0]
        action_to = action[1]

        # Moving a card or stack onto another stack
        from_stack_index = action_from[0]
        from_card_index = action_from[1]

        to_cheat_state = action_to[0]
        to_stack_index = action_to[1]

        cards_to_pull = len(
            self.stacks[from_stack_index]) - from_card_index
        cards = self.pull_from_stack(from_stack_index, cards_to_pull)
        self.stacks[to_stack_index] += cards
        # Set the cheat state of the topmost card. Has a real effect only if moving a cheat card
        self.cheats[to_stack_index] = to_cheat_state
        # If moving a cheated card to a valid position, un-cheat that stack
        if self.cheats[from_stack_index]:
            self.cheats[from_stack_index] = False

    def get_heuristic_value(self):
        """
            Returns a heuristic value for choosing a state over another
        """
        score = 0

        # TODO: heuristic based on number of completed stacks

        return score

    def __eq__(self, other):
        for i in STACK_RANGE:
            if self.stacks[i] != other.stacks[i]:
                return False

        return True

    def __hash__(self):
        stacks_hash = "-".join(["".join([str(y) for y in x])
                                for x in self.stacks if len(x) > 0])
        cheats_hash = "".join("C" if x else "L" for x in self.cheats)
        return hash(stacks_hash + "-" + cheats_hash)

    def __str__(self):
        return ("Board:\n" +
                "\n".join([", ".join(
                    map(lambda slot: str(slot[0]) + " " + str(slot[1]), self.stacks[stack_index])) + (" C" if self.cheats[stack_index] else "")
                    for stack_index in STACK_RANGE]
                ))
