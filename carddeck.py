import os
import pygame
import random
from card import Card


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

IMAGE_DIR = os.path.join(BASE_DIR, "images")

class CardDeck:

    def __init__(self):


        self.cards = []

        suits = ["hearts", "diamonds", "spades", "clubs"]
        ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "j", "q", "k", "a"]

        for s in suits:
            for r in ranks:
                filename = f"{s}_{r}.png"
                path = os.path.join(IMAGE_DIR, filename)

                image = pygame.image.load(path).convert_alpha()

                image = pygame.transform.scale(image, (120, 180))

                if r in ["j", "q", "k"]:
                    val = 10
                elif r == "a":
                    val = 11
                else:
                    val = int(r)

                new_card = Card(s, r, val, image)
                self.cards.append(new_card)

    def shuffle(self):
        random.shuffle(self.cards)


    def draw_card(self):
        if len(self.cards) > 0:
            return self.cards.pop()
        return None

        


        