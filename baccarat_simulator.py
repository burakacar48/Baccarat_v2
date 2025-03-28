"""
Enhanced Baccarat Simulator for the bbaccarat application.
This module simulates a realistic baccarat game with proper shoe, burn card, and cut card rules.
"""
import random
from typing import List, Dict, Tuple, Optional, Union

class Card:
    """Represents a playing card in the baccarat game."""
    
    def __init__(self, rank: str, suit: str):
        """
        Args:
            rank (str): Card rank ('A', '2', '3', ..., 'T', 'J', 'Q', 'K')
            suit (str): Card suit ('H', 'D', 'C', 'S')
        """
        self.rank = rank
        self.suit = suit
        
        # Card values in baccarat
        if rank == 'A':
            self.value = 1
        elif rank in '23456789':
            self.value = int(rank)
        else:  # 10, J, Q, K
            self.value = 0
    
    def __str__(self) -> str:
        return f"{self.rank}{self.suit}"

class BaccaratShoe:
    """Represents a baccarat shoe containing multiple decks of cards."""
    
    def __init__(self, num_decks: int = 8):
        """
        Args:
            num_decks (int): Number of decks in the shoe
        """
        self.num_decks = num_decks
        self.cards = []
        self.cut_card_position = 0
        self.is_new_shoe = True
        self.prepare_shoe()
    
    def prepare_shoe(self):
        """Create and shuffle a new shoe of cards."""
        # Create cards for each deck
        suits = ['H', 'D', 'C', 'S']  # Hearts, Diamonds, Clubs, Spades
        ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K']
        
        self.cards = []
        for _ in range(self.num_decks):
            for suit in suits:
                for rank in ranks:
                    self.cards.append(Card(rank, suit))
        
        # Shuffle using Fisher-Yates algorithm
        self.shuffle()
        
        # Place cut card between the 400th and 401st card
        self.cut_card_position = 400
        
        # Apply burn card rules
        self.burn_cards()
        
        # Set new shoe flag
        self.is_new_shoe = True
    
    def shuffle(self):
        """Shuffle the cards using Fisher-Yates algorithm."""
        for i in range(len(self.cards) - 1, 0, -1):
            j = random.randint(0, i)
            self.cards[i], self.cards[j] = self.cards[j], self.cards[i]
    
    def burn_cards(self):
        """Apply burn card rules for baccarat."""
        if not self.cards:
            return
        
        # Reveal first card
        first_card = self.cards.pop(0)
        print(f"New shoe: First card revealed: {first_card}")
        
        # Determine how many cards to burn
        if first_card.value == 0:  # 10, J, Q, K
            burn_count = 10
        elif first_card.rank == 'A':
            burn_count = 1
        else:
            burn_count = first_card.value  # 2-9
        
        print(f"Burning {burn_count} cards")
        
        # Burn the appropriate number of cards
        for _ in range(min(burn_count, len(self.cards))):
            self.cards.pop(0)
    
    def draw_card(self) -> Optional[Card]:
        """Draw a card from the shoe.
        
        Returns:
            Card or None: The drawn card or None if the shoe is empty
        """
        # Reset new shoe flag if it was set
        if self.is_new_shoe:
            self.is_new_shoe = False
            
        if not self.cards:
            return None
        return self.cards.pop(0)
    
    def cards_remaining(self) -> int:
        """Get the number of cards remaining in the shoe.
        
        Returns:
            int: Number of cards remaining
        """
        return len(self.cards)
    
    def cut_card_reached(self, index: int) -> bool:
        """Check if the specified card index has reached or passed the cut card.
        
        Args:
            index (int): Current card index in the shoe
            
        Returns:
            bool: True if the cut card has been reached
        """
        return index >= self.cut_card_position

class BaccaratHand:
    """Represents a baccarat hand (player or banker)."""
    
    def __init__(self):
        self.cards = []
    
    def add_card(self, card: Card):
        """Add a card to the hand.
        
        Args:
            card (Card): The card to add
        """
        self.cards.append(card)
    
    def value(self) -> int:
        """Calculate the value of the hand in baccarat.
        
        Returns:
            int: The value (0-9) of the hand
        """
        total = sum(card.value for card in self.cards)
        return total % 10
    
    def __str__(self) -> str:
        return " ".join(str(card) for card in self.cards)

