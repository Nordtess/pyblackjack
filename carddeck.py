import os
import pygame
import random
from card import Card

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.path.join(BASE_DIR, "images")


class CardDeck:
    """Represents a deck of 52 playing cards."""
    
    def __init__(self):
        self.cards = []
        self._build_deck()

    def _build_deck(self):
        suits = ["hearts", "diamonds", "spades", "clubs"]
        ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "j", "q", "k", "a"]

        for suit in suits:
            for rank in ranks:
                image_path = os.path.join(IMAGE_DIR, f"{suit}_{rank}.png")
                image = pygame.image.load(image_path).convert_alpha()
                image = pygame.transform.scale(image, (120, 180))
                
                if rank in ["j", "q", "k"]:
                    value = 10
                elif rank == "a":
                    value = 11
                else:
                    value = int(rank)
                    
                self.cards.append(Card(suit, rank, value, image))

    def shuffle(self):
        random.shuffle(self.cards)

    def draw_card(self):
        return self.cards.pop() if self.cards else None