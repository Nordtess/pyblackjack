class Player:
    def __init__(self):
        self.hand = []



    def add_card(self, card):
        self.hand.append(card)


    def get_value(self):
        value = 0
        aces = 0

        for card in self.hand:
            value += card.value
            if card.rank == "ace":
                aces += 1

        while value > 21 and aces > 0:
            value -= 10
            aces -= 1
        return value
