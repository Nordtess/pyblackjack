class Card:

    def __init__(self, suit, rank, value, image):
        self.suit = suit
        self.rank = rank
        self.value = value
        self.image = image


    def draw(self, screen, x, y):
        screen.blit(self.image, (x, y))


    def __repr__(self):
        return f"{self.rank} of {self.suit}"
        

