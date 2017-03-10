import random


class Card:
    """ Represents a card using a suit and a rank
    suits are Clubs, Diamonds, Hearts, Spades represented by 0, 1, 2, 3
    the ranks are 1 to 13 for Ace, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, Jack, Queen, King"""

    def __init__(self, rank=2, suit=1):
        self.rank = rank
        self.suit = suit

    suit_names = ['Clubs', 'Diamonds', 'Hearts', 'Spades']
    rank_names = [None, 'Ace', '1', '2', '3', '4', '5', '6',
                  '7', '8', '9', '10', 'Jack', 'Queen', 'King']

    def __str__(self):
        return '%s of %s' % (Card.rank_names[self.rank],
                             Card.suit_names[self.suit])

    def __lt__(self, other):
        return (self.suit, self.rank) < (other.suit, other.rank)


class Deck:
    """ Representing a deck of cards, containing one of each card """

    def __init__(self):
        self.new_deck()

    def new_deck(self):
        self.cards = []
        for suit in range(4):
            for rank in range(1, 14):
                card = Card(rank, suit)
                self.cards.append(card)

    def __str__(self):
        res = []
        for card in self.cards:
            res.append(str(card))
        return '\n'.join(res)

    def pop_card(self):
        return self.cards.pop()

    def add_card(self, card):
        self.cards.append(card)

    def shuffle(self):
        random.shuffle(self.cards)

    def sort(self):
        self.cards.sort()


deck = Deck()
deck.shuffle()
deck.sort()
print(deck)
