class Player:
    """Represents a player in the blackjack game."""
    
    def __init__(self):
        self.hand = []

    def add_card(self, card):
        self.hand.append(card)

    def get_value(self):
        """Calculate total hand value with ace optimization."""
        return self._calculate_value(len(self.hand))

    def get_value_for_cards(self, num_cards):
        """Calculate value for only the first num_cards in hand."""
        return self._calculate_value(num_cards)
    
    def _calculate_value(self, num_cards):
        value = 0
        aces = 0

        for i in range(min(num_cards, len(self.hand))):
            card = self.hand[i]
            value += card.value
            if card.rank == "ace":
                aces += 1

        while value > 21 and aces > 0:
            value -= 10
            aces -= 1
            
        return value
