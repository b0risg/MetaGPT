## game.py
import random
from typing import List

class Card:
    """Represents a single playing card."""
    def __init__(self, rank: str, suit: str):
        self.rank = rank
        self.suit = suit

    def get_value(self) -> int:
        """Returns the value of the card for blackjack."""
        if self.rank in ['J', 'Q', 'K']:
            return 10
        elif self.rank == 'A':
            return 11  # Ace can be 1 or 11, handled in Player/Dealer class
        else:
            return int(self.rank)

class Deck:
    """Represents a deck of playing cards."""
    def __init__(self):
        self.cards = [Card(rank, suit) for rank in ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
                      for suit in ['Hearts', 'Diamonds', 'Clubs', 'Spades']]
        self.shuffle()

    def shuffle(self) -> None:
        """Shuffles the deck of cards."""
        random.shuffle(self.cards)

    def deal_card(self) -> Card:
        """Deals a card from the deck."""
        return self.cards.pop()

class Player:
    """Represents a player in the game."""
    def __init__(self):
        self.hand: List[Card] = []

    def add_card(self, card: Card) -> None:
        """Adds a card to the player's hand."""
        self.hand.append(card)

    def get_hand(self) -> List[Card]:
        """Returns the player's hand."""
        return self.hand

    def get_score(self) -> int:
        """Calculates and returns the player's score."""
        score = 0
        num_aces = 0
        for card in self.hand:
            score += card.get_value()
            if card.rank == 'A':
                num_aces += 1
        while score > 21 and num_aces:
            score -= 10
            num_aces -= 1
        return score

class Dealer(Player):
    """Represents the dealer in the game."""
    def __init__(self):
        super().__init__()

class Game:
    """Handles the game logic."""
    def __init__(self):
        self.deck = Deck()
        self.player = Player()
        self.dealer = Dealer()

    def start(self) -> None:
        """Starts a new game."""
        self.deck = Deck()
        self.player = Player()
        self.dealer = Dealer()
        self.player.add_card(self.deck.deal_card())
        self.player.add_card(self.deck.deal_card())
        self.dealer.add_card(self.deck.deal_card())
        self.dealer.add_card(self.deck.deal_card())

    def hit(self) -> None:
        """Player takes a hit."""
        self.player.add_card(self.deck.deal_card())

    def stand(self) -> None:
        """Player stands, dealer plays."""
        while self.dealer.get_score() < 17:
            self.dealer.add_card(self.deck.deal_card())

    def get_player_hand(self) -> List[Card]:
        """Returns the player's hand."""
        return self.player.get_hand()

    def get_dealer_hand(self) -> List[Card]:
        """Returns the dealer's hand."""
        return self.dealer.get_hand()

    def get_player_score(self) -> int:
        """Returns the player's score."""
        return self.player.get_score()

    def get_dealer_score(self) -> int:
        """Returns the dealer's score."""
        return self.dealer.get_score()

    def check_winner(self) -> str:
        """Determines the winner of the game."""
        player_score = self.get_player_score()
        dealer_score = self.get_dealer_score()
        if player_score > 21:
            return "Dealer wins!"
        elif dealer_score > 21 or player_score > dealer_score:
            return "Player wins!"
        elif player_score < dealer_score:
            return "Dealer wins!"
        else:
            return "It's a tie!"
