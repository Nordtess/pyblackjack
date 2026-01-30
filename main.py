import os
import pygame
from carddeck import CardDeck
from player import Player

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BALANCE_FILE = os.path.join(BASE_DIR, "balance.txt")
BACKSIDE_PATH = os.path.join(BASE_DIR, "images", "backside.png")
WALLPAPER_PATH = os.path.join(BASE_DIR, "images", "wallpaper1.jpg")

CARD_DELAY_MS = 600
INFO_PANEL_X, INFO_PANEL_Y = 900, 100
INFO_PANEL_WIDTH, INFO_PANEL_HEIGHT = 340, 500

COLOR_DARK_GREEN = (10, 60, 15)
COLOR_LIGHT_GREEN = (7, 96, 20)
COLOR_GOLD = (255, 215, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_RED = (255, 0, 0)
COLOR_GREEN = (100, 255, 100)
COLOR_GRAY = (70, 70, 70)
COLOR_BLUE = (0, 120, 220)
COLOR_BLUE_HOVER = (30, 140, 240)
COLOR_CHIP_RED = (210, 70, 70)
COLOR_CHIP_RED_HOVER = (230, 100, 100)

deck = CardDeck()
deck.shuffle()
player = Player()
dealer = Player()

game_over = False
status_message = ""
show_menu = True
betting = False
balance = 0
current_bet = 50
dealer_hide_second = False
cards_to_show = 0
last_card_time = 0
player_cards_to_show_hit = 2
running = True

font = pygame.font.SysFont("Arial", 48, bold=True)
button_font = pygame.font.SysFont("Arial", 32, bold=True)
title_font = pygame.font.SysFont("Arial", 72, bold=True)
info_font = pygame.font.SysFont("Arial", 24)

hit_button = pygame.Rect(100, 610, 160, 60)
stay_button = pygame.Rect(300, 610, 160, 60)
quit_button = pygame.Rect(20, 20, 80, 32)
play_again_button = pygame.Rect(130, 20, 160, 32)
play_button = pygame.Rect(520, 300, 240, 80)
menu_start_time = pygame.time.get_ticks()

chip_buttons = [(pygame.Rect(920 + (i % 2) * 140, 420 + (i // 2) * 90, 100, 80), val) 
                for i, val in enumerate([10, 25, 50, 100])]


def load_image(path, size=None):
    """Load and optionally scale an image."""
    try:
        img = pygame.image.load(path)
        if size:
            img = pygame.transform.scale(img, size)
        return img.convert_alpha() if path.endswith('.png') else img.convert()
    except Exception:
        return None


backside_image = load_image(BACKSIDE_PATH, (120, 180))
wallpaper_image = load_image(WALLPAPER_PATH, (1280, 720))

def load_balance():
    """Load player balance from file or return default."""
    if not os.path.exists(BALANCE_FILE):
        return 500
    try:
        with open(BALANCE_FILE, "r", encoding="utf-8") as f:
            return max(0, int(f.read().strip() or 0))
    except Exception:
        return 500


def save_balance(value):
    """Save player balance to file."""
    try:
        with open(BALANCE_FILE, "w", encoding="utf-8") as f:
            f.write(str(int(value)))
    except Exception:
        pass


def reset_round():
    """Reset game state for new round."""
    global deck, player, dealer, game_over, status_message, betting, current_bet, balance
    global dealer_hide_second, cards_to_show, last_card_time, player_cards_to_show_hit
    
    deck = CardDeck()
    deck.shuffle()
    player = Player()
    dealer = Player()
    game_over = False
    status_message = ""
    betting = True
    dealer_hide_second = False
    cards_to_show = 0
    last_card_time = 0
    player_cards_to_show_hit = 2

    if balance <= 0:
        status_message = "Out of funds"
        game_over = True
        betting = False
    else:
        current_bet = max(10, min(current_bet, balance))


def settle_round(result):
    """Handle payouts and end round."""
    global game_over, status_message, balance, betting, dealer_hide_second
    
    if game_over:
        return
        
    game_over = True
    betting = False
    dealer_hide_second = False

    payouts = {
        "blackjack": (int(current_bet * 2.5), "Blackjack! Paid 3:2"),
        "player_win": (current_bet * 2, "You win"),
        "push": (current_bet, "Push"),
        "dealer_win": (0, "Dealer wins"),
        "bust": (0, "You are bust")
    }
    
    payout, msg = payouts.get(result, (0, "Round over"))
    balance += payout
    status_message = msg
    save_balance(balance)


def start_round():
    """Deal initial cards after bet is placed."""
    global betting, balance, status_message, game_over, dealer_hide_second, cards_to_show, last_card_time
    
    if not betting:
        return
    if current_bet <= 0 or current_bet > balance:
        status_message = "Invalid bet"
        return
        
    balance -= current_bet
    save_balance(balance)

    player.add_card(deck.draw_card())
    dealer.add_card(deck.draw_card())
    player.add_card(deck.draw_card())
    dealer.add_card(deck.draw_card())
    
    dealer_hide_second = True
    betting = False
    game_over = False
    status_message = ""
    cards_to_show = 0
    last_card_time = pygame.time.get_ticks()


def handle_hit():
    """Player hits for another card."""
    global game_over, status_message, player_cards_to_show_hit
    
    if game_over or betting:
        return
        
    new_card = deck.draw_card()
    if new_card:
        player.add_card(new_card)
        player_cards_to_show_hit += 1
        
    score = player.get_value()
    if score > 21:
        settle_round("bust")
    elif score == 21:
        play_dealer()


def handle_stay():
    """Player stays with current hand."""
    if game_over or betting:
        return
    play_dealer()


def play_dealer():
    """Dealer plays according to house rules."""
    global dealer_hide_second
    
    dealer_hide_second = False
    
    while dealer.get_value() < 17:
        new_card = deck.draw_card()
        if new_card:
            dealer.add_card(new_card)
        else:
            break
    
    finalize_dealer_round()


def finalize_dealer_round():
    """Determine winner and settle round."""
    player_val = player.get_value()
    dealer_val = dealer.get_value()

    if player_val > 21:
        settle_round("bust")
    elif dealer_val > 21:
        settle_round("player_win")
    elif player_val > dealer_val:
        settle_round("player_win")
    elif player_val < dealer_val:
        settle_round("dealer_win")
    else:
        settle_round("push")


def draw_button(rect, label, enabled=True, hovered=False):
    """Draw a styled button."""
    color = COLOR_GRAY if not enabled else (COLOR_BLUE_HOVER if hovered else COLOR_BLUE)
    pygame.draw.rect(screen, color, rect, border_radius=8)
    pygame.draw.rect(screen, (20, 20, 20), rect, width=2, border_radius=8)
    text_surface = button_font.render(label, True, COLOR_WHITE)
    screen.blit(text_surface, text_surface.get_rect(center=rect.center))


def draw_chip_button(rect, value, hovered=False, enabled=True):
    """Draw a betting chip button."""
    color = COLOR_CHIP_RED if enabled else COLOR_GRAY
    if hovered and enabled:
        color = COLOR_CHIP_RED_HOVER
        
    pygame.draw.ellipse(screen, color, rect)
    pygame.draw.ellipse(screen, (40, 20, 20), rect, width=3)
    text_surface = button_font.render(f"${value}", True, COLOR_WHITE)
    screen.blit(text_surface, text_surface.get_rect(center=rect.center))


def draw_text_with_shadow(text, font_obj, color, pos):
    """Draw text with drop shadow for better visibility."""
    shadow_surface = font_obj.render(text, True, (0, 0, 0))
    surface = font_obj.render(text, True, color)
    screen.blit(shadow_surface, (pos[0] + 2, pos[1] + 2))
    screen.blit(surface, pos)


def draw_text_with_background(text, font_obj, color, pos):
    """Draw text with semi-transparent background."""
    text_surface = font_obj.render(text, True, color)
    bg_rect = pygame.Rect(pos[0] - 5, pos[1] - 5, text_surface.get_width() + 10, 30)
    pygame.draw.rect(screen, (0, 0, 0, 180), bg_rect, border_radius=5)
    draw_text_with_shadow(text, font_obj, color, pos)


def draw_hand(cards, y_pos, hide_second=False, max_cards=None):
    """Draw a hand of cards."""
    x_pos = 100
    cards_shown = len(cards) if max_cards is None else min(max_cards, len(cards))
    
    for idx in range(cards_shown):
        card = cards[idx]
        if hide_second and idx == 1 and backside_image:
            screen.blit(backside_image, (x_pos, y_pos))
        else:
            screen.blit(card.image, (x_pos, y_pos))
        x_pos += 130


def update_card_animation():
    """Handle card animation timing and blackjack checks."""
    global cards_to_show, last_card_time, dealer_hide_second
    
    if betting or cards_to_show >= 4 or game_over:
        return
        
    current_time = pygame.time.get_ticks()
    if current_time - last_card_time >= CARD_DELAY_MS:
        cards_to_show += 1
        last_card_time = current_time
        
        if cards_to_show == 4 and len(player.hand) == 2 and len(dealer.hand) == 2:
            player_blackjack = player.get_value() == 21
            dealer_blackjack = dealer.get_value() == 21
            
            if player_blackjack or dealer_blackjack:
                dealer_hide_second = False
                if player_blackjack and dealer_blackjack:
                    settle_round("push")
                elif player_blackjack:
                    settle_round("blackjack")
                else:
                    settle_round("dealer_win")


def get_visible_cards():
    """Calculate how many cards should be visible based on animation state."""
    if betting:
        return len(dealer.hand), len(player.hand)
        
    dealer_visible = min(2, (cards_to_show + 1) // 2)
    player_visible = min(2, cards_to_show // 2)
    
    if cards_to_show >= 4:
        dealer_visible = len(dealer.hand)
        player_visible = player_cards_to_show_hit
        
    return dealer_visible, player_visible


balance = load_balance()
reset_round()


while running: 
    for event in pygame.event.get(): 
        if event.type == pygame.QUIT:
            running = False

        if show_menu:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    running = False
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    reset_round()
                    show_menu = False
                    menu_start_time = pygame.time.get_ticks()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if play_button.collidepoint(event.pos):
                    reset_round()
                    show_menu = False
                    menu_start_time = pygame.time.get_ticks()
            continue

        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                reset_round()
            if event.key == pygame.K_h and not game_over:
                handle_hit()
            if event.key == pygame.K_s and not game_over:
                handle_stay()
            if event.key == pygame.K_q:
                running = False
            if betting and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                start_round()
            if betting:
                if event.key == pygame.K_UP:
                    current_bet = min(balance, current_bet + 10)
                if event.key == pygame.K_DOWN:
                    current_bet = max(10, current_bet - 10)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not game_over and not betting:
            if hit_button.collidepoint(event.pos):
                handle_hit()
            if stay_button.collidepoint(event.pos):
                handle_stay()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if quit_button.collidepoint(event.pos):
                running = False
            if game_over and play_again_button.collidepoint(event.pos):
                reset_round()
            if betting and hit_button.collidepoint(event.pos):
                start_round()
            if betting:
                for rect, val in chip_buttons:
                    if rect.collidepoint(event.pos):
                        current_bet = min(balance, val)

    if show_menu:
        if wallpaper_image:
            screen.blit(wallpaper_image, (0, 0))
        else:
            screen.fill((7, 96, 20))
        mouse_pos = pygame.mouse.get_pos()
        hover_play = play_button.collidepoint(mouse_pos)

        elapsed = pygame.time.get_ticks() - menu_start_time
        alpha = max(0, min(255, int((elapsed / 800) * 255)))

        title_text = title_font.render("Blackjack", True, (255, 255, 255))
        title_text.set_alpha(alpha)
        title_rect = title_text.get_rect(center=(640, 200))
        # Draw semi-transparent background behind title
        bg_rect = pygame.Rect(title_rect.x - 10, title_rect.y - 5, title_rect.width + 20, title_rect.height + 10)
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
        bg_surface.set_alpha(min(180, alpha))
        bg_surface.fill((0, 0, 0))
        screen.blit(bg_surface, bg_rect)
        screen.blit(title_text, title_rect)

        instruction_text = info_font.render("Enter/Space: Play  |  Q: Quit", True, (255, 255, 255))
        instruction_text.set_alpha(alpha)
        instruction_rect = instruction_text.get_rect(center=(640, 400))
        # Draw semi-transparent background behind instructions
        bg_rect2 = pygame.Rect(instruction_rect.x - 10, instruction_rect.y - 5, instruction_rect.width + 20, instruction_rect.height + 10)
        bg_surface2 = pygame.Surface((bg_rect2.width, bg_rect2.height))
        bg_surface2.set_alpha(min(180, alpha))
        bg_surface2.fill((0, 0, 0))
        screen.blit(bg_surface2, bg_rect2)
        screen.blit(instruction_text, instruction_rect)

        draw_button(play_button, "Play Blackjack", enabled=True, hovered=hover_play)
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND if hover_play else pygame.SYSTEM_CURSOR_ARROW)
        pygame.display.flip()
        clock.tick(60)
        continue

    if wallpaper_image:
        screen.blit(wallpaper_image, (0, 0))
    else:
        screen.fill((7, 96, 20))

    mouse_pos = pygame.mouse.get_pos()
    score = player.get_value()

    text_color = (255, 255, 255)

    if score > 21 and not game_over:
        text_color = (255, 0, 0)
        settle_round("bust")
    if "bust" in status_message.lower():
        text_color = (255, 0, 0)

    current_time = pygame.time.get_ticks()
    if not betting and cards_to_show < 4 and not game_over and current_time - last_card_time >= CARD_DELAY_MS:
        cards_to_show += 1
        last_card_time = current_time
        
        # Check for blackjack after all initial cards are dealt
        if cards_to_show == 4 and len(player.hand) == 2 and len(dealer.hand) == 2:
            player_blackjack = player.get_value() == 21
            dealer_blackjack = dealer.get_value() == 21
            
            if player_blackjack or dealer_blackjack:
                dealer_hide_second = False
                if player_blackjack and dealer_blackjack:
                    settle_round("push")
                elif player_blackjack:
                    settle_round("blackjack")
                else:
                    settle_round("dealer_win")
    
    # Show cards based on animation progress
    dealer_cards_visible = min(2, (cards_to_show + 1) // 2) if not betting else 0
    player_cards_visible = min(2, cards_to_show // 2) if not betting else 0
    
    # After initial animation, show all cards instantly
    if not betting and cards_to_show >= 4:
        dealer_cards_visible = len(dealer.hand)
        player_cards_visible = player_cards_to_show_hit
    
    if betting:
        dealer_cards_visible = len(dealer.hand)
        player_cards_visible = len(player.hand)
    
    # Draw dealer section only if there are cards
    if len(dealer.hand) > 0:
        # Show dealer label only after initial animation completes or during betting
        if betting or cards_to_show >= 4 or game_over:
            if dealer_hide_second and not game_over:
                dealer_label = "Dealer: ?"
            else:
                dealer_score = dealer.get_value_for_cards(dealer_cards_visible)
                dealer_label = f"Dealer: {dealer_score}"
            # Draw semi-transparent background for better readability
            text_surface = info_font.render(dealer_label, True, (255, 255, 255))
            text_width = text_surface.get_width()
            bg_rect = pygame.Rect(95, 45, text_width + 10, 30)
            pygame.draw.rect(screen, (0, 0, 0, 180), bg_rect, border_radius=5)
            draw_text_with_shadow(dealer_label, info_font, (255, 255, 255), (100, 50))
        draw_hand(dealer.hand, 80, hide_second=dealer_hide_second and not game_over, max_cards=dealer_cards_visible)

    # Draw player section only if there are cards
    if len(player.hand) > 0:
        # Show player label only after initial animation completes or during betting
        if betting or cards_to_show >= 4 or game_over:
            player_score = player.get_value_for_cards(player_cards_visible)
            player_text_color = (255, 0, 0) if player_score > 21 else (255, 255, 255)
            player_label = f"Player Points: {player_score}"
            # Draw semi-transparent background for better readability
            text_surface = info_font.render(player_label, True, player_text_color)
            text_width = text_surface.get_width()
            bg_rect = pygame.Rect(95, 315, text_width + 10, 30)
            pygame.draw.rect(screen, (0, 0, 0, 180), bg_rect, border_radius=5)
            draw_text_with_shadow(player_label, info_font, player_text_color, (100, 320))
        draw_hand(player.hand, 350, max_cards=player_cards_visible)
    
    # Right-side information panel
    info_panel_x = 900
    info_panel_y = 100
    panel_width = 340
    panel_height = 500
    
    # Draw info panel background
    panel_rect = pygame.Rect(info_panel_x, info_panel_y, panel_width, panel_height)
    pygame.draw.rect(screen, (10, 60, 15), panel_rect, border_radius=15)
    pygame.draw.rect(screen, (200, 200, 200), panel_rect, width=3, border_radius=15)
    
    # Info panel title
    draw_text_with_shadow("Game Info", button_font, (255, 215, 0), (info_panel_x + 20, info_panel_y + 20))
    
    # Balance and bet info
    draw_text_with_shadow(f"Balance: ${balance}", info_font, (255, 255, 255), (info_panel_x + 20, info_panel_y + 70))
    draw_text_with_shadow(f"Current Bet: ${current_bet}", info_font, (255, 255, 255), (info_panel_x + 20, info_panel_y + 105))
    
    # Show betting options when betting
    if betting:
        draw_text_with_shadow("Select Bet Amount:", info_font, (255, 215, 0), (info_panel_x + 20, info_panel_y + 200))
        for rect, val in chip_buttons:
            draw_chip_button(rect, val, hovered=rect.collidepoint(mouse_pos), enabled=val <= balance)

    # Status message in info panel
    if status_message:
        status_color = (255, 0, 0) if "bust" in status_message.lower() else (100, 255, 100)
        draw_text_with_shadow(status_message, button_font, status_color, (info_panel_x + 20, info_panel_y + 160))

    mouse_pos = pygame.mouse.get_pos()
    buttons_enabled = not game_over and not betting  # Dim Hit/Stay after Stay or bust
    place_enabled = betting and current_bet <= balance and balance > 0
    hover_hit = hit_button.collidepoint(mouse_pos) and (buttons_enabled or place_enabled)
    hover_stay = stay_button.collidepoint(mouse_pos) and buttons_enabled
    hover_quit = quit_button.collidepoint(mouse_pos)
    hover_play_again = game_over and play_again_button.collidepoint(mouse_pos)
    hover_chip = False
    if betting:
        for rect, val in chip_buttons:
            chip_hover = rect.collidepoint(mouse_pos)
            hover_chip = hover_chip or chip_hover

    if betting:
        draw_button(hit_button, "Deal", enabled=place_enabled, hovered=hover_hit)
        draw_button(stay_button, "Stay", enabled=False, hovered=False)
    else:
        draw_button(hit_button, "Hit", enabled=buttons_enabled, hovered=hover_hit)
        draw_button(stay_button, "Stay", enabled=buttons_enabled, hovered=hover_stay)
    draw_button(quit_button, "Quit", enabled=True, hovered=hover_quit)
    if game_over:
        draw_button(play_again_button, "Play again", enabled=True, hovered=hover_play_again)

    if hover_hit or hover_stay or hover_quit or hover_play_again or hover_chip:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
    else:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    # Centered bottom instructions on game screen
    if betting:
        instructions = "Set bet with chips or Up/Down, then Deal (Enter/Space)   |   Q: Quit"
    else:
        instructions = "H: Hit   S: Stay   R: Reset   Q: Quit   Mouse: Buttons"
    instruction_surface = info_font.render(instructions, True, (240, 240, 240))
    instruction_rect = instruction_surface.get_rect(center=(640, 690))
    # Draw semi-transparent background
    bg_rect = pygame.Rect(instruction_rect.x - 5, instruction_rect.y - 2, instruction_rect.width + 10, instruction_rect.height + 4)
    pygame.draw.rect(screen, (0, 0, 0, 200), bg_rect, border_radius=5)
    shadow_surface = info_font.render(instructions, True, (0, 0, 0))
    screen.blit(shadow_surface, (instruction_rect.x + 2, instruction_rect.y + 2))
    screen.blit(instruction_surface, instruction_rect)

    pygame.display.flip()
    clock.tick(60)


pygame.quit()