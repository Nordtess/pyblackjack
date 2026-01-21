import pygame
from carddeck import CardDeck
from player import Player


pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()


deck = CardDeck()
deck.shuffle()

player = Player()
dealer = Player()


player.add_card(deck.draw_card())
player.add_card(deck.draw_card())

font = pygame.font.SysFont("Arial", 48, bold=True)

running = True




while running: 
    for event in pygame.event.get(): 
        if event.type == pygame.QUIT:
            running = False

        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_h:
                new_card = deck.draw_card()
                if new_card:
                    player.add_card(new_card)

    current_score = player.get_value()

    screen.fill("green")
    
    score = player.get_value()

    text_color = (255, 255, 255)

    if score > 21:
        text_color = (255, 0, 0)

    score_text = font.render(f"Points: {score}", True, text_color)


    screen.blit(score_text, (100, 350))

    x_pos = 100
    for card in player.hand:
        screen.blit(card.image, (x_pos, 500))
        x_pos += 130

    pygame.display.flip()
    clock.tick(60)


pygame.quit()