class BaccaratGame:
    """Manages a baccarat game with proper rules."""
    
    def __init__(self, num_decks: int = 8):
        """
        Args:
            num_decks (int): Number of decks to use in the shoe
        """
        self.shoe = BaccaratShoe(num_decks)
        self.card_index = 0
        self.cut_card_reached = False
        self.finish_current_round = False
        self.round_started = False
        self.new_shoe_detected = False
    
    def play_hand(self) -> str:
        """Play a single hand of baccarat.
        
        Returns:
            str: 'P' for Player win, 'B' for Banker win, 'T' for tie
        """
        # Reset new shoe detected flag
        self.new_shoe_detected = False
        
        # Check if we need a new shoe
        if len(self.shoe.cards) < 6 or (self.cut_card_reached and not self.finish_current_round):
            self.shoe = BaccaratShoe(self.shoe.num_decks)
            self.card_index = 0
            self.cut_card_reached = False
            self.finish_current_round = False
            self.new_shoe_detected = True
            print("\n--- NEW SHOE STARTED ---\n")
        
        # Start a new round
        self.round_started = True
        
        # Check for cut card
        if not self.cut_card_reached and self.shoe.cut_card_reached(self.card_index):
            self.cut_card_reached = True
            print("Cut card reached!")
            if self.round_started:
                # Cut card came out instead of first Player card, play one more full round
                self.finish_current_round = True
                print("Playing one more full round")
            else:
                # Cut card came out mid-hand, finish this hand and play one more
                self.finish_current_round = True
                print("Finishing this hand and playing one more")
        
        # Initialize hands
        player_hand = BaccaratHand()
        banker_hand = BaccaratHand()
        
        # Initial deal: Player, Banker, Player, Banker
        player_hand.add_card(self.shoe.draw_card())
        self.card_index += 1
        banker_hand.add_card(self.shoe.draw_card())
        self.card_index += 1
        player_hand.add_card(self.shoe.draw_card())
        self.card_index += 1
        banker_hand.add_card(self.shoe.draw_card())
        self.card_index += 1
        
        player_value = player_hand.value()
        banker_value = banker_hand.value()
        
        # Check for naturals (8 or 9)
        if player_value >= 8 or banker_value >= 8:
            # Natural - no more cards drawn
            winner = self._determine_winner(player_value, banker_value)
            self.round_started = False
            
            # If we're finishing the round after cut card and this was the last hand
            if self.cut_card_reached and self.finish_current_round:
                self.finish_current_round = False
            
            return winner
        
        # Third card rules
        player_third_card = None
        
        # Player draws on 0-5, stands on 6-7
        if player_value <= 5:
            third_card = self.shoe.draw_card()
            self.card_index += 1
            if third_card:
                player_hand.add_card(third_card)
                player_third_card = third_card
        
        # Banker's turn
        banker_draws = False
        if player_third_card is None:
            # If player didn't draw, banker draws on 0-5, stands on 6-7
            banker_draws = banker_value <= 5
        else:
            # If player drew a third card, banker's action depends on banker's hand and player's third card
            if banker_value <= 2:
                banker_draws = True
            elif banker_value == 3:
                banker_draws = player_third_card.value != 8
            elif banker_value == 4:
                banker_draws = player_third_card.value in [2, 3, 4, 5, 6, 7]
            elif banker_value == 5:
                banker_draws = player_third_card.value in [4, 5, 6, 7]
            elif banker_value == 6:
                banker_draws = player_third_card.value in [6, 7]
            # Banker always stands on 7
        
        if banker_draws:
            third_card = self.shoe.draw_card()
            self.card_index += 1
            if third_card:
                banker_hand.add_card(third_card)
        
        # Determine winner
        final_player_value = player_hand.value()
        final_banker_value = banker_hand.value()
        winner = self._determine_winner(final_player_value, final_banker_value)
        
        self.round_started = False
        
        # If we're finishing the round after cut card and this was the last hand
        if self.cut_card_reached and self.finish_current_round:
            self.finish_current_round = False
        
        return winner
    
    def _determine_winner(self, player_value: int, banker_value: int) -> str:
        """Determine the winner of a hand.
        
        Args:
            player_value (int): Player's hand value
            banker_value (int): Banker's hand value
            
        Returns:
            str: 'P' for Player win, 'B' for Banker win, 'T' for tie
        """
        if player_value > banker_value:
            return 'P'  # Player wins
        elif banker_value > player_value:
            return 'B'  # Banker wins
        else:
            return 'T'  # Tie
    
    def is_new_shoe(self) -> bool:
        """Check if a new shoe has been started.
        
        Returns:
            bool: True if a new shoe has been started
        """
        return self.new_shoe_detected
    
    def simulate_and_return_winner(self) -> str:
        """Play a hand and return only 'P' or 'B' (retrying on ties).
        
        Returns:
            str: 'P' for Player win, 'B' for Banker win
        """
        while True:
            result = self.play_hand()
            if result != 'T':  # Ignore ties for bbaccarat
                return result

# Singleton baccarat game instance
_baccarat_game = None

def get_baccarat_game() -> BaccaratGame:
    """Get or create the singleton baccarat game instance.
    
    Returns:
        BaccaratGame: The game instance
    """
    global _baccarat_game
    if _baccarat_game is None:
        _baccarat_game = BaccaratGame()
    return _baccarat_game

def get_next_result() -> str:
    """Get the next baccarat result (P or B) for the bbaccarat application.
    
    Returns:
        str: 'P' for Player win, 'B' for Banker win
    """
    game = get_baccarat_game()
    result = game.simulate_and_return_winner()
    
    # Expose new shoe information to the application
    setattr(game, 'new_shoe_detected', game.is_new_shoe())
    
    return result

# Check if a new shoe has been detected
def is_new_shoe_detected() -> bool:
    """Check if a new shoe has been detected in the last hand.
    
    Returns:
        bool: True if a new shoe has been detected
    """
    game = get_baccarat_game()
    return getattr(game, 'new_shoe_detected', False)