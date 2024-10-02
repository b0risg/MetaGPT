## main.py
import cmd
from game import Game

class Main(cmd.Cmd):
    """Command-line interface for the Blackjack game."""
    intro = "Welcome to Blackjack! Type help or ? to list commands.\n"
    prompt = "(blackjack) "

    def __init__(self):
        super().__init__()
        self.game = Game()

    def do_start(self, arg):
        """Start a new game of Blackjack."""
        self.game.start()
        self.show_hands()
        self.check_game_status()

    def do_hit(self, arg):
        """Take a hit (draw a card)."""
        self.game.hit()
        self.show_hands()
        self.check_game_status()

    def do_stand(self, arg):
        """Stand (end your turn)."""
        self.game.stand()
        self.show_hands()
        self.check_game_status()

    def do_quit(self, arg):
        """Quit the game."""
        print("Thank you for playing!")
        return True

    def show_hands(self):
        """Display the hands of the player and the dealer."""
        player_hand = self.game.get_player_hand()
        dealer_hand = self.game.get_dealer_hand()
        print(f"Player's hand: {self.format_hand(player_hand)} (Score: {self.game.get_player_score()})")
        print(f"Dealer's hand: {self.format_hand(dealer_hand)} (Score: {self.game.get_dealer_score()})")

    def check_game_status(self):
        """Check the status of the game and determine if there's a winner."""
        result = self.game.check_winner()
        if result:
            print(result)
            return True
        return False

    def format_hand(self, hand):
        """Format the hand for display."""
        return ', '.join(f"{card.rank} of {card.suit}" for card in hand)

    def do_help(self, arg):
        """Show help information."""
        print("Commands:")
        print("  start - Start a new game")
        print("  hit   - Take a hit (draw a card)")
        print("  stand - Stand (end your turn)")
        print("  quit  - Quit the game")
        print("  help  - Show this help message")

if __name__ == '__main__':
    Main().cmdloop()